from exec_unit import ExecUnit
from rs import ReservationStationEntry

import instr, isa


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

class ArithUnit(ExecUnit):
    """
    Arithmetic Unit class, can be used to create different types of execution units
    performing arithmetic operations.
    """
    def __init__(self, n_entries : int , reservation_station_t : type[arithReservationStationEntry], latency : int = 1, iterative : bool = True ) -> None:
        super().__init__(n_entries, reservation_station_t, latency, iterative)

    def execute(self, entry : ReservationStationEntry):
        """Implement the execution of the instruction.
        You are given with an entry from the reservation station
        and must perform operation with it. 
        """
        raise Exception("Not implemented yet.")