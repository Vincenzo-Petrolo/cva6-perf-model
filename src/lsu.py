from load_unit import LoadUnit, loadReservationStationEntry
from store_unit import StoreUnit, storeReservationStationEntry
from print import convertToHex
from rob import ROBEntry

class LoadStoreUnit(object):
    """Resembles the Load Store Unit of LEN5 processor."""
    #todo miss support for LB, LH, LD, SB, SH, SD, do I really need this?

    def __init__(self) -> None:

        # Create the Load Unit
        self.load_unit = LoadUnit(n_entries=8)

        # Create the Store Unit
        self.store_unit = StoreUnit(n_entries=8)

        # Memory
        self.mem = None

        # Commit interface
        self.commit_unit = None
    
    def connectMemory(self, mem):
        self.mem = mem
    
    def connectCommitUnit(self, commit_unit):
        self.commit_unit = commit_unit
    
    def check(self):
        """Check if the Memory is connected"""
        if (self.mem is None):
            raise Exception("Memory not connected to LoadStoreUnit")
        
        if (self.commit_unit is None):
            raise Exception("Commit Unit not connected to LoadStoreUnit")

    def step(self):
        """Steps to perform:
        1. Check the memory for completed transactions.
        2. Check for new startable transactions.
        3. Step the Load Unit.
        4. Step the Store Unit.
        5. Step the memory.
        6. Store-to-Load Forwarding.
        """
        # Step 1
        if (self.mem.hasReadyTransaction()):
            txn = self.mem.getReadyTransaction()
            if (type(txn) == loadReservationStationEntry):
                self.load_unit.updateResult(txn)
                print(f"Updated load txn: {txn} with ROBidx: {txn.getROBIdx()}")
        # Step 2
        elif (self.mem.canStartTransaction()):
            txn = self.getStartableTransactions()
            if (txn is not None):
                print(f"Starting transaction")
                print(f"Picked txn: {txn} with ROBIdx: {txn.getROBIdx()}")
                self.mem.startTransaction(txn)
        
        # Step 3,4,5
        self.load_unit.step()
        self.store_unit.step()
        self.mem.step()

        # Step 6
        # todo check and implement this
        # self.storeToLoadForwarding()

        
#-------------------------------------------------------------------------------
# Interface with the CDB
#-------------------------------------------------------------------------------
    def hasResult(self):
        """Returns true if it has a ready result from the Load Unit"""
        #todo think if we need to check the store unit as well
        return self.load_unit.hasResult()   
    
    def getResult(self):
        """Returns result from the reservation station of the Load Unit"""
        return self.load_unit.getResult()

#-------------------------------------------------------------------------------
# Store-to-Load Forwarding
#-------------------------------------------------------------------------------
    def storeToLoadForwarding(self):
        """Forward the store results to the load unit."""
        #todo, check if this works

        for s_entry in self.store_unit.rs.entries:
            if (s_entry["status"] == "done"):
                for l_entry in self.load_unit.rs.entries:
                    if (l_entry["status"] == "waiting_operands"):
                        if (l_entry["entry"].address == s_entry["entry"].address):
                            l_entry["entry"].res_value = s_entry["entry"].res_value

                            # Flag the load entry as ready
                            l_entry["status"] = "ready"

#-------------------------------------------------------------------------------
# Speculative Load hazard check
#-------------------------------------------------------------------------------
    def speculativeLoadHazardCheck(self, txn):
        """Check if there is a speculative load hazard."""

        for entry in self.store_unit.rs.entries:
            if (entry["status"] not in ["clear", "done"]):
                if (entry["entry"].address == txn.address or entry["entry"].address is None):
                    return True
        
        return False

    def getStartableTransactions(self):
        """Get the startable transactions from either Load or Store Unit.
        Load unit is given priority over the Store Unit."""

        txn = None

        # Check the head of the ROB if there is a load or store instruction
        # if there is, allow the memory transaction
        rob = self.commit_unit.rob

        # Pick the oldest address_ready txn from the load unit
        txn = LoadStoreUnit.pickOldest(self.load_unit.rs, rob_idx=rob.head)

        txn = self.validateTransaction(txn)

        if (txn is not None):
            return txn

        txn = LoadStoreUnit.pickOldest(self.store_unit.rs, rob_idx=rob.head)

        txn = self.validateTransaction(txn)
        
        if (txn is not None):
            return txn
        
        return None
    
        
    def pickOldest(rs, rob_idx : int):
        """Pick the next entry ready for execution from the RS.
        Pick the oldest entry that is ready for execution.
        """

        for entry in rs.entries:
            if (entry["status"] == "address_ready" and entry["entry"].getROBIdx() == rob_idx):
                return entry
        
        return None

    
    def validateTransaction(self, txn):
        """Validate the transaction before starting it."""
        if (txn is not None):
            match txn["status"]:
                case "address_ready":
                    # The txn is ready to be issued, set its status to executing
                    if (type(txn["entry"]) == loadReservationStationEntry):
                        txn["status"] = "executing"
                    else:
                        txn["status"] = "done"
                    return txn["entry"]
                case "waiting_operands":
                    # The load is waiting for the operands to be ready
                    # I think this will never happen, because if it is at ROB head
                    # then all the other instructions have committed and it can't 
                    # be updated anymore, so raise an exception here
                    print(txn)
                    print(self.load_unit.rs)
                    raise Exception("TXN is waiting for operands, this should not happen")
                case _:
                    return None