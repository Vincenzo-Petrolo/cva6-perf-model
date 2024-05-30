from abc import ABC, abstractmethod
from queue import Queue
from rs import ReservationStation, ReservationStationEntry
from pipeline import Pipeline

class ExecUnit(ABC):
    def __init__(self, n_entries : int , reservation_station_t : type[ReservationStationEntry], latency : int = 1, iterative : bool = True ) -> None:
        super().__init__()
        # Result at the output of the execution unit
        self.result = None

        # Ready signal for the result
        self.ready = False

        # Destination register index
        self.rd_idx = None

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
    
    def stepExecution(self):
        self.ex_ctr = max(0, self.ex_ctr-1)

    def hasResult(self):
        return self.ready
    
    def setExecutionDone(self):
        self.ready = True

        # Pop the instruction from the pipeline
        self.result = self.pipeline.popLastInstruction()
    
    def setIdle(self):
        self.status = 'idle'
        self.ready = False
    
    def setExecuting(self):
        self.status = 'executing'
        self.ready = False

    def getResult(self):
        return {"res_value": self.result, "valid": self.ready, "rd_idx": self.rd_idx}
    
    def step(self):
        """Steps to do:
        1. Check if buffer_o is clear, else don't pop new instructions (except if they are None)
        2. Pop the computed instruction from the execution pipeline
        3. If there is a new instruction, and no other instruction is executing, 
        and the execution unit is in iterative mode, get the instruction
        and execute it.
        """

        # Step 1 & 2
        if self.buffer_o.empty() and self.pipeline.getLastInstruction() is not None:
            self.setExecutionDone()
            result = self.pipeline.popLastInstruction()

            self.buffer_o.put(result)

        # Step 3
        if self.pipeline.canGetNewInstruction():

            entry = self.rs.getEntryReadyForExecution()

            # If there are ready instructions
            if entry is not None:
                # Execute the instruction
                self.startExecution(entry)
            else:
                # Just advance the pipeline if no new entry
                self.pipeline.advance()
        
