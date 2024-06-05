from commit_unit import CommitUnit
from exec_unit import ExecUnit
from rf import RF
from rs import ReservationStationEntry
from cdb import CommonDataBus

import instr, isa


class branchReservationStationEntry(ReservationStationEntry):
    """Resembles the Reservation Station Entry of a generic Arithmetic Unit of LEN5 processor."""
    def __init__(self) -> None:
        super().__init__()
        self.rd_idx     = None
        self.rs1_idx    = None
        self.rs1_value  = None
        self.rs2_idx    = None
        self.rs2_value  = None
        self.op         = None
        self.imm        = None
        self.funct3     = None
        self.cmp_result = None


    def __str__(self):
        return f"branchReservationStationEntry(pc={self.pc}, instr={self.instr}, ready={self.isReady()}, res_value={self.res_value}, rd_idx={self.rd_idx}, rs1_idx={self.rs1_idx}, rs1_value={self.rs1_value}, rs2_idx={self.rs2_idx}, rs2_value={self.rs2_value}, op={self.op}, imm={self.imm}, funct3={self.funct3}, cmp_result={self.cmp_result})"
    
    def __repr__(self):
        return self.__str__()

    def convertToEntry(instr : instr.Instruction):
        """Instruction can be of R-type or I-type."""
        # Create the entry object
        entry = branchReservationStationEntry()
        entry.setInstr(instr.mnemo)
        entry.setPC(instr.address)
        entry.setROBIdx(instr.rob_idx)

        if (instr.getType() is isa.Btype): #Branch
            entry.rs2_idx = instr.fields().rs2
            entry.rs1_idx = instr.fields().rs1
            entry.funct3 = instr.fields().funct3
            entry.imm = instr.fields().imm
            entry.rd_idx = -1 #Don't need to write to RF
        elif (instr.getType() is isa.Jtype ): #Unconditional Jump
            entry.rd_idx = instr.fields().rd
            entry.imm = instr.fields().imm
        elif (instr.getType() is isa.Itype): #JALR
            entry.rd_idx = instr.fields().rd
            entry.imm = instr.fields().imm
            entry.rs1_idx = instr.fields().rs1
            entry.funct3 = instr.fields().funct3

        entry.op = instr.fields().opcode

        return entry
    
    def isReady(self):
        if (self.rs2_idx is not None): # Branch instruction requires rs2
            return self.rs2_value is not None and self.rs1_value is not None
        elif (self.rs1_idx is not None): # JALR
            return self.rs1_value is not None
        else: # Unconditional Jump
            """Always ready"""
            return True


    def forwardOperands(self, rf: RF, commit_unit: CommitUnit, cdb : CommonDataBus):
        """Search in the Commit Unit first"""
        #todo split it into smaller functions
        #todo think of implementing all this searchin into the base exec unit class

        # print(commit_unit.commit_queue.queue)
        if (self.rs1_idx is not None):
            # Search for rs1
            entry, rob_idx = commit_unit.searchOperand(self.rs1_idx, self.pc)
            # print(entry)

            cdb_last_result = cdb.getLastResult()
            # print(f"CDB last result: {cdb_last_result}")

            if (entry is not None):
                if (entry.res_ready):
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

        if (self.rs2_idx is not None):
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
        if (self.rs1_idx is not None):
            if (self.rs1_value is None and self.rs1_idx == rob_idx):
                self.rs1_value = value

        if (self.rs2_idx is not None):
            if (self.rs2_value is None and self.rs2_idx == rob_idx):
                self.rs2_value = value

        
class BranchUnit(ExecUnit):
    """
    Arithmetic Unit class, can be used to create different types of execution units
    performing arithmetic operations.
    """
    def __init__(self, n_entries : int, latency : int = 1, iterative : bool = True ) -> None:
        super().__init__(n_entries, branchReservationStationEntry, latency, iterative)

    def execute(self, entry : branchReservationStationEntry):
        """Execute the requested operation."""
        if (entry.rs2_idx is not None): # Branch
            match entry.funct3:
                case 0b000: # BEQ
                    entry.cmp_result = entry.rs1_value == entry.rs2_value
                case 0b001: # BNE
                    entry.cmp_result = entry.rs1_value != entry.rs2_value
                case 0b100: # BLT
                    entry.cmp_result = entry.rs1_value < entry.rs2_value
                case 0b101: # BGE
                    entry.cmp_result = entry.rs1_value >= entry.rs2_value
                case 0b110: # BLTU
                    entry.cmp_result = BranchUnit.toUnsigned64bit(entry.rs1_value)\
                          < BranchUnit.toUnsigned64bit(entry.rs2_value)
                case 0b111: # BGEU
                    entry.cmp_result = BranchUnit.toUnsigned64bit(entry.rs1_value)\
                    >= BranchUnit.toUnsigned64bit(entry.rs2_value)
                case _:
                    raise Exception("Branch operation not supported.")
            return None
        elif (entry.rs1_idx is not None): # JALR
            match entry.funct3:
                case 0b000: # JALR
                    entry.cmp_result = True
                    return entry.getPC() + 4
                case _:
                    raise Exception("Branch operation not supported.")
        else: # Unconditional Jump
            entry.cmp_result = True
            return entry.getPC() + 4
    
    def toUnsigned64bit(value):
        return value & 0xFFFFFFFFFFFFFFFF