import time
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class MetricsTracker:
    execution_time_ms: float = 0.0
    nodes_generated: int = 0
    nodes_expanded: int = 0
    max_tree_depth: int = 0
    min_tree_depth: int = float('inf')
    sum_tree_depth: int = 0
    
    sum_heuristic_value: float = 0.0
    count_heuristic_evals: int = 0
    solution_depth: int = 0
    
    _start_time: float = field(default=0.0, init=False, repr=False)

    def start_timer(self) -> None:
        self._start_time = time.perf_counter()

    def stop_timer(self) -> None:
        if self._start_time > 0:
            elapsed = time.perf_counter() - self._start_time
            self.execution_time_ms = elapsed * 1000.0

    def calculate_ebf(self, total_nodes: int, depth: int, tolerance: float = 0.01) -> float:
        """
        Calculates the Effective Branching Factor (EBF).
        total_nodes = 1 + b + b^2 + ... + b^d
        """
        if depth == 0 or total_nodes <= depth + 1:
            return 1.0
        
        low = 1.0
        high = float(total_nodes)
        
        def polynomial(b: float) -> float:
            if b == 1.0:
                return float(depth + 1)
            return (b ** (depth + 1) - 1) / (b - 1)
            
        while high - low > tolerance:
            mid = (low + high) / 2.0
            if polynomial(mid) < total_nodes:
                low = mid
            else:
                high = mid
        return (low + high) / 2.0

    def increment_generated(self, count: int = 1) -> None:
        self.nodes_generated += count

    def increment_expanded(self) -> None:
        self.nodes_expanded += 1

    def update_depth(self, current_depth: int) -> None:
        if current_depth > self.max_tree_depth:
            self.max_tree_depth = current_depth
        self.sum_tree_depth += current_depth

    def record_dead_end(self, depth: int) -> None:
        if depth < self.min_tree_depth:
            self.min_tree_depth = depth

    def record_heuristic(self, h_value: float) -> None:
        self.sum_heuristic_value += h_value
        self.count_heuristic_evals += 1

    def get_metrics_summary(self) -> Dict[str, Any]:
        ebf = self.calculate_ebf(self.nodes_generated, self.max_tree_depth)
        avg_depth = (self.sum_tree_depth / self.nodes_generated) if self.nodes_generated > 0 else 0
        h_avg = (self.sum_heuristic_value / self.count_heuristic_evals) if self.count_heuristic_evals > 0 else 0
        penetrance = (self.solution_depth / self.nodes_expanded) if self.nodes_expanded > 0 else 0
        min_depth = self.min_tree_depth if self.min_tree_depth != float('inf') else 0
        
        return {
            "Time(ms)": round(self.execution_time_ms, 2),
            "N": self.nodes_expanded,
            "d/N": round(penetrance, 4),
            "EBF": round(ebf, 3),
            "Havg": round(h_avg, 3),
            "Min Depth": min_depth,
            "Avg Depth": round(avg_depth, 2),
            "Max Depth": self.max_tree_depth
        }
