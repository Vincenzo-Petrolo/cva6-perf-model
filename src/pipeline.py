class Pipeline:
    def __init__(self, num_stages: int = 2, iterative : bool = False):

        if (num_stages < 2):
            raise ValueError("Pipeline must have at least 2 stages")

        self.num_stages = num_stages

        self.stages = [None for _ in range(num_stages)] 

        self.iterative = iterative

    def addInstruction(self, instruction) -> bool:
        """Add an instruction to the pipeline.
        If the pipeline is iterative, and there is currently an in-flight
        instruction, the instruction is not added and False is returned.
        """
        if (self.iterative and self._hasInFlightInstruction()):
            return False

        self.stages[0] = instruction

        return True
    
    def _hasInFlightInstruction(self):
        for instr in self.stages:
            if instr is not None:
                return True
        
        return False

    def advance(self):
        #? This is not very efficient, but it is simple
        # Move instructions through the pipeline
        for i in range(self.num_stages-1, 0, -1):
            # Do not overwrite the i-th instruction
            # because if it is not None, it means it could not be
            # moved to the next stage
            if (self.stages[i] is None):
                self.stages[i] = self.stages[i-1]

    def popLastInstruction(self):
        # Remove the instruction at the end of the pipeline
        last_instruction = self.stages[-1]
        self.stages[-1] = None
        return last_instruction

    def getLastInstruction(self):
        # Get the instruction at the end of the pipeline
        return self.stages[-1]
    
    def canGetNewInstruction(self):
        if (self.iterative):
            return not self._hasInFlightInstruction()
        
        # If first entry is None, I can get a new instruction
        return self.stages[0] is None

    def __repr__(self):
        return f"Pipeline(stages={list(self.stages)})"