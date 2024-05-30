from queue import Queue
from arith_unit import arithReservationStationEntry, ArithUnit
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

        # Empty list of execution units
        self.EUS = []

        # Dispatch buffer
        self.buffer_o = [Queue(1) for _ in range(n_issue)]

        # Instruction Queue
        self.iq = None

    def register(self, eu):
        """Register the execution unit to the Dispatcher.
        """
        self.EUS.append(eu)
    
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

                instr_obj = Dispatcher.convertInstr(
                    instr["line"],
                    instr["address"],
                    instr["hex_code"],
                    instr["mnemo"]
                )

                # See which execution unit can handle this instruction
                eus = Dispatcher.rules[instr_obj.getType()]

                if (len(eus) == 0):
                    raise Exception(f"No execution unit available for instruction {instr_obj}")
                
                # Iterate over the execution units
                could_issue = False

                for eu in eus:
                    # Issue the instruction
                    could_issue = eu.issue(arithReservationStationEntry.convertToEntry(instr_obj))

                    if (could_issue == True):
                        # The instruction was able to issue
                        break
                
                if (could_issue == False):
                    # If couldn't issue the instructon, put it back to the buffer
                    buffer.put(instr_)
