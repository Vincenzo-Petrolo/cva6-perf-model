from arith_unit import ArithUnit
from exec_unit import ExecUnit
from customQueue import CustomQueue
from instr import Instruction
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
        self.buffer_o = CustomQueue(max_size=self.n_issue)

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
        

    def step(self):
        """Steps to perform in a cycle:
        1. Pull in new instructions if there is space.
        2. Pop all instructions pulled into the ROB if there is space in Reservation Stations.
        """

        # Step 1
        while not self.buffer_o.full():
            # Check if we can pull in new instructions
            if not self.iq.empty():
                self.enqueueInstruction()
            else:
                break


        # Step 2
        for i, instr in enumerate(self.buffer_o):
            # Check if the instruction was not allocated in the ROB
            if instr.rob_idx is None:
                # Continue to the next entry
                continue

            # See which execution unit can handle this instruction
            eus = Dispatcher.EUS_mapping[Dispatcher.rules[instr.getType()]]

            if (len(eus) == 0):
                raise Exception(f"No execution unit can accept this instruction {instr}")
            
            # Iterate over the execution units
            could_issue = False

            for eu in eus:
                could_issue = self.issue(eu, instr)

                # If could issue, then free buffer entry
                if could_issue:
                    self.buffer_o.pop_at(i)
    
    def issue(self, eu : ExecUnit, instr : Instruction):
        """Issue an instruction to an execution unit"""
        # Issue the entry to the execution unit
        could_issue = eu.issue(instr)

        return could_issue

    def enqueueInstruction(self):
        """Enqueue an instruction to the dispatcher."""
        instr = self.iq.get()

        self.buffer_o.enqueue(instr)
        
    def getIssuableInstructions(self, n):
        """Get n instructions that can be allocated in ROB."""
        instrs = []

        i = 0

        while i < len(self.buffer_o) and i < n:
            instr = self.buffer_o[i]
            instrs.append(instr)

            i += 1
        
        
        return instrs
    
    def empty(self):
        return self.buffer_o.empty()