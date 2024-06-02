from rs import ReservationStationEntry
from rf import RF
from cdb import CommonDataBus
from commit_unit import CommitUnit
from mem_unit import MemoryUnit
from queue import Queue

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


    def __str__(self):
        return f"storeReservationStationEntry(pc={self.pc}, instr={self.instr}, ready={self.isReady()}, res_value={self.res_value}, rs1_idx={self.rs1_idx}, rs1_value={self.rs1_value}, rs2_idx={self.rs2_idx}, rs2_value={self.rs2_value}, offset={self.offset}, address={self.address})"
    
    def __repr__(self):
        return self.__str__()

    def convertToEntry(instr : instr.Instruction):
        """Instruction can be of R-type or I-type."""
        # Create the entry object
        entry = storeReservationStationEntry()
        entry.setInstr(instr.mnemo)
        entry.setPC(instr.address)
        entry.setROBIdx(instr.rob_idx)
        # Set common operands in R/I instr
        entry.rs1_idx = instr.fields().rs1
        entry.rs1_idx = instr.fields().rs2
        entry.offset = instr.fields().offset

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
        entry = commit_unit.searchOperand(self.rs1_idx, self.pc)
        # print(entry)

        cdb_last_result = cdb.getLastResult()
        # print(f"CDB last result: {cdb_last_result}")

        if (entry is not None):
            if (entry.res_ready):
                # print(f"Forwarding rs1 value {entry.res_value} to {self}")
                self.rs1_value = entry.res_value
        elif (cdb_last_result is not None and cdb_last_result["rd_idx"] == self.rs1_idx):
            # print(f"Forwarding CDB value {cdb_last_result['res_value']} to {self}")
            self.rs1_value = cdb_last_result["res_value"]
        else:
            # No in-flight instruction is computing the value, so get it from RF
            # print(f"Fetching rs1 value {rf[self.rs1_idx]} from RF {self}")
            self.rs1_value = rf[self.rs1_idx]

        entry = commit_unit.searchOperand(self.rs2_idx, self.pc)
        # print(entry)

        if (entry is not None):
            if (entry.res_ready):
                # print(f"Forwarding rs2 value {entry.res_value} to {self}")
                self.rs2_value = entry.res_value
        elif (cdb_last_result is not None and cdb_last_result["rd_idx"] == self.rs2_idx):
            # print(f"Forwarding CDB value {cdb_last_result['res_value']} to {self}")
            self.rs2_value = cdb_last_result["res_value"]
        else:
            # No in-flight instruction is computing the value, so get it from RF
            # print(f"Fetching rs2 value {rf[self.rs2_idx]} from RF {self}")
            self.rs2_value = rf[self.rs2_idx]

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
            if (e.getROBIdx() == resultFromMemUnit["rob_idx"]):
                # Update the address
                e.address = resultFromMemUnit["res_value"]

    
    def step(self):
        """ Actions to perform:
        1. Check if the memory unit has the address ready.
        2. Step the inner memory unit which will compute the address.
        """

        # Step 1
        if (super().hasResult()):
            # Update the reservation station with the address
            self.updateAddress(super().getResult())

        # Step 2
        super().step()
    

#-------------------------------------------------------------------------------
# Interface with the CDB
#-------------------------------------------------------------------------------
    def hasResult(self):
        """Store unit never writes on CDB."""
        return False
    
    def getResult(self):
        """Store unit never writes on CDB"""
        return None


#-------------------------------------------------------------------------------
# Interface with the Memory 
#-------------------------------------------------------------------------------
    def hasReadyAddress(self):
        """Returns true if there is an entry with a ready address"""
        for entry in self.rs.entries:
            if (entry.hasReadyAddress()):
                return True
        
        return False
    
    def getReadyMemoryTransaction(self) -> dict | None:
        """Returns a ready read transaction to be sent to the memory unit"""

        entry = self.rs.getEntryReadyForExecution()

        if (entry["entry"].address is None):
            return None

        transaction = {
            "entry" : entry
        }

        return transaction

    def updateResult(self, resultFromMemory : storeReservationStationEntry):
        """Update the rd_value with a transaction from Memory"""
        self.rs.updateResult(resultFromMemory.getROBIdx(), resultFromMemory.getResult())