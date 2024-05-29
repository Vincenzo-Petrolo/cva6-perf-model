from abc import ABC, abstractmethod

class ExecUnit(ABC):
    def __init__(self) -> None:
        super().__init__()
        # Result at the output of the execution unit
        self.result = None

        # Ready signal for the result
        self.ready = False

        # Destination register index
        self.rd_idx = None
        


    @abstractmethod
    def execute(self, instr):
        """Implement the execution of the instruction."""
        pass

    def hasResult(self):
        # TODO implement me
        pass
    
    def setExecutionDone(self):
        # TODO implement me
        pass

    def getNextInstruction(self):
        # TODO implement me
        pass

    def getResult(self):
        return {"res_value": self.result, "valid": self.ready, "rd_idx": self.rd_idx}
        
