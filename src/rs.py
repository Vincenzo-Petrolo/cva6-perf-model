from abc import ABC, abstractmethod
import instr
import isa

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
    def convertToEntry(instr):
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

class arithReservationStationEntry(ReservationStationEntry):
    """Resembles the Reservation Station Entry of a generic Arithmetic Unit of LEN5 processor."""
    def __init__(self) -> None:
        super().__init__()
        self.rd_idx     = None
        self.rs1_idx    = None
        self.rs1_value  = None
        self.rs2_idx    = None
        self.rs2_value  = None
        self.op         = None
        self.func7      = None
        self.func3      = None
        self.imm        = None


    def __str__(self):
        return f"arithReservationStationEntry(pc={self.pc}, instr={self.instr}, ready={self.ready}, res_value={self.res_value}, rd_idx={self.rd_idx}, rs1_idx={self.rs1_idx}, rs1_value={self.rs1_value}, rs2_idx={self.rs2_idx}, rs2_value={self.rs2_value}, op={self.op})"
    
    def __repr__(self):
        return self.__str__()

    def convertToEntry(pc, instr : instr.Instruction):
        """Instruction can be of R-type or I-type."""
        # Create the entry object
        entry = arithReservationStationEntry()
        entry.setInstr(instr)
        entry.setPC(pc)
        # Set common operands in R/I instr
        entry.rd_idx = instr.rd
        entry.rs1_idx = instr.rs1
        entry.func3 = instr.func3
        entry.op = instr.opcode


        # If instruction is of R-type
        if (instr.getType() is isa.Rtype):
            entry.rs2_idx = instr.rs2
            entry.func7 = instr.func7
        elif (instr.getType() is isa.Itype):
            entry.imm = instr.imm


        return entry


    def reset(self):
        self.pc         = None
        self.instr      = None
        self.res_value  = None
        self.rd_idx     = None
        self.rs1_idx    = None
        self.rs1_value  = None
        self.rs2_idx    = None
        self.rs2_value  = None
        self.op         = None
    
    def isReady(self):
        return self.rs1_value is not None and self.rs2_value is not None



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
    
    def issue(self, instr) -> bool:
        """Issue an entry to the Reservation Station.
        If there is an empty entry, the instruction is converted to an entry,
        and the entry is stored in the Reservation Station.

        Returns True if the instruction was issued, False otherwise. 
        """
        for e in self.entries:
            if e["status"] == "clear":
                e["entry"] = self.entry_t.convertToEntry(instr)
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
    
    