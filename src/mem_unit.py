from exec_unit import ExecUnit
from rs import ReservationStationEntry
from queue import Queue

class MemoryUnit(ExecUnit):
    """Base class for the Load unit and Store unit.
    It inherits from the ExecUnit class. It will be extended
    by Load unit and Store unit classes. It implements the base buffer
    and address calculation logic for both units. 
    The buffer is a reservation station.
    """
    def __init__(self, n_entries: int, reservation_station_t: type[ReservationStationEntry], latency: int = 1, iterative: bool = True) -> None:
        super().__init__(n_entries, reservation_station_t, latency, iterative)


        # Buffer for the requests toward the memory unit
        """It contains a dictionary with:
        - address   : int
        - value     : int
        - read      : bool
        """
        self.address_o = Queue(1)
    
    def execute(self, entry: ReservationStationEntry):
        """Compute the address and return it."""
        return entry.address + entry.offset