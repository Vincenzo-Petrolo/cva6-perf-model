from rob import ROB, ROBEntry

# Import the queue data structure from the Python standard library
from queue import Queue

# Commit Unit Implementation

class CommitUnit( object ):
    """Resembles the commit unit of LEN5 processor"""
    def __init__(self):
        # Reorder Buffer
        self.rob = ROB(16)
        # A queue of size 3
        self.commit_queue = Queue(3)

        # RF handle
        self.rf = None

        # CDB handle
        self.cdb = None

        # Dispatcher handle
        self.dispatcher = None


    def step(self):
        """Steps to perform in a cycle:
        1. Check for the RF handle.
        2. Pop from the commit queue.
        3. Commit the instruction by writing to the RF.
        4. Pop from the ROB if the instruction is ready.
        5. Push the instruction to the commit queue.
        All of this happens if everything has space, otherwise if one in the 
        pipeline is full, then the remaining steps will stall.
        """
        # Step 1
        self.check_connections()
        self.cdb.step()
        # print(f"CDB: {self.cdb.buffer_o.full()}")
        cdb_entry = self.cdb.get()

        print(f"Got CDB Entry: {cdb_entry}")

        if cdb_entry:
            self.rob.updateResult(cdb_entry["rd_idx"], cdb_entry["res_value"], cdb_entry["rob_idx"])

        # Step 2
        full = False

        # Check if the commit queue is full
        if self.commit_queue.full():
            full = True

        if not self.commit_queue.empty():
            entry = self.commit_queue.get()
            # Step 3 If the entry is valid, write to the RF
            print(f"Committing Instruction: {entry.instruction} at 0x{entry.instr_pc:08X}")
            if entry.valid:
                self.rf.write(entry.rd_idx, entry.res_value)
        
        if (full):
            # If the commit queue was full, then only this operation is performed
            # at this time, must wait the next cycle
            return

        # Check if ROB is full
        if self.rob.is_full():
            full = True

        # Step 4
        if self.rob.canCommit():
            entry = self.rob.pop()


            # Step 5, TODO could skip this if the instr is not valid
            # print(f"Going to commit {entry.instruction} at 0x{entry.instr_pc:08X} with valid {entry.valid}")
            self.commit_queue.put(entry)
        
        if (full):
            # If the ROB was full, then only this operation is performed
            # at this time, must wait the next cycle
            return

        # End

    def connectRF(self, rf):
        """Connect the RF to the commit unit."""
        self.rf = rf
    
    def connectCDB(self, cdb):
        """Connect the CDB to the commit unit."""
        self.cdb = cdb
    
    def connectDispatcher(self, dispatcher):
        """Connect the dispatcher to the commit unit."""
        self.dispatcher = dispatcher

    def searchOperand(self, rs_idx: int, instr_addr : int) -> int:
        """Search for the operand in the commit stage for forwarding."""
        # Search in the ROB
        operand = self.rob.searchOperand(rs_idx, instr_addr)
        
        # Found
        if (operand is not None):
            return operand
        
        # Search in the commit queue
        for entry in self.commit_queue.queue:
            if entry.rd_idx == rs_idx and entry.valid:
                # Found, return the value
                return entry

        # Not found
        return None
    
    def check_connections(self):
        """Checks wether all the handles are not None."""
        if self.rf is None:
            raise ValueError("RF handle is not connected to the commit unit.")
        
        if self.cdb is None:
            raise ValueError("CDB handle is not connected to the commit unit.")
        
        if self.dispatcher is None:
            raise ValueError("Dispatcher handle is not connected to the commit unit.")
    
    def empty(self) -> bool:
        """Check if the commit unit is empty."""
        return self.rob.is_empty() and self.commit_queue.empty()
