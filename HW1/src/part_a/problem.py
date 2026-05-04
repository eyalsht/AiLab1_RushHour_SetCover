from typing import List, Tuple, Optional
from src.part_a.state import State, Vehicle

class RushHourProblem:
    def __init__(self, initial_state: State, target_vehicle_id: str = 'X', heuristic_type: str = 'h1') -> None:
        self.initial_state = initial_state
        self.target_vehicle_id = target_vehicle_id
        self.heuristic_type = heuristic_type

    def is_goal(self, state: State) -> bool:
        target = state.get_vehicle(self.target_vehicle_id)
        if not target:
            return False
        return target.col + target.length >= state.grid_size

    def get_actions(self, state: State) -> List[Tuple[str, int]]:
        actions = []
        grid = self._create_grid(state)
        
        for v in state.vehicles:
            if v.is_horizontal:
                offset = 1
                while v.col + v.length - 1 + offset < state.grid_size and grid[v.row][v.col + v.length - 1 + offset] is None:
                    actions.append((v.id, offset))
                    offset += 1
                offset = 1
                while v.col - offset >= 0 and grid[v.row][v.col - offset] is None:
                    actions.append((v.id, -offset))
                    offset += 1
            else:
                offset = 1
                while v.row + v.length - 1 + offset < state.grid_size and grid[v.row + v.length - 1 + offset][v.col] is None:
                    actions.append((v.id, offset))
                    offset += 1
                offset = 1
                while v.row - offset >= 0 and grid[v.row - offset][v.col] is None:
                    actions.append((v.id, -offset))
                    offset += 1
                    
        return actions

    def get_result(self, state: State, action: Tuple[str, int]) -> State:
        vehicle_id, offset = action
        new_vehicles = []
        for v in state.vehicles:
            if v.id == vehicle_id:
                if v.is_horizontal:
                    new_vehicles.append(Vehicle(v.id, v.is_horizontal, v.length, v.row, v.col + offset))
                else:
                    new_vehicles.append(Vehicle(v.id, v.is_horizontal, v.length, v.row + offset, v.col))
            else:
                new_vehicles.append(v)
        return State(frozenset(new_vehicles), state.grid_size)

    def calculate_heuristic(self, state: State) -> float:
        target = state.get_vehicle(self.target_vehicle_id)
        if not target or self.is_goal(state):
            return 0.0
            
        grid = self._create_grid(state)
        blocking_cars = set()
        
        for c in range(target.col + target.length, state.grid_size):
            if grid[target.row][c] is not None:
                blocking_cars.add(grid[target.row][c])
                
        h1 = len(blocking_cars) + 1  # 1 for the target car to move, plus blocking cars
        
        if self.heuristic_type == 'h1':
            return float(h1)
            
        h2 = h1
        if self.heuristic_type == 'h2':
            for car_id in blocking_cars:
                car = state.get_vehicle(car_id)
                if not car.is_horizontal:
                    # Check if the blocking car is blocked on both sides
                    can_move_up = car.row > 0 and grid[car.row - 1][car.col] is None
                    can_move_down = car.row + car.length < state.grid_size and grid[car.row + car.length][car.col] is None
                    if not can_move_up and not can_move_down:
                        h2 += 1
            return float(h2)
            
        return float(h1)

    def _create_grid(self, state: State) -> List[List[Optional[str]]]:
        grid = [[None for _ in range(state.grid_size)] for _ in range(state.grid_size)]
        for v in state.vehicles:
            for i in range(v.length):
                if v.is_horizontal:
                    grid[v.row][v.col + i] = v.id
                else:
                    grid[v.row + i][v.col] = v.id
        return grid
