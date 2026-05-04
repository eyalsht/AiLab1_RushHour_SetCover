import random
from typing import Optional

from src.part_a.state import State, Vehicle
from src.part_a.problem import RushHourProblem
from src.part_a.search import AStarSearch

def _state_to_string(state: State) -> str:
    grid = [['.' for _ in range(state.grid_size)] for _ in range(state.grid_size)]
    for v in state.vehicles:
        for i in range(v.length):
            if v.is_horizontal:
                grid[v.row][v.col + i] = v.id
            else:
                grid[v.row + i][v.col] = v.id
    return ''.join(''.join(row) for row in grid)

def generate_puzzle(target_depth: int, max_attempts: int = 1000) -> Optional[str]:
    """
    Randomly generates a valid Rush Hour board that has a solution depth of `target_depth`.
    Returns the 36-character string representation, or None if unsuccessful.
    """
    for _ in range(max_attempts):
        vehicles = []
        # Always place target car 'X'
        row_x = 2
        col_x = random.randint(0, 3)
        vehicles.append(Vehicle('X', True, 2, row_x, col_x))
        
        # Grid to track occupied spaces
        grid = [['.' for _ in range(6)] for _ in range(6)]
        grid[row_x][col_x] = 'X'
        grid[row_x][col_x+1] = 'X'
        
        # Try adding 5-10 random vehicles
        num_vehicles = random.randint(5, 10)
        available_ids = "ABCDEFGHIJKLMOPQRSTUVWYZ"
        
        v_idx = 0
        failures = 0
        while v_idx < num_vehicles and failures < 20:
            is_horiz = random.choice([True, False])
            length = random.choice([2, 3])
            row = random.randint(0, 5)
            col = random.randint(0, 5)
            
            # Check bounds and overlaps
            valid = True
            if is_horiz:
                if col + length > 6:
                    valid = False
                else:
                    for i in range(length):
                        if grid[row][col+i] != '.':
                            valid = False
            else:
                if row + length > 6:
                    valid = False
                else:
                    for i in range(length):
                        if grid[row+i][col] != '.':
                            valid = False
                            
            if valid:
                v_id = available_ids[v_idx % len(available_ids)]
                vehicles.append(Vehicle(v_id, is_horiz, length, row, col))
                if is_horiz:
                    for i in range(length):
                        grid[row][col+i] = v_id
                else:
                    for i in range(length):
                        grid[row+i][col] = v_id
                v_idx += 1
            else:
                failures += 1
                
        initial_state = State(frozenset(vehicles))
        problem = RushHourProblem(initial_state, heuristic_type='h1')
        algo = AStarSearch()
        
        # Time limit of 2 seconds for generation attempts
        solution = algo.search(problem, time_limit_ms=2000.0)
        
        if solution is not None and solution.depth == target_depth:
            return _state_to_string(initial_state)
            
    return None
