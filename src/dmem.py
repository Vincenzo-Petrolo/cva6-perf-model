import random   # Used for choosing wether it is a cache hit or miss
from load_unit import loadReservationStationEntry
from store_unit import storeReservationStationEntry

class DataMemory(object):
    """Data Memory of LEN5 processor."""
    def __init__(self, cache_latency : int = 1, cache_hit_rate : float = 0.9, mem_latency : int = 2) -> None:

        # Memory is an on-demand dictionary
        self.mem = {}

        # Cache latency
        self.cache_latency = cache_latency

        # Cache hit rate
        self.cache_hit_rate = cache_hit_rate

        # Memory latency
        self.mem_latency = mem_latency

        # Curr transaction counter
        """It is used to keep track of when the current transaction will be done.
        It is a downcounter, when it reaches 0, the transaction is done."""
        self.txn_counter = 0

        # Current transaction
        """It stores a dictionary with the latest transaction."""
        self.curr_txn = None
    
    def step(self):
        """Advance the transaction counter."""

        if (self.txn_counter is None or self.txn_counter == 0):
            return

        if (self.txn_counter is not None):
            self.txn_counter = max(0, self.txn_counter - 1)
        
        if (self.txn_counter == 0):
            # Perform the operation of the transaction
            if (type(self.curr_txn) == loadReservationStationEntry):
                self.curr_txn.setResult(self.read(self.curr_txn.address))
            elif (type(self.curr_txn) == storeReservationStationEntry):
                self.write(self.curr_txn.address, self.curr_txn.value)
            else:
                raise Exception("Invalid transaction type")

        
    def hasReadyTransaction(self) -> bool:
        """Returns True if there is a ready transaction for Load unit."""

        if (self.txn_counter is None):
            return False

        return self.txn_counter == 0
    
    def getReadyTransaction(self) -> dict | None:
        """Returns the ready transaction, only for the Load unit."""

        if (not self.hasReadyTransaction()):
            return None
        
        txn = self.curr_txn

        # Clear the transaction
        self.clearTransaction()

        return txn
    
    def clearTransaction(self):
        """Clear the current transaction."""
        self.curr_txn = None
        self.txn_counter = None
    
    def canStartTransaction(self) -> bool:
        """Returns True if a transaction can be started."""
        return self.txn_counter is None

    def startTransaction(self, txn : loadReservationStationEntry | storeReservationStationEntry):
        """Start a transaction."""
        self.curr_txn = txn
        # If the random number between 0 and 1 is less than the cache hit rate, then we have a hit, else a miss
        self.txn_counter = self.cache_latency if (random.random() < self.cache_hit_rate) else self.mem_latency

    
    def read(self, addr : int) -> int:
        """Read from the memory."""
        if (addr in self.mem):
            return self.mem[addr]
        else:
            return 0
    
    def write(self, addr : int, value : int):
        """Write to the memory."""
        self.mem[addr] = value