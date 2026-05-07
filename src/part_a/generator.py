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


def _is_valid_board(state: State) -> bool:
    grid = [['.' for _ in range(state.grid_size)] for _ in range(state.grid_size)]
    for v in state.vehicles:
        for i in range(v.length):
            if v.is_horizontal:
                grid[v.row][v.col + i] = v.id
            else:
                grid[v.row + i][v.col] = v.id

    x_vehicle = state.get_vehicle('X')
    if x_vehicle is None:
        return False
    x_right_end = x_vehicle.col + x_vehicle.length

    blockers = []
    for col in range(x_right_end, 6):
        cell = grid[2][col]
        if cell != '.' and cell != 'X':
            blocker_v = state.get_vehicle(cell)
            if blocker_v and not blocker_v.is_horizontal:
                blockers.append(blocker_v)

    if not (1 <= len(blockers) <= 3):
        return False

    occupied = sum(1 for row in grid for cell in row if cell != '.')
    if occupied < 12:
        return False

    has_dependent = False
    for v in blockers:
        top_row = v.row - 1
        bot_row = v.row + v.length
        top_blocked = (top_row < 0) or (grid[top_row][v.col] != '.')
        bot_blocked = (bot_row >= 6) or (grid[bot_row][v.col] != '.')
        if top_blocked and bot_blocked:
            has_dependent = True
            break

    return has_dependent


def generate_puzzle(target_depth: int, max_attempts: int = 1000) -> Optional[str]:
    """
    Randomly generates a valid Rush Hour board that has a solution depth of `target_depth`.
    Returns the 36-character string representation, or None if unsuccessful.
    Enforces: 1-3 vertical blockers in X's exit lane, min 12 occupied cells,
    at least one dependent (stuck) blocker.
    """
    for _ in range(max_attempts):
        vehicles = []
        row_x = 2
        col_x = random.randint(0, 3)
        vehicles.append(Vehicle('X', True, 2, row_x, col_x))

        grid = [['.' for _ in range(6)] for _ in range(6)]
        grid[row_x][col_x] = 'X'
        grid[row_x][col_x + 1] = 'X'

        num_vehicles = random.randint(7, 12)
        available_ids = "ABCDEFGHIJKLMOPQRSTUVWYZ"

        v_idx = 0
        failures = 0
        while v_idx < num_vehicles and failures < 30:
            is_horiz = random.choice([True, False])
            length = random.choice([2, 3])
            row = random.randint(0, 5)
            col = random.randint(0, 5)

            valid = True
            if is_horiz:
                if col + length > 6:
                    valid = False
                else:
                    for i in range(length):
                        if grid[row][col + i] != '.':
                            valid = False
            else:
                if row + length > 6:
                    valid = False
                else:
                    for i in range(length):
                        if grid[row + i][col] != '.':
                            valid = False

            if valid:
                v_id = available_ids[v_idx % len(available_ids)]
                vehicles.append(Vehicle(v_id, is_horiz, length, row, col))
                if is_horiz:
                    for i in range(length):
                        grid[row][col + i] = v_id
                else:
                    for i in range(length):
                        grid[row + i][col] = v_id
                v_idx += 1
            else:
                failures += 1

        initial_state = State(frozenset(vehicles))

        if not _is_valid_board(initial_state):
            continue

        problem = RushHourProblem(initial_state, heuristic_type='h1')
        algo = AStarSearch()
        solution = algo.search(problem, time_limit_ms=2000.0)

        if solution is not None and solution.depth == target_depth:
            return _state_to_string(initial_state)

    return None
