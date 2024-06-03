from instr import Instruction

#   typedef struct packed {
#     instr_t instruction;  // the instruction
#     logic [XLEN-1:0] instr_pc;  // the program counter of the instruction
#     logic res_ready;  // the result of the instruction is ready
#     logic [XLEN-1:0] res_value;  // the value of the result (from the EU)
#     logic [REG_IDX_LEN-1:0] rd_idx;  // the destination register (rd)
#     logic rd_upd;  // update the destination register (rd)
#     logic mem_crit;  // memory accesses shall wait for this instruction to complete
#     logic order_crit;  // no out-of-order commit allowed
#     logic except_raised;  // an exception has been raised
#     except_code_t except_code;  // the exception code
#     logic mem_clear;  // clear to commit to memory out of order (stores only)
#   } rob_entry_t;

class ROBEntry():
    def __init__(self) -> None:
        self.instruction = None
        self.instr_pc = None
        self.res_ready = False
        self.res_value = None
        self.rd_idx = None
        self.rd_upd = None
        self.mem_crit = None
        self.order_crit = None
        self.except_raised = None
        self.except_code = None
        self.mem_clear = None
        self.valid = False

    def __str__(self):
        return f"ROBEntry(instruction={self.instruction}, instr_pc={self.instr_pc}, res_ready={self.res_ready}, res_value={self.res_value}, rd_idx={self.rd_idx}, valid={self.valid})"

    def __repr__(self):
        return self.__str__()
    
    def convertInstructionToROBEntry(instr: Instruction):
        entry = ROBEntry()

        entry.instruction = instr
        entry.instr_pc = instr.address
        try:
            entry.rd_idx = instr.fields().rd
        except AttributeError:
            # In case an instruction has no destination register
            entry.rd_idx = -1

        entry.valid = True

        return entry

class ROB():
    """Reorder Buffer data structure."""
    def __init__(self, size: int) -> None:
        self.size = size
        self.entries = [ROBEntry() for _ in range(size)]
        self.head = 0
        self.tail = 0
        self.count = 0

    def __str__(self):
        """Dump each entry of the ROB."""
        return "\n".join([f"ROB[{i}]={entry}" for i, entry in enumerate(self.entries)])


    def __repr__(self):
        return self.__str__()

    def is_empty(self) -> bool:
        return self.count == 0

    def is_full(self) -> bool:
        return self.count == self.size

    def push(self, instr: Instruction) -> int:
        """This is done by the issue unit, it pushes the instruction to the ROB."""
        if self.is_full():
            return -1

        self.entries[self.tail] = ROBEntry.convertInstructionToROBEntry(instr)

        rob_idx = self.tail

        self.tail = (self.tail + 1) % self.size
        self.count += 1

        # Return the index of the entry
        return rob_idx

    def pop(self) -> ROBEntry:
        if self.is_empty():
            return None
        entry = self.entries[self.head]

        # Make a copy of the entry
        entry_copy = ROBEntry()
        entry_copy.instruction = entry.instruction
        entry_copy.instr_pc = entry.instr_pc
        entry_copy.res_ready = entry.res_ready
        entry_copy.res_value = entry.res_value
        entry_copy.rd_idx = entry.rd_idx
        entry_copy.valid = entry.valid


        # Invalidate the current entry
        entry.valid = False

        # print(f"Clearing ROB Entry {self.head} {entry}")
        # Clear the ROB Entry
        self.entries[self.head] = ROBEntry()

        self.head = (self.head + 1) % self.size
        self.count -= 1

        return entry_copy

    def peek(self) -> ROBEntry:
        if self.is_empty():
            return None
        return self.entries[self.head]

    def clear(self) -> None:
        self.head = 0
        self.tail = 0
        self.count = 0
        self.entries = [ROBEntry() for _ in range(self.size)]
    
    def updateResult(self, rd_idx: int, res_value: int, rob_idx : int) -> None:
        """Update the result of the instruction in the ROB, this comes from the CDB."""
        # print(f"Updating result for ROB Entry {rob_idx}")
        entry = self.entries[rob_idx]

        # rd_idx == -1 means that the instruction has no destination register
        if (entry.rd_idx == -1):
            entry.res_ready = True
            entry.res_value = 0
            entry.valid = False
        elif entry.rd_idx == rd_idx:
            entry.res_ready = True
            entry.res_value = res_value
            entry.valid = True
        else:
            raise ValueError(f"ROB Entry {rob_idx} does not match the destination register {rd_idx}")

    def __getitem__(self, key: int) -> ROBEntry:
        return self.entries[key]

    def __setitem__(self, key: int, value: ROBEntry) -> None:
        self.entries[key] = value

    def __len__(self) -> int:
        return self.size
    
    def searchOperand(self, rs_idx: int, inst_addr : int) -> ROBEntry:
        """Searches the most recent entry that has rd_idx with the rs_idx
        it must be valid, and of course, it must not be the current instruction.
        Keep in mind that the ROB is a circular buffer, so we must search
        from the head to the tail."""
        i = self.head
        while i != self.tail:
            entry = self.entries[i]

            if entry.rd_idx == rs_idx and entry.valid and entry.instr_pc != inst_addr:
                return entry

            i = (i+1) % self.size
        return None
    
    def canCommit(self) -> bool:
        """Check if the head of the ROB can be committed."""
        if self.is_empty():
            return False
        return self.entries[self.head].res_ready
    
    def freeSlots(self) -> int:
        """Return the number of free slots in the ROB."""
        return self.size - self.count