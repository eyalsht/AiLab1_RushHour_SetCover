import time
from src.part_b.problem import SetCoverProblem

class GreedySetCover:
    def solve(self, problem: SetCoverProblem):
        start_time = time.perf_counter()
        
        uncovered_elements = set(range(problem.m))
        selected_sets = set()
        total_cost = 0.0
        
        set_covers = [set() for _ in range(problem.n)]
        for element_idx, covering_sets in enumerate(problem.covers):
            for set_idx in covering_sets:
                set_covers[set_idx].add(element_idx)
                
        while uncovered_elements:
            best_set = -1
            best_ratio = float('inf')
            best_coverage = set()
            
            for set_idx in range(problem.n):
                if set_idx in selected_sets:
                    continue
                    
                coverage = set_covers[set_idx].intersection(uncovered_elements)
                if not coverage:
                    continue
                    
                ratio = problem.costs[set_idx] / len(coverage)
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_set = set_idx
                    best_coverage = coverage
                    
            if best_set == -1:
                break
                
            selected_sets.add(best_set)
            uncovered_elements -= best_coverage
            total_cost += problem.costs[best_set]
            
        elapsed = (time.perf_counter() - start_time) * 1000.0
        return total_cost, selected_sets, elapsed
