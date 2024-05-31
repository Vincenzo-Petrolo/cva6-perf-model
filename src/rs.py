from abc import ABC, abstractmethod
from instr import Instruction
from rf import RF
from commit_unit import CommitUnit

class ReservationStationEntry(object):
    """Resembles the Reservation Station Entry of a generic Unit of LEN5 processor."""
    def __init__(self) -> None:
        self.pc         = None
        self.instr      = None
        self.res_value  = None
        self.rob_idx    = None
    
    def __str__(self):
        return f"ReservationStationEntry(pc={self.pc}, instr={self.instr}, res_value={self.res_value})"
    
    def __repr__(self):
        return self.__str__()
    
    def getResult(self):
        return self.res_value
    
    def setResult(self, value):
        self.res_value = value
    
    def setInstr(self, instr):
        self.instr = instr
    
    def getInstr(self):
        return self.instr
    
    def setPC(self, pc):
        self.pc = pc
    
    def getPC(self):
        return self.pc
    
    def setROBIdx(self, idx):
        self.rob_idx = idx

    def getROBIdx(self):
        return self.rob_idx
    
    @abstractmethod
    def convertToEntry(instr : Instruction):
        """Implement me and return an entry of the type of the Reservation Station Entry."""
        pass

    @abstractmethod
    def reset(self):
        """Reset the entry by clearing everything."""
        pass

    @abstractmethod
    def isReady(self):
        """Check if the entry is ready to be executed.
        This is done by checking if the operands are not None.
        """
        pass

    @abstractmethod
    def fillOperands(self, rf : RF, commit_unit : CommitUnit):
        """Fill the operands of the entry by forwarding from RF or from ROB."""
        """You must implement this, remember to always look for the value in the ROB first."""
        """Then fetch from the RF"""
        pass


class ReservationStation(ABC):
    """Generic Reservation Station of LEN5 processor."""
    """Possible values status of each entry:
    - clear: the entry is empty
    - waiting_operands: the entry is waiting for the operands
    - ready: the entry is ready to be executed
    - executing: the entry is executing
    - done: the entry is done, waiting to be committed
    """

    def __init__(self, n_entries : int, entry_t : type[ReservationStationEntry]) -> None:
        super().__init__()
        self.n_entries = n_entries

        # Store the type
        self.entry_t = entry_t

        # List of entries
        self.entries = [{"entry": entry_t(), "status" : "clear"} for _ in range(n_entries)]

    def __str__(self):
        return f"ReservationStation(n_entries={self.n_entries}, entries={self.entries})"
    
    def __repr__(self):
        return self.__str__()
    
    def issue(self, entry : ReservationStationEntry) -> bool:
        """Issue an entry to the Reservation Station.
        If there is an empty entry, the instruction is converted to an entry,
        and the entry is stored in the Reservation Station.

        Returns True if the instruction was issued, False otherwise. 
        """
        for e in self.entries:
            if e["status"] == "clear":
                e["entry"] = entry
                # Check if the entry is ready to be executed
                if e["entry"].isReady():
                    e["status"] = "ready"
                else:
                    e["status"] = "waiting_operands"
                return True
        return False
    
    def getEntry(self, idx):
        """Get the entry at the index."""
        return self.entries[idx]["entry"]
    
    def clearEntry(self, idx):
        """Clear the entry at the index."""
        self.entries[idx]["status"] = "clear" 
        self.entries[idx]["entry"].reset()

    def updateFromCDB(self, rob_idx, value):
        """When the CDB broadcasts a new computed value, the Reservation Station
        must update the entries that are waiting for that value."""
        for e in self.entries:
            if e["entry"].rs1_idx == rob_idx:
                e["entry"].rs1_value = value
            if e["entry"].rs2_idx == rob_idx:
                e["entry"].rs2_value = value
            
            # Check if this entry is ready
            if e["entry"].isReady():
                e["status"] = "ready"
    
    def getEntryReadyForExecution(self):
        """Get the entry that is ready for execution."""
        for e in self.entries:
            if e["status"] == "ready":
                e["status"] = "executing"
                return e
        return None
    
    def updateResult(self, e : type[ReservationStationEntry], res_value):
        """Update the result of the instruction in the Reservation Station
        this is obtained after the execution of the entry."""
        for e in self.entries:
            if e["entry"].rd_idx == e.getROBIdx():
                e["entry"].setResult(res_value)
                e["status"] = "done"
    
    