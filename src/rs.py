from abc import ABC, abstractmethod
from instr import Instruction
from rf import RF
from commit_unit import CommitUnit
from rs_pick_policy import ReservationStationPickPolicy

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
    def forwardOperands(self, rf : RF, commit_unit : CommitUnit):
        """Fill the operands of the entry by forwarding from RF or from ROB."""
        """You must implement this, remember to always look for the value in the ROB first."""
        """Then fetch from the RF"""
        pass

    @abstractmethod
    def updateFromCDB(self, rd_idx, value):
        """Update the entry with forwarded values from the Common Data Bus."""
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

    def __init__(self, n_entries : int, entry_t : type[ReservationStationEntry], pick_policy = ReservationStationPickPolicy.pickOldestReady) -> None:
        super().__init__()
        self.n_entries = n_entries

        # Store the type
        self.entry_t = entry_t

        # List of entries
        self.entries = [{"entry": entry_t(), "status" : "clear"} for _ in range(n_entries)]

        # Picking scheduling policy, it is a function
        self.pick = pick_policy

        # Attributes useful for scheduling
        self.oldest_ptr = 0
        self.newest_ptr = 0
    

    def __str__(self):
        string = ""
        for i, e in enumerate(self.entries):
            string += f"{i}: {e}\n"
        return string
    
    def __repr__(self):
        return self.__str__()
    
    def issue(self, entry : ReservationStationEntry) -> bool:
        """Issue an entry to the Reservation Station.
        If there is an empty entry, the instruction is converted to an entry,
        and the entry is stored in the Reservation Station.

        Returns True if the instruction was issued, False otherwise. 
        """
        i = self.newest_ptr

        if self.entries[i]["status"] == "clear":
            self.entries[i]["entry"] = entry

            if entry.isReady():
                self.entries[i]["status"] = "ready"
            else:
                self.entries[i]["status"] = "waiting_operands"

            self.newestPtrUp()
            return True
        return False
        # for e in self.entries:
        #     if e["status"] == "clear":
        #         e["entry"] = entry
        #         # Check if the entry is ready to be executed
        #         if e["entry"].isReady():
        #             e["status"] = "ready"
        #         else:
        #             e["status"] = "waiting_operands"
                
        #         # Increase the newest pointer up
        #         self.newestPtrUp()
        #         return True
        # return False
    
    def oldestPtrUp(self):
        """Move the oldest pointer up."""
        self.oldest_ptr = (self.oldest_ptr + 1) % self.n_entries
    
    def newestPtrUp(self):
        """Move the newest pointer up."""
        self.newest_ptr = (self.newest_ptr + 1) % self.n_entries
    
    def getEntry(self, idx):
        """Get the entry at the index."""
        return self.entries[idx]["entry"]
    
    def clearEntry(self, idx):
        """Clear the entry at the index."""
        for e in self.entries:
            if e["entry"].getROBIdx() == idx:
                e["status"] = "clear"

        # Move the oldest pointer up
        self.oldestPtrUp()

    def updateFromCDB(self, rd_idx, value):
        """When the CDB broadcasts a new computed value, the Reservation Station
        must update the entries that are waiting for that value."""
        for e in self.entries:
            if (e["status"] == "waiting_operands"):
                e["entry"].updateFromCDB(rd_idx, value)
                
                # Check if this entry is ready
                if e["entry"].isReady():
                    e["status"] = "ready"
    
    def getEntryReadyForExecution(self):
        """Get the entry that is ready for execution."""
        return self.pick(self, status="ready", next_status="executing") 
    
    def getEntryDone(self):
        """Return an entry that can be sent to CDB"""
        return self.pick(self, status="done", next_status="clear") 
    
    def hasResultDone(self):
        """Returns true if the reservation station has an entry, flagged as done."""

        for entry in self.entries:
            if (entry["status"] == "done"):
                return True
            
        return False

    def updateResult(self, rob_idx, res_value):
        """Update the result of the instruction in the Reservation Station
        this is obtained after the execution of the entry."""
        found = False
        for i, e in enumerate(self.entries):
            if e["entry"].rob_idx == rob_idx and e["status"] == "executing":
                e["entry"].setResult(res_value)
                e["status"] = "done"
                found = True

                # self.clearEntry(i)
        
        assert found, f"Entry with ROB idx: {rob_idx} and status : executing not found in Reservation Station."