from load_unit import LoadUnit, loadReservationStationEntry
from store_unit import StoreUnit, storeReservationStationEntry

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
    
    def connectMemory(self, mem):
        self.mem = mem
    
    def check(self):
        """Check if the Memory is connected"""
        if (self.mem is None):
            raise Exception("Memory not connected to LoadStoreUnit")

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
        
        # Step 2
        if (self.mem.canStartTransaction()):
            txn = self.getStartableTransactions()
            if (txn is not None):
                self.mem.startTransaction(txn)
        
        # Step 3,4,5
        self.load_unit.step()
        self.store_unit.step()
        self.mem.step()

        # Step 6
        self.storeToLoadForwarding()

        
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
            if (entry["status"] != "clear"):
                if (entry["entry"].address == txn.address):
                    return True
        
        return False

    def getStartableTransactions(self):
        """Get the startable transactions from either Load or Store Unit.
        Load unit is given priority over the Store Unit."""

        txn = None

        # Check the Load Unit
        if (self.load_unit.hasReadyAddress()):
            txn = self.load_unit.getReadyMemoryTransaction()
            print("Load Unit has ready memory transaction")
            # Check for speculative load hazard
            if (self.speculativeLoadHazardCheck(txn)):
                print("Speculative Load Hazard Detected")
                txn = None

        # if no load transaction can be issued, then check the store unit
        if (txn is None and self.store_unit.hasReadyAddress()):
            print("Store Unit has ready memory transaction")
            txn = self.store_unit.getReadyMemoryTransaction()

        return txn