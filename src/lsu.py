from load_unit import LoadUnit

class LoadStoreUnit(object):
    """Resembles the Load Store Unit of LEN5 processor."""
    def __init__(self) -> None:

        # Create the Load Unit
        self.load_unit = LoadUnit(n_entries=8)

        # Create the Store Unit
        # self.store_unit 

        # Memory
        self.mem = None
    
    def connectMemory(self, mem):
        self.mem = mem
    
    def check(self):
        """Check if the Memory is connected"""
        if (self.mem is None):
            raise Exception("Memory not connected to LoadStoreUnit")

    def step(self):
        raise NotImplementedError
        
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
    raise NotImplementedError

#-------------------------------------------------------------------------------
# Speculative Load hazard check
#-------------------------------------------------------------------------------
def speculativeLoadHazardCheck(self):
    """Check if there is a speculative load hazard."""
    raise NotImplementedError