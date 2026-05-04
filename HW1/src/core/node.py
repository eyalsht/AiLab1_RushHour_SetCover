from dataclasses import dataclass, field
from typing import Optional, Any, List

@dataclass
class Node:
    state: Any
    parent: Optional['Node'] = None
    action: Any = None
    path_cost: float = 0.0
    depth: int = 0
    heuristic_value: float = field(default=0.0, compare=False)

    def __lt__(self, other: 'Node') -> bool:
        """
        Comparison strictly based on total estimated cost (f = g + h) for A* priority queue.
        """
        return (self.path_cost + self.heuristic_value) < (other.path_cost + other.heuristic_value)

    def get_solution_path(self) -> List[Any]:
        """
        Traces back the formulation of the solution from this node to the root.
        """
        path = []
        current = self
        while current is not None:
            if current.action is not None:
                path.append(current.action)
            current = current.parent
        return path[::-1]
