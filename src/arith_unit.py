from commit_unit import CommitUnit
from exec_unit import ExecUnit
from rf import RF
from rs import ReservationStationEntry
from cdb import CommonDataBus
from print import convertToHex
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
        return f"arithReservationStationEntry(pc={convertToHex(self.pc)}, instr={self.instr}, ready={self.isReady()}, res_value={convertToHex(self.res_value)}, rd_idx={self.rd_idx}, rs1_idx={self.rs1_idx}, rs1_value={convertToHex(self.rs1_value)}, rs2_idx={self.rs2_idx}, rs2_value={convertToHex(self.rs2_value)}, op={self.op})"
    
    def __repr__(self):
        return self.__str__()

    def convertToEntry(instr : instr.Instruction):
        """Instruction can be of R-type or I-type."""
        # Create the entry object
        entry = arithReservationStationEntry()
        entry.setInstr(instr.mnemo)
        entry.setPC(instr.address)
        entry.setROBIdx(instr.rob_idx)
        # Set common operands in R/I instr
        entry.rd_idx = instr.fields().rd
        entry.rs1_idx = instr.fields().rs1
        entry.func3 = instr.fields().funct3
        entry.op = instr.fields().opcode


        # If instruction is of R-type
        if (instr.getType() is isa.Rtype):
            entry.rs2_idx = instr.fields().rs2
            entry.func7 = instr.fields().funct7
        elif (instr.getType() is isa.Itype):
            entry.imm = instr.fields().imm


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
    
    def Rtype(op):
        return op == 0b0110011

    def Itype(op):
        return op == 0b0010011
    
    def isReady(self):
        if (arithReservationStationEntry.Rtype(self.op)):
            # R-type
            return self.rs1_value is not None and self.rs2_value is not None
        elif (arithReservationStationEntry.Itype(self.op)):
            # I-type
            return self.rs1_value is not None

    def forwardOperands(self, rf: RF, commit_unit: CommitUnit, cdb : CommonDataBus):
        """Search in the Commit Unit first"""
        #todo split it into smaller functions
        #todo think of implementing all this searchin into the base exec unit class

        # print(commit_unit.commit_queue.queue)
        # Search for rs1
        entry, rob_idx = commit_unit.searchOperand(self.rs1_idx, self.pc)

        cdb_last_result = cdb.getLastResult()
        # print(f"CDB last result: {cdb_last_result}")

        if (entry is not None):
            if (entry.res_ready):
                # In case the result is ready both in ROB or in the commit queue
                # print(f"Forwarding rs1 value {entry.res_value} to {self}")
                self.rs1_value = entry.res_value
            elif (rob_idx is not None):
                self.rs1_idx = rob_idx
        elif (cdb_last_result is not None and cdb_last_result["rd_idx"] == self.rs1_idx):
            # print(f"Forwarding CDB value {cdb_last_result['res_value']} to {self}")
            self.rs1_value = cdb_last_result["res_value"]
        else:
            # No in-flight instruction is computing the value, so get it from RF
            # print(f"Fetching rs1 value {rf[self.rs1_idx]} from RF {self}")
            self.rs1_value = rf[self.rs1_idx]


        if (arithReservationStationEntry.Rtype(self.op)):
            # R-type, search for RS2 too
            # print(commit_unit.commit_queue.queue)
            entry, rob_idx = commit_unit.searchOperand(self.rs2_idx, self.pc)
            # print(entry)

            if (entry is not None):
                if (entry.res_ready):
                    # print(f"Forwarding rs2 value {entry.res_value} to {self}")
                    self.rs2_value = entry.res_value
                elif (rob_idx is not None):
                    self.rs2_idx = rob_idx
            elif (cdb_last_result is not None and cdb_last_result["rd_idx"] == self.rs2_idx):
                # print(f"Forwarding CDB value {cdb_last_result['res_value']} to {self}")
                self.rs2_value = cdb_last_result["res_value"]
            else:
                # No in-flight instruction is computing the value, so get it from RF
                # print(f"Fetching rs2 value {rf[self.rs2_idx]} from RF {self}")
                self.rs2_value = rf[self.rs2_idx]
    
    def updateFromCDB(self, rob_idx, value):
        """Check if can update entry with the value from the CDB."""
        if (self.rs1_idx == rob_idx):
            self.rs1_value = value

        if (arithReservationStationEntry.Rtype(self.op)):
            if (self.rs2_idx == rob_idx):
                self.rs2_value = value


        
