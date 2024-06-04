from rs import ReservationStationEntry
from rf import RF
from cdb import CommonDataBus
from commit_unit import CommitUnit
from mem_unit import MemoryUnit
from queue import Queue
from rs_pick_policy import ReservationStationPickPolicy
from print import convertToHex

import instr

class storeReservationStationEntry(ReservationStationEntry):
    """Resembles the Reservation Station Entry of a generic Arithmetic Unit of LEN5 processor."""
    def __init__(self) -> None:
        super().__init__()
        self.rs1_idx    = None
        self.rs1_value  = None
        self.rs2_idx    = None
        self.rs2_value  = None
        self.offset     = None
        self.address    = None
        self.rd_idx     = -1


    def __str__(self):
        return f"storeReservationStationEntry(pc={convertToHex(self.pc)}, instr={self.instr}, ready={self.isReady()}, res_value={self.res_value}, rs1_idx={self.rs1_idx}, rs1_value={self.rs1_value}, rs2_idx={self.rs2_idx}, rs2_value={self.rs2_value}, offset={self.offset}, address={convertToHex(self.address)})"
    
    def __repr__(self):
        return self.__str__()

    def convertToEntry(instr : instr.Instruction):
        # Create the entry object
        print(f"Converting {instr} to store entry with rob_idx {instr.rob_idx}")
        entry = storeReservationStationEntry()
        entry.setInstr(instr.mnemo)
        entry.setPC(instr.address)
        entry.setROBIdx(instr.rob_idx)
        # Set common operands in R/I instr
        entry.rs1_idx = instr.fields().rs1
        entry.rs2_idx = instr.fields().rs2
        entry.offset = instr.fields().imm

        return entry

    def isReady(self):
        return self.rs1_value is not None and self.rs2_value is not None
    
    def hasReadyAddress(self):
        return self.address is not None

    def forwardOperands(self, rf: RF, commit_unit: CommitUnit, cdb : CommonDataBus):
        """Search in the Commit Unit first"""
        #todo split it into smaller functions
        #todo think of implementing all this searchin into the base exec unit class

        # print(commit_unit.commit_queue.queue)
        # Search for rs1
        entry, rob_idx = commit_unit.searchOperand(self.rs1_idx, self.pc)
        # print(entry)

        cdb_last_result = cdb.getLastResult()
        # print(f"CDB last result: {cdb_last_result}")

        if (entry is not None):
            if (entry.res_ready):
                # print(f"Forwarding rs1 value {entry.res_value} to {self}")
                self.rs1_value = entry.res_value
            elif (rob_idx is not None):
                self.rs1_idx = rob_idx
        elif (cdb_last_result is not None and cdb_last_result["rd_idx"] == self.rs1_idx):
            # print(f"Forwarding CDB value {cdb_last_result['res_value']} to {self}")
            self.rs1_value = cdb_last_result["res_value"]
        else:
            # No in-flight instruction is computing the value, so get it from RF
            # print(f"Fetching rs1 value {rf[self.rs1_idx]} from RF {self}")
            self.rs1_value = rf[self.rs1_idx]

        entry, rob_idx = commit_unit.searchOperand(self.rs2_idx, self.pc)
        # print(entry)

        if (entry is not None):
            if (entry.res_ready):
                # print(f"Forwarding rs2 value {entry.res_value} to {self}")
                self.rs2_value = entry.res_value
            elif (rob_idx is not None):
                self.rs2_idx = rob_idx
        elif (cdb_last_result is not None and cdb_last_result["rd_idx"] == self.rs2_idx):
            # print(f"Forwarding CDB value {cdb_last_result['res_value']} to {self}")
            self.rs2_value = cdb_last_result["res_value"]
        else:
            # No in-flight instruction is computing the value, so get it from RF
            # print(f"Fetching rs2 value {rf[self.rs2_idx]} from RF {self}")
            self.rs2_value = rf[self.rs2_idx]

    def updateFromCDB(self, rob_idx, value):
        """Update the entry with the value from the CDB."""
        if (rob_idx == self.rs1_idx):
            self.rs1_value = value
        if (rob_idx == self.rs2_idx):
            self.rs2_value = value

class StoreUnit(MemoryUnit):
    """Load Unit class, inherits from Memory Unit."""
    def __init__(self, n_entries: int) -> None:
        super().__init__(n_entries, storeReservationStationEntry, latency=1, iterative=True)

    def updateAddress(self, resultFromMemUnit : dict):
        """Receive a dictionary with:
            {
                "res_value": res_value,
                "rd_idx": rd_idx,
                "rob_idx": entry["entry"].getROBIdx(),
                "valid" : True
            }
        """
        for e in self.rs.entries:
            if (e["entry"].getROBIdx() == resultFromMemUnit["rob_idx"] and e["status"] == "executing"):
                print(f"Updating address for {e['entry']} with {resultFromMemUnit['res_value']}")
                # Update the address
                e["entry"].address = resultFromMemUnit["res_value"]
                e["status"] = "address_ready"

    
    def step(self):
        """ Actions to perform:
        1. Check if the memory unit has the address ready.
        2. Step the inner memory unit which will compute the address.
        """

        # Step 1
        if (super().hasResult()):
            # Update the reservation station with the address
            self.updateAddress(self.pipeline.popLastInstruction())

        # Step 2
        super().step()
    

#-------------------------------------------------------------------------------
# Interface with the CDB
#-------------------------------------------------------------------------------
    def hasResult(self):
        """Store unit always commits.
        Unless it triggers memory access results, but this is not
        implemented because the input data comes from Spike. 
        """
        return self.rs.hasResultDone()
        
    
    def getResult(self):
        """Store unit never writes on CDB"""
        entry = self.rs.getEntryDone()

        print(f"{__class__.__name__} {entry}")

        if (entry is None):
            return None

        return {
            "res_value" : 0,
            "rd_idx"    : entry["entry"].rd_idx,
            "rob_idx"   : entry["entry"].getROBIdx(),
            "valid"     : True
        }

#-------------------------------------------------------------------------------
# Interface with the Memory 
#-------------------------------------------------------------------------------
    def hasReadyAddress(self):
        """Returns true if there is an entry with a ready address"""
        for entry in self.rs.entries:
            if (entry["status"] == "address_ready"):
                return True
        
        return False

    def getEntryWithAddressReady(self):
        return ReservationStationPickPolicy.pickOldestReady(self.rs, status="address_ready", next_status="executing")
    
    def getReadyMemoryTransaction(self) -> storeReservationStationEntry:
        """Returns a ready read transaction to be sent to the memory unit"""

        if (not self.hasReadyAddress()):
            return None

        entry = self.getEntryWithAddressReady()

        transaction = entry["entry"]

        transaction.value = transaction.rs2_value

        # Update the entry status
        entry["status"] = "done"

        return transaction

    def updateResult(self, resultFromMemory : storeReservationStationEntry):
        """Update the rd_value with a transaction from Memory"""
        self.rs.updateResult(resultFromMemory.getROBIdx(), resultFromMemory.getResult())