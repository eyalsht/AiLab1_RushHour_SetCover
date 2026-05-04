import typing

class SetCoverProblem:
    def __init__(self, m: int, n: int, costs: list[float], covers: list[list[int]]):
        self.m = m
        self.n = n
        self.costs = costs
        self.covers = covers

    @classmethod
    def from_file(cls, filepath: str) -> 'SetCoverProblem':
        with open(filepath, 'r') as f:
            tokens = f.read().split()
        
        if not tokens:
            raise ValueError("Empty file")
            
        iterator = iter(tokens)
        
        m = int(next(iterator))
        n = int(next(iterator))
        
        costs = []
        for _ in range(n):
            costs.append(float(next(iterator)))
            
        covers = []
        sets_to_elements = [[] for _ in range(n)]
        
        for e in range(m):
            num_sets = int(next(iterator))
            covered_by = []
            for _ in range(num_sets):
                s_idx = int(next(iterator)) - 1
                covered_by.append(s_idx)
                sets_to_elements[s_idx].append(e)
            covers.append(covered_by)
            
        prob = cls(m, n, costs, covers)
        prob.sets_to_elements = sets_to_elements
        return prob
