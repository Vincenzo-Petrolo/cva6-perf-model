
class CommonDataBus(object):
    """Resembles the Common Data Bus of LEN5 processor.
        All the execution units can write to the CDB, the arbiter will
        give priority to those units registered before the others.
        (in hardware this is done by the priority encoder, here we will
        use the order of the list of units to determine the priority) 
    """
    def __init__(self) -> None:

        # Empty list of execution units
        self.EUS = []

        # This is used as a container to store the current value
        # that the CDB is holding, this is used for the ROB to be
        # able to read the value from the CDB.
        self.currentOutput = {"rd_idx": None, "res_value": None, "valid" : False}

        pass

    def register(self, eu):
        """Register the execution unit to the CDB.
        The execution units will be registered in the order they are
        added to the CDB.
        """
        self.EUS.append(eu)
    
    def get(self):
        """Get the current value from the CDB.
        This is used by the ROB to read the value from the CDB.
        """
        return self.currentOutput


    def step(self):
        """Steps to perform in a cycle:
        1. Iterate over the execution units.
        2. Check if the execution unit has a result ready.
        3. If the result is ready, update the current output.
        """

        # Prepare the current output to be invalid
        self.currentOutput = {"rd_idx": None, "res_value": None, "valid" : False}

        # Step 1
        for eu in self.EUS:
            # Step 2
            if eu.hasResult():
                # Step 3
                self.currentOutput = eu.getResult()
