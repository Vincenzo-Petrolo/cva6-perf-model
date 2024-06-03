from iq             import InstrQueue
from dispatcher     import Dispatcher
from arith_unit     import ArithUnit
from cdb            import CommonDataBus
from commit_unit    import CommitUnit
from rf             import RF
from lsu            import LoadStoreUnit
from dmem           import DataMemory
from branch_unit    import BranchUnit



class Scheduler(object):
    """Schedules the updates in a simulation loop, it runs until the 
    - instruction queue is empty,
    - dispatcher is empty,
    - the rob is empty.
    """
    def __init__(self, test_name : str) -> None:
        """Instantiate all the objects"""
        self.iq = InstrQueue(test_name)

        self.dispatcher = Dispatcher()

        self.arith_unit = ArithUnit(8, 1, True)

        self.load_store_unit = LoadStoreUnit()

        self.branch_unit = BranchUnit(8, 1, True)

        self.dmem = DataMemory()

        self.cdb = CommonDataBus()

        self.commit_unit = CommitUnit()

        self.rf = RF()

        self.connect()

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
    
    def step(self):
        """Run one step of the simulation loop"""
        self.commit_unit.step()
        self.arith_unit.step()
        self.branch_unit.step()
        self.load_store_unit.step()
        self.dispatcher.step()

        print(self.commit_unit.rob)

        if (self.check()):
            raise Exception("Simulation is over")

    def check(self):
        """Check if the simulation is over"""
        return self.iq.empty() and self.dispatcher.empty() and self.commit_unit.empty()



