from queue import Queue
from arith_unit import arithReservationStationEntry, ArithUnit
import isa


class Dispatcher(object):
    """Rules for the dispatcher:
        Where each instruction should go to.
        Instructions to be dispatched must be mapped here.

        Map an EU to a set of instructions.

        !!!Warning!!!
        If you add custom instructions or new execution units, you must
        update the mapping rules, otherwise it will raise a Python exception.
    """
    rules = {
        ########################################################################
        # Exec Unit type    : [instr type1, instr type2, instr type3, ...]     #   
        ########################################################################
        ArithUnit           : [isa.Itype, isa.Rtype],                           # Instructions for the Arithmetic Unit

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
        self.buffer_o = Queue(self.n_issue)

    def register(self, eu):
        """Register the execution unit to the Dispatcher.
        """
        self.EUS.append(eu)
    

    def step(self):
        """Steps to perform in a cycle:
        1. 
        """