class ArithUnit(ExecUnit):
    """
    Arithmetic Unit class, can be used to create different types of execution units
    performing arithmetic operations.
    """
    def __init__(self, n_entries : int, latency : int = 1, iterative : bool = True ) -> None:
        super().__init__(n_entries, arithReservationStationEntry, latency, iterative)

    def execute(self, entry : ReservationStationEntry):
        """Execute the requested operation."""


        match entry.op: # Decoder
            case 0b0110011:
                if (entry.func3 == 0b000 and entry.func7 == 0b0000000):
                    # ADD
                    print(f"ADD {entry.rs1_value} + {entry.rs2_value}")
                    return entry.rs1_value + entry.rs2_value
                elif (entry.func3 == 0b000 and entry.func7 == 0b0100000):
                    # SUB
                    return entry.rs1_value - entry.rs2_value
                elif (entry.func3 == 0b111 and entry.func7 == 0b0000000):
                    # AND
                    return entry.rs1_value & entry.rs2_value
                elif (entry.func3 == 0b110 and entry.func7 == 0b0000000):
                    # OR
                    return entry.rs1_value | entry.rs2_value
                elif (entry.func3 == 0b100 and entry.func7 == 0b0000000):
                    # XOR
                    return entry.rs1_value ^ entry.rs2_value
                elif (entry.func3 == 0b001 and entry.func7 == 0b0000000):
                    # SLL
                    return entry.rs1_value << entry.rs2_value
                elif (entry.func3 == 0b101 and entry.func7 == 0b0000000):
                    # SRL
                    return entry.rs1_value >> entry.rs2_value
                elif (entry.func3 == 0b101 and entry.func7 == 0b0100000):
                    # SRA #todo fix
                    return entry.rs1_value >> entry.rs2_value
                elif (entry.func3 == 0b110 and entry.func7 == 0b0000000):
                    # SLT
                    return 1 if entry.rs1_value < entry.rs2_value else 0
                elif (entry.func3 == 0b111 and entry.func7 == 0b0000000):
                    # SLTU
                    return 1 if ArithUnit.to_unsigned_64bit(entry.rs1_value) < ArithUnit.to_unsigned_64bit(entry.rs2_value) else 0
                else:
                    raise Exception("Not implemented yet.")
            case 0b0010011:
                if (entry.func3 == 0b000):
                    # ADDI
                    return entry.rs1_value + entry.imm
                elif (entry.func3 == 0b111):
                    # ANDI
                    return entry.rs1_value & entry.imm
                elif (entry.func3 == 0b110):
                    # ORI
                    return entry.rs1_value | entry.imm
                elif (entry.func3 == 0b100):
                    # XORI
                    return entry.rs1_value ^ entry.imm
                elif (entry.func3 == 0b001):
                    # SLLI
                    return entry.rs1_value << entry.imm
                elif (entry.func3 == 0b101 and entry.func7 == 0b0000000):
                    # SRLI
                    return entry.rs1_value >> entry.imm
                elif (entry.func3 == 0b101 and entry.func7 == 0b0100000):
                    # SRAI  #todo fix
                    return entry.rs1_value >> entry.imm
                elif (entry.func3 == 0b110):
                    # SLTI
                    return 1 if entry.rs1_value < entry.imm else 0
                elif (entry.func3 == 0b111):
                    # SLTIU
                    return 1 if ArithUnit.to_unsigned_64bit(entry.rs1_value) < ArithUnit.to_unsigned_64bit(entry.imm) else 0
                else:
                    raise Exception("Not implemented yet.")

            case _:
                raise Exception("Not implemented yet.")
    
    def to_unsigned_64bit(value):
        """Utility function to convert a signed 64-bit value to unsigned 64-bit value."""
        return value & 0xFFFFFFFFFFFFFFFF
