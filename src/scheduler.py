from iq             import InstrQueue
from dispatcher     import Dispatcher
from arith_unit     import ArithUnit
from cdb            import CommonDataBus
from commit_unit    import CommitUnit
from rf             import RF
from lsu            import LoadStoreUnit
from dmem           import DataMemory
from branch_unit    import BranchUnit

COMMIT_HISTORY_DUMP = "commit.log"
ROB_DUMP = "rob.log"
MEM_DUMP = "memory.log"


class Scheduler(object):
    """Schedules the updates in a simulation loop, it runs until the 
    - instruction queue is empty,
    - dispatcher is empty,
    - the rob is empty.
    """
    def __init__(self, test_name    : str,
                 mem_name           : str,
                 mem_dump           :  bool = False,
                 commit_history_dump: bool = False,
                 rob_dump           : bool = False
                 ) -> None:
        """Instantiate all the objects"""
        self.iq = InstrQueue(test_name)

        self.dispatcher = Dispatcher()

        self.arith_unit = ArithUnit(8, 1, True)

        self.load_store_unit = LoadStoreUnit()

        self.branch_unit = BranchUnit(8, 1, True)

        self.dmem = DataMemory(filename=mem_name)

        self.cdb = CommonDataBus()

        self.commit_unit = CommitUnit()

        self.rf = RF()

        self.mem_dump = mem_dump

        self.commit_history_dump = commit_history_dump

        self.rob_dump = rob_dump

        self.connect()

        self._cleanDumps()

    def connect(self) -> None:
        """Connect the objects"""
        self.dispatcher.connectIQ(self.iq)
        self.dispatcher.connectRF(self.rf)
        self.dispatcher.connectCommitUnit(self.commit_unit)
        self.dispatcher.connectCDB(self.cdb)

        # make the arithmetic unit visible for the dispatcher
        self.dispatcher.register(self.arith_unit)
        self.dispatcher.register(self.load_store_unit.load_unit)
        self.dispatcher.register(self.load_store_unit.store_unit)
        self.dispatcher.register(self.branch_unit)

        # Connect the LSU to the memory
        self.load_store_unit.connectMemory(self.dmem)
        self.load_store_unit.connectCommitUnit(self.commit_unit)

        # make the arithmetic unit visible for the CDB
        self.cdb.register(self.arith_unit)
        self.cdb.register(self.load_store_unit.load_unit)
        self.cdb.register(self.load_store_unit.store_unit)
        self.cdb.register(self.branch_unit)

        # connect the commit unit to the CDB to update ROB entries,
        # to the RF to write and to the dispatcher to allocate new instructions
        self.commit_unit.connectCDB(self.cdb)
        self.commit_unit.connectDispatcher(self.dispatcher)
        self.commit_unit.connectRF(self.rf)
    
    def step(self, cycle : int):
        """Run one step of the simulation loop"""
        self.commit_unit.step()
        self.arith_unit.step()
        self.branch_unit.step()
        self.load_store_unit.step()
        self.dispatcher.step()

        # Dump the data structures
        self.dump(cycle)

        if (self.check()):
            if (self.commit_history_dump):
                self.dumpDataStructure(self.commit_unit.commitHistory(), COMMIT_HISTORY_DUMP, None)

            raise Exception("Simulation is over")

    def check(self):
        """Check if the simulation is over"""

        return self.iq.empty() and self.dispatcher.empty() and self.commit_unit.empty()
    
    
    def dump(self, cycle : int):
        """Take care of dumping stuff"""
        
        if (self.rob_dump):
            self.dumpDataStructure(self.commit_unit.rob, ROB_DUMP, cycle)
        
        if (self.mem_dump):
            self.dumpDataStructure(self.dmem, MEM_DUMP, cycle)


    def _cleanDumps(self):
        """Clean the dump files"""
        with open(COMMIT_HISTORY_DUMP, "w") as f:
            pass

        with open(ROB_DUMP, "w") as f:
            pass

        with open(MEM_DUMP, "w") as f:
            pass

    def dumpDataStructure(self, data_structure, filename, cycle):
        """Dump a data structure, said data structure musti implement the __str__ method"""

        with open(filename, "a") as f:
            f.write("Cycle: " + str(cycle) + "\n") if cycle is not None else None
            f.write(str(data_structure))