from queue import Queue

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
        self.buffer_o = Queue(1)

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
        if (self.buffer_o.empty()):
            return None

        return self.buffer_o.get()


    def step(self):
        """Steps to perform in a cycle:
        1. Check if CDB is empty
        2. Iterate over the execution units.
        3. Check if the execution unit has a result ready.
        4. If the result is ready, update the current output.
        """
        # Step 1
        if (self.buffer_o.full()):
            return


        # Step 2
        for eu in self.EUS:
            # Step 3
            if eu.hasResult():
                print(f"CDB Step, getting results from {eu}")
                # Step 4
                self.buffer_o.put(eu.getResult())
