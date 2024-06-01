from abc import ABC, abstractmethod
from queue import Queue
from rs import ReservationStation, ReservationStationEntry
from pipeline import Pipeline

class ExecUnit(ABC):
    """
    Execution Unit class, can be used to create different types of execution units
    performing arithmetic operations.
    Maybe it can be used also as a branch unit, but definitely not as LSU.

    Remember to implement the execute method!
    """
    def __init__(self, n_entries : int , reservation_station_t : type[ReservationStationEntry], latency : int = 1, iterative : bool = True ) -> None:
        super().__init__()

        # Create the reservation station with the given type
        self.rs = ReservationStation(n_entries, reservation_station_t)

        # Latency of the execution unit
        self.latency = latency

        # Execution pipeline
        self.pipeline = Pipeline(latency, iterative)


    @abstractmethod
    def execute(self, entry : ReservationStationEntry):
        """Implement the execution of the instruction.
        You are given with an entry from the reservation station
        and must perform operation with it. Return the result.
        """
        return None
    
    def startExecution(self, entry):
        self.setExecuting()

        res_value   = self.execute(entry["entry"])
        rd_idx      = entry["entry"].rd_idx

        # Push the result to the pipeline
        self.pipeline.addInstruction(
            {
                "res_value": res_value,
                "rd_idx": rd_idx,
                "rob_idx": entry["entry"].getROBIdx(),
                "valid" : True
            }
        )
    
    def hasResult(self):
        """Directly access the last stage of the pipeline."""
        return self.pipeline.getLastInstruction() is not None

    
    def getResult(self):
        """Pop the result from the last stage of the pipeline."""
        
        if (self.hasResult() == False):
            return None

        result  = self.pipeline.popLastInstruction()

        # Update the result in the reservation station
        self.rs.updateResult(result["rob_idx"])

        return result
    
    def issue(self, entry : ReservationStationEntry) -> bool:
        """Issue an instruction to the execution unit.
        If the instruction is issued, it is converted to an entry
        and stored in the reservation station.
        """
        return self.rs.issue(entry)
    
    def setIdle(self):
        self.status = 'idle'
        self.ready = False
    
    def setExecuting(self):
        self.status = 'executing'
        self.ready = False

    
    def step(self):
        """Steps to do:
        1. Issue an instruction if pipeline is not stalled.
        """

        self.pipeline.advance()

        # Step 1
        if self.pipeline.canGetNewInstruction():
            entry = self.rs.getEntryReadyForExecution()
            print(f"Got ready entry {entry} from RS")

            if (entry is None):
                return

            # Execute the instruction, if it is  None, then a bubble is inserted
            self.startExecution(entry)

        print(self.pipeline)
        for e in self.rs.entries:
            print(e)

        
