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

    def __repr__(self):
        return self.mnemo

