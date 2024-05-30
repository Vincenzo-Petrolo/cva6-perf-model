from isa import Instr, Reg

class Instruction(Instr):
    """Represents a RISC-V instruction with annotations"""

    def __init__(self, line, address, hex_code, mnemo):
        Instr.__init__(self, int(hex_code, base=16))
        self.line = line
        self.address = int(address, base=16)
        self.hex_code = hex_code
        self.mnemo = mnemo
        self.events = []

    def mnemo_name(self):
        """The name of the instruction (fisrt word of the mnemo)"""
        return self.mnemo.split()[0]

    def next_addr(self):
        """Address of next instruction"""
        return self.address + self.size()

    _ret_regs = [Reg.ra, Reg.t0]

    def is_ret(self):
        "Does CVA6 consider this instruction as a ret?"
        f = self.fields()
        # Strange conditions, no imm check, no rd-discard check
        return self.is_regjump() \
                and f.rs1 in Instruction._ret_regs \
                and (self.is_compressed() or f.rs1 != f.rd)

    def is_call(self):
        "Does CVA6 consider this instruction as a ret?"
        base = self.base()
        f = self.fields()
        return base == 'C.JAL' \
            or base == 'C.J[AL]R/C.MV/C.ADD' and f.name == 'C.JALR' \
            or base in ['JAL', 'JALR'] and f.rd in Instruction._ret_regs

    def __repr__(self):
        return self.mnemo

