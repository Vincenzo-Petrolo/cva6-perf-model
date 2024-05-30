from collections import deque

class Pipeline:
    def __init__(self, num_stages: int, iterative : bool = False):
        self.num_stages = num_stages

        self.stages = deque([None] * num_stages, maxlen=num_stages)

        self.iterative = iterative

    def addInstruction(self, instruction) -> bool:
        """Add an instruction to the pipeline.
        If the pipeline is iterative, and there is currently an in-flight
        instruction, the instruction is not added and False is returned.
        """
        if (self.iterative and self._hasInFlightInstruction()):
            return False
        
        self.stages.appendleft(instruction)

        return True
    
    def _hasInFlightInstruction(self):
        for instr in self.stages:
            if instr is not None:
                return True
        
        return False

    def advance(self):
        # Move instructions through the pipeline
        # The instruction at the end is automatically discarded if it's None
        self.stages.appendleft(None)

    def popLastInstruction(self):
        # Remove the instruction at the end of the pipeline
        return self.stages.pop()

    def getLastInstruction(self):
        # Get the instruction at the end of the pipeline
        return self.stages[-1]
    
    def canGetNewInstruction(self):
        if (self.iterative):
            return self._hasInFlightInstruction()
        
        # If first entry is None, we can get a new instruction
        return self.stages[0] is None

    def __repr__(self):
        return f"Pipeline(stages={list(self.stages)})"