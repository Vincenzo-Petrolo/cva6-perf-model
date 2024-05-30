from queue import Queue
from arith_unit import ArithUnit
from exec_unit import ExecUnit
from rs import ReservationStationEntry
import isa


class Dispatcher(object):
    """ Rules for the dispatcher:
        What each Execution Unit can do.
        Instructions to be dispatched must be mapped here.

        Map an EU to a set of instructions.

        !!!Warning!!!
        If you add custom instructions or new execution units, you must
        update the mapping rules, otherwise it will raise a Python exception.
    """
    rules = {
        #############################################
        # Instr Type                    : Exec Unit # 
        #############################################
        isa.Itype                       : ArithUnit,
        isa.Rtype                       : ArithUnit,

    }

    """
     Map a class to the available ExecUnits for that class.
    """
    EUS_mapping = {
        ArithUnit : []
    }

    """ 
    Issue the instructions to the reservation stations.
    """
    def __init__(self, n_issue : int = 1) -> None:

        # Number of issued instructions per cycle
        self.n_issue = n_issue

        # Dispatch buffer
        """A typical buffer entry is a dictionary with the following keys
        {
            "line" : str,
            "address" : int,
            "hex_code" : str,
            "mnemo" : str,
            "rob_idx" : int | None
        } 

        In the beginning, the rob_idx is None, but when the ROB has space, the
        instruction is allocated a space in the ROB and the rob_idx is updated.
        """
        self.buffer_o = [Queue(1) for _ in range(n_issue)]

        # Instruction Queue
        self.iq = None

    def register(self, eu):
        """Register the execution unit to the Dispatcher."""
        Dispatcher.EUS_mapping[eu.__class__].append(eu)
    
    def connectIQ(self, iq):
        """Connect the instruction queue to the dispatcher.
        """
        self.iq = iq
    
    def check(self):
        """Check if instruction queue is connected"""
        if self.iq is None:
            raise Exception("Instruction Queue is not connected to the dispatcher.")
        
    def convertInstr(line, address, hex_code, mnemo):
        """
        Get a raw HEX instruction and convert it to an Instruction object so that
        we can get its type.
        """
        c_instr = isa.Instruction(line, address, hex_code, mnemo)

        return c_instr



    def step(self):
        """Steps to perform in a cycle:
        1. Iterate over the buffers, if there is an instruction, issue it by
        removing it from the buffer and sending it to the execution unit.
        If we find a hole in the buffer, place an instruction from the instruction
        queue.
        """
        for buffer in self.buffer_o:
            # Check if the buffer is empty
            if buffer.empty():
                # Check if we can issue an instruction
                if not self.iq.empty():
                    instr = self.iq.get()
                    buffer.put(instr)
            else:
                # See if we can issue the instruction
                instr_ = buffer.get()

                # Check if the instruction was allocated in the ROB
                if instr_["rob_idx"] is None:
                    # Put instruction back to the buffer
                    buffer.put(instr_)
                    # Continue to the next buffer entry
                    continue

                instr_obj = Dispatcher.convertInstr(
                    instr_["line"],
                    instr_["address"],
                    instr_["hex_code"],
                    instr_["mnemo"]
                )

                # See which execution unit can handle this instruction
                eus = Dispatcher.rules[instr_obj.getType()]

                if (len(eus) == 0):
                    raise Exception(f"No execution unit can accept this instruction {instr_obj}")
                
                # Iterate over the execution units
                could_issue = False

                for eu in eus:
                    could_issue = self.issue(eu, instr_obj, instr_["rob_idx"])

                if (could_issue == False):
                    # If couldn't issue the instructon, put it back to the buffer
                    buffer.put(instr_)
    
    def issue(self, eu : ExecUnit, instr : isa.Instruction, rob_idx : int):
        """Issue an instruction to an execution unit"""
        # First get the entry type for this execution unit
        entry_t = eu.rs.entry_t

        # Create an entry
        entry = entry_t.convertToEntry(instr)

        # Update the entry with basic info
        entry.setPC(instr.pc)
        entry.setROBIdx(rob_idx)
        entry.setInstr(instr.mnemo)

        # Issue the entry to the execution unit
        could_issue = eu.issue(entry)

        return could_issue




