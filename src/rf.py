class RF( object ):
    """Resembles the register file of LEN5 processor."""
    def __init__(s, *args, **kwargs):
        # 32 registers
        s.regs = [0]*32

    def read(s, idx: int) -> int:
        """Read the value from the register."""

        if (idx == 0):
            return 0
        if (idx > 0 and idx < 32):
            return s.regs[idx]
        else:
            raise ValueError(f"Invalid register index {idx}")

    def write(s, idx: int, value: int):
        """Write the value to the register."""
        if (idx > 0 and idx < 32):
            s.regs[idx] = value

    def __getitem__(s, idx: int) -> int:
        """Read the value from the register."""
        return s.read(idx)

    def __setitem__(s, idx: int, value: int):
        """Write the value to the register."""
        s.write(idx, value)
    
    def __str__(self) -> str:
        """Dump all the register file content."""
        return "\n".join([f"RF[{i}]={self.regs[i]}" for i in range(32)])