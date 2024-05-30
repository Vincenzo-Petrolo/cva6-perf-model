import re
from queue import Queue

class InstrQueue(object):
    """
    Instruction Queue, reads a Spike disassembly file and stores the instructions,
    so that the dispatcher can issue them to the execution units.
    
    """
    def __init__(self, filename : str) -> None:

        # Infinite instruction queue
        self.queue = Queue(maxsize=-1)

        # Parse the file to fill the queue
        self.parseFile(filename)

    
    def get(self) -> list:
        """Get n instructions from the queue."""
        return self.queue.get()


    def parseFile(self, filename : str):
        """Parse the file and store the instructions in the queue."""

        with open(filename) as f:
            for i, line in enumerate(f):
                """Get line, address, hex code, mnemo"""
                address, hex_code, mnemonic = self._parseDisassemblyLine(line)

                # Skip if what we got is not an instruction
                if address is None:
                    continue
                
                instr = {
                    "line" : i,
                    "address" : address,
                    "hex_code" : hex_code,
                    "mnemo" : mnemonic
                }

                self.queue.put(instr)
            

    def _parseDisassemblyLine(line):
        """
        Parse a line from the disassembly file and extract the address, hex code,
        """
        pattern = re.compile(r'^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]+)\s+(.+)$')
        
        # Search the pattern in the given line
        match = pattern.match(line)
        if match:
            # Extract the address, hex code, and mnemonic
            address = match.group(1)
            hex_code = match.group(2)
            mnemonic = match.group(3).strip()
            return address, hex_code, mnemonic
        else:
            return None, None, None
    

