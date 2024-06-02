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
        
        # If the pipeline has no new results
        if (self.hasResult() == False):
            # Search for done entries in the RS
            entry = self.rs.getEntryDone()
            if (entry is None):
                return None
            else:
                # Return a previous entry
                return {
                    "res_value": entry.getResult(),
                    "rd_idx": entry["rd_idx"],
                    "rob_idx": entry.getROBIdx(),
                    "valid" : True
                }


        # If the pipeline has a fresh result, then don't store in the RS
        # directly give it to the CDB
        result  = self.pipeline.popLastInstruction()

        # Clear the entry
        self.rs.clearEntry(result["rob_idx"])

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
        1. If last pipeline stage was not gotten from CDB previously, then
        store the result in the RS.
        2. Issue an instruction if pipeline is not stalled.
        """

        if (self.hasResult()):
            # Update the reservation station with the result
            #todo check for correctness of this new feature
            result = self.pipeline.popLastInstruction()
            self.rs.updateResult(result["rob_idx"], result["res_value"])

        self.pipeline.advance()

        # Step 1
        if self.pipeline.canGetNewInstruction():
            entry = self.rs.getEntryReadyForExecution()

            if (entry is None):
                return

            print(f"Got ready entry {entry} from RS with ROB idx {entry["entry"].getROBIdx()}")
            # Execute the instruction, if it is  None, then a bubble is inserted
            self.startExecution(entry)

        # print(self.pipeline)

        
