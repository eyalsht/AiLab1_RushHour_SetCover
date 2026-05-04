from abc import ABC, abstractmethod
from typing import Optional, Any
from src.core.node import Node
from src.core.metrics import MetricsTracker

class SearchAlgorithm(ABC):
    """
    Abstract base class for all search algorithms.
    Enforces the implementation of the search logic and standardizes metric tracking.
    """

    def __init__(self) -> None:
        self.metrics = MetricsTracker()

    @abstractmethod
    def search(self, problem: Any) -> Optional[Node]:
        """
        Executes the search on a given problem.
        
        Args:
            problem: The specific problem formulation to solve.

        Returns:
            The goal Node if a solution is found, None otherwise.
        """
        pass
