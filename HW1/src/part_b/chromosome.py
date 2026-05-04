from dataclasses import dataclass
from typing import List
from src.part_b.problem import SetCoverProblem

@dataclass
class Chromosome:
    genes: List[int]
    fitness: float = float('inf')
    is_valid: bool = False
    cost: float = float('inf')

    def evaluate(self, problem: SetCoverProblem) -> None:
        # Track covered elements
        covered_counts = [0] * problem.m
        selected_sets = []
        
        for i, val in enumerate(self.genes):
            if val == 1:
                selected_sets.append(i)
                for e in problem.sets_to_elements[i]:
                    covered_counts[e] += 1
                    
        # 1. Repair phase: Greedily cover any uncovered elements
        uncovered = [e for e, count in enumerate(covered_counts) if count == 0]
        while uncovered:
            best_set = -1
            best_ratio = float('inf')
            
            # Find the best set to cover the remaining uncovered elements
            for s_idx in range(problem.n):
                if self.genes[s_idx] == 1:
                    continue
                
                new_covered = 0
                for e in problem.sets_to_elements[s_idx]:
                    if covered_counts[e] == 0:
                        new_covered += 1
                        
                if new_covered > 0:
                    ratio = problem.costs[s_idx] / new_covered
                    if ratio < best_ratio:
                        best_ratio = ratio
                        best_set = s_idx
            
            if best_set != -1:
                self.genes[best_set] = 1
                selected_sets.append(best_set)
                for e in problem.sets_to_elements[best_set]:
                    if covered_counts[e] == 0:
                        uncovered.remove(e)
                    covered_counts[e] += 1
            else:
                break # Should not happen unless problem is unsolvable
                
        # 2. Exploitation (Redundancy Removal) phase
        # Iterate over selected sets and turn them off if their elements are fully covered by other sets
        # Process in descending order of cost to remove expensive redundant sets first
        selected_sets.sort(key=lambda idx: problem.costs[idx], reverse=True)
        
        for s_idx in selected_sets:
            # Check if redundant
            is_redundant = True
            for e in problem.sets_to_elements[s_idx]:
                if covered_counts[e] <= 1:
                    is_redundant = False
                    break
            
            if is_redundant:
                self.genes[s_idx] = 0
                for e in problem.sets_to_elements[s_idx]:
                    covered_counts[e] -= 1
                    
        # Calculate final cost
        total_cost = 0.0
        for i, val in enumerate(self.genes):
            if val == 1:
                total_cost += problem.costs[i]
                
        self.is_valid = True
        self.cost = total_cost
        self.fitness = total_cost
