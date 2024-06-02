from exec_unit import ExecUnit
from rs import ReservationStationEntry
from queue import Queue

class MemoryUnit(ExecUnit):
    """Base class for the Load unit and Store unit.
    It inherits from the ExecUnit class. It will be extended
    by Load unit and Store unit classes. It implements the base address 
    calculation logic for both units. 
    """
    def __init__(self, n_entries: int, reservation_station_t: type[ReservationStationEntry], latency: int = 1, iterative: bool = True) -> None:
        super().__init__(n_entries, reservation_station_t, latency, iterative)
    
    def execute(self, entry: ReservationStationEntry):
        """Compute the address and return it."""
        return entry.address + entry.offset