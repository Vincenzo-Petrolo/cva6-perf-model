from abc import ABC, abstractmethod
from queue import Queue
from rs import ReservationStation, ReservationStationEntry
from pipeline import Pipeline

class ExecUnit(ABC):
    def __init__(self, n_entries : int , reservation_station_t : type[ReservationStationEntry], latency : int = 1, iterative : bool = True ) -> None:
        super().__init__()

        # Create the reservation station with the given type
        self.rs = ReservationStation(n_entries, reservation_station_t)

        # Latency of the execution unit
        self.latency = latency

        # Execution pipeline
        self.pipeline = Pipeline(latency, iterative)

        # Output buffer
        self.buffer_o   = Queue(1)


    @abstractmethod
    def execute(self, entry : ReservationStationEntry):
        """Implement the execution of the instruction.
        You are given with an entry from the reservation station
        and must perform operation with it. 
        """
        pass
    
    def startExecution(self, entry):
        self.setExecuting()

        res_value   = self.execute(entry)
        rob_idx     = entry.getROBIdx()

        # Push the result to the pipeline
        self.pipeline.addInstruction(
            {
                "res_value": res_value,
                "rd_idx": rob_idx
            }
        )
    
    def hasResult(self):
        return self.buffer_o.full()
    
    def setResult(self, result):
        self.buffer_o.put(
            {
                "res_value": result["res_value"],
                "valid": True,
                "rd_idx": result["rd_idx"]
            }
        )

    def getResult(self):
        return self.buffer_o.get()
    
    def setIdle(self):
        self.status = 'idle'
        self.ready = False
    
    def setExecuting(self):
        self.status = 'executing'
        self.ready = False

    
    def step(self):
        """Steps to do:
        1. Check if buffer_o is clear, else don't pop new instructions (except if they are None)
        2. Pop the computed instruction from the execution pipeline
        3. Issue an instruction if pipeline is not stalled.
        """

        # Step 1 & 2
        if self.buffer_o.empty() and self.pipeline.getLastInstruction() is not None:
            result = self.pipeline.popLastInstruction()
            self.setExecutionDone(result)

        # Step 3
        self.pipeline.advance()

        if self.pipeline.canGetNewInstruction():

            entry = self.rs.getEntryReadyForExecution()

            # Execute the instruction, if it is  None, then a bubble is inserted
            self.startExecution(entry)
        
