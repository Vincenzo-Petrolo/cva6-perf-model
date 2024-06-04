import random   # Used for choosing wether it is a cache hit or miss
from load_unit import loadReservationStationEntry
from store_unit import storeReservationStationEntry
from print import convertToHex

XLEN=32
BYTE=8

class DataMemory(object):
    """Data Memory of LEN5 processor."""
    def __init__(self, filename : str = None, cache_latency : int = 1, cache_hit_rate : float = 0.9, mem_latency : int = 2) -> None:

        # Memory is an on-demand dictionary
        self.mem = {}

        if (filename is not None):
            self._loadMemoryFromFile(filename)
            print(f"Loaded memory from {filename}")
            print(self)

        # Cache latency
        self.cache_latency = cache_latency

        # Cache hit rate
        self.cache_hit_rate = cache_hit_rate

        # Memory latency
        self.mem_latency = mem_latency

        # Curr transaction counter
        """It is used to keep track of when the current transaction will be done.
        It is a downcounter, when it reaches 0, the transaction is done."""
        self.txn_counter = None

        # Current transaction
        """It stores a dictionary with the latest transaction."""
        self.curr_txn = None
    
    def __str__(self) -> str:
        string = ""
        for addr in self.mem:
            string += f"{convertToHex(addr)}: {self.mem[addr]}\n"
        
        return string

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

    
    def read(self, addr : int, mode : str = 'w') -> int:
        """Read from the memory.
        Default mode is word, but it can be byte (b),
        half-word (h)"""

        if (addr not in self.mem):
            return 0

        match mode:
            case 'b':
                return self.mem[addr]
            case 'h':
                return self.mem[addr+1] + (self.mem[addr] << 8)
            case _:
                read_val = self.mem[addr+3] + (self.mem[addr+2] << 8) + (self.mem[addr+1] << 16) + (self.mem[addr] << 24)
                print(f"Reading from {convertToHex(addr)} value {read_val}")

                return read_val

    
    def write(self, addr : int, value : int, mode : str = 'w'):
        """Write to the memory."""
        match mode:
            case 'b':
                self.mem[addr] = value
            case 'h':
                self.mem[addr] = value & 0xFF
                self.mem[addr+1] = (value >> 8) & 0xFF
            case _:
                print(f"Writing {value} to {convertToHex(addr)}")
                self.mem[addr] = value & 0xFF
                self.mem[addr+1] = (value >> 8) & 0xFF
                self.mem[addr+2] = (value >> 16) & 0xFF
                self.mem[addr+3] = (value >> 24) & 0xFF
    
    def _loadMemoryFromFile(self, filename : str):
        """Load the memory from a file in verilog format obtained
        through objcopy with -O verilog option."""
        with open(filename, "r") as f:
            last_addr = None
            for line in f:
                if (line.startswith("@")):
                    # Exclude the address
                    last_addr = int(line[1:], 16)
                else:
                    splitted = line.split()
                    # print(splitted)
                    for i in range(0, len(splitted), 4):
                        last_addr = self._storeWord(self._flipWord(splitted[i:i+4]), last_addr)

    
    def _flipWord(self, word : list) -> str:
        """Flip the word."""
        return [word[3] , word[2] , word[1] , word[0]]
    
    def _storeWord(self, word : list, addr : int):
        """Store a word in memory."""
        # print(word)
        for i in range(4):
            # print(f"Storing {word[i]} at {convertToHex(addr+i)}")
            self.mem[addr + i] = int(word[i], 16)
        
        return addr+4


