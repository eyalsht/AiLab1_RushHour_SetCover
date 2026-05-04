from dataclasses import dataclass
from typing import FrozenSet, Optional

@dataclass(frozen=True)
class Vehicle:
    id: str
    is_horizontal: bool
    length: int
    row: int
    col: int

@dataclass(frozen=True)
class State:
    """
    Represents a specific board state for the Rush Hour puzzle.
    Uses a frozenset of vehicles to allow correct hashing and equality tracking.
    """
    vehicles: FrozenSet[Vehicle]
    grid_size: int = 6

    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        for v in self.vehicles:
            if v.id == vehicle_id:
                return v
        return None
