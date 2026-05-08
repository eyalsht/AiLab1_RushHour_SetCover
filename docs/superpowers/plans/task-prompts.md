# Task Prompts — AI Lab 1 Completion

Each task below is a self-contained unit of work that should be implemented and merged as its own pull request to the `main` branch on GitHub. The repo is at `c:\Users\אייל. ש\Documents\HUP\AI lab`.

Before each task: create a feature branch named `task/<N>-<slug>`, implement, commit, push, and open a PR with `gh pr create`.

---

## Task 1 — Part A: Solution file + stats summary + CSV

**Branch:** `task/1-solution-file-and-stats`

**Prompt:**

You are working in the repository at `c:\Users\אייל. ש\Documents\HUP\AI lab`.

The assignment requires that after running all 40 Rush Hour puzzles in batch mode, the program:
1. Writes a solution file (one line per puzzle — the formatted move string or the word `FAILED`).
2. Prints a statistics summary (averages of N, d/N, Time, EBF, Havg, Min/Avg/Max Depth) for the solved puzzles.
3. Saves the full per-puzzle results to a CSV file.

Currently `run_batch` in `main.py` only prints a table to stdout and does nothing else.

**What to change — `main.py`, function `run_batch` (lines 104–131):**

Replace the function with this implementation:

```python
def run_batch(args):
    puzzles = parse_all_board_file(args.board_file)
    print(f"{'Problem':<8} | {'Heuristic':<10} | {'N':<6} | {'d/N':<8} | {'Time(ms)':<10} | {'Success':<8} | {'EBF':<6} | {'Havg':<6} | {'Min':<4} | {'Avg':<6} | {'Max':<4}")
    print("-" * 105)

    success_count = 0
    time_limit = args.time_limit if args.time_limit else None

    algo_tag = args.algorithm
    solutions_file = os.path.join("results", f"solutions_{algo_tag}_{args.heuristic}.txt")
    os.makedirs("results", exist_ok=True)

    rows = []
    solution_lines = []

    for i, puzzle_str in enumerate(puzzles):
        state = parse_rush_hour_string(puzzle_str)
        problem = RushHourProblem(state, heuristic_type=args.heuristic)

        if args.algorithm == 'bfs':
            algo = BreadthFirstSearch()
        else:
            algo = AStarSearch()

        solution = algo.search(problem, time_limit_ms=time_limit)
        m = algo.metrics.get_metrics_summary()

        success_str = "Y" if solution else "N"
        if solution:
            success_count += 1
            path = solution.get_solution_path()
            solution_lines.append(format_solution(path, state))
        else:
            solution_lines.append("FAILED")

        rows.append({
            'Problem': i + 1,
            'Heuristic': args.heuristic,
            'Algorithm': args.algorithm,
            'N': m['N'],
            'd/N': m['d/N'],
            'Time(ms)': m['Time(ms)'],
            'Success': success_str,
            'EBF': m['EBF'],
            'Havg': m['Havg'],
            'Min Depth': m['Min Depth'],
            'Avg Depth': m['Avg Depth'],
            'Max Depth': m['Max Depth'],
        })

        print(f"{i+1:<8} | {args.heuristic:<10} | {m['N']:<6} | {m['d/N']:<8} | {m['Time(ms)']:<10.2f} | {success_str:<8} | {m['EBF']:<6} | {m['Havg']:<6} | {m['Min Depth']:<4} | {m['Avg Depth']:<6} | {m['Max Depth']:<4}")

    print("-" * 105)
    print(f"Total Successes: {success_count}/{len(puzzles)}")

    with open(solutions_file, 'w') as f:
        for line in solution_lines:
            f.write(line + "\n")
    print(f"Solutions written to: {solutions_file}")

    df = pd.DataFrame(rows)
    solved = df[df['Success'] == 'Y']
    print(f"\n--- Statistics Summary ({args.heuristic}, {args.algorithm}) ---")
    if not solved.empty:
        for col in ['N', 'd/N', 'Time(ms)', 'EBF', 'Havg', 'Min Depth', 'Avg Depth', 'Max Depth']:
            print(f"  Avg {col}: {solved[col].mean():.4f}")

    csv_file = os.path.join("results", f"batch_results_{algo_tag}_{args.heuristic}.csv")
    df.to_csv(csv_file, index=False)
    print(f"Batch results saved to: {csv_file}")
```

**Steps:**
1. Create branch: `git checkout -b task/1-solution-file-and-stats`
2. Apply the code change to `main.py`.
3. Verify: `python main.py part_a --board_file data/rh.txt --batch --algorithm astar --heuristic h1 --time_limit 5000` — confirm `results/solutions_astar_h1.txt` is created with 40 lines.
4. Commit: `git add main.py && git commit -m "feat: batch writes solution file, stats summary, and CSV"`
5. Push and open PR: `git push -u origin task/1-solution-file-and-stats && gh pr create --title "Task 1: solution file, stats summary, CSV in run_batch" --body "Implements mandatory assignment output: solution file per run, per-heuristic statistics summary, and CSV export."`

---

## Task 2 — Part A: BFS vs A* comparison (`--compare` flag)

**Branch:** `task/2-bfs-vs-astar-compare`

**Prompt:**

You are working in the repository at `c:\Users\אייל. ש\Documents\HUP\AI lab`.

The assignment requires comparing the uninformed algorithm (BFS) against the informed one (A*) under the same time limit, showing how many problems each solved, average N, and average time.

Currently there is no such comparison mode. You need to add a `--compare` flag to the `part_a` subcommand and a `run_comparison` function.

**What to add to `main.py`:**

1. Add this function before `run_part_a`:

```python
def run_comparison(args):
    """Run BFS and A* on all puzzles and print a side-by-side comparison."""
    puzzles = parse_all_board_file(args.board_file)
    time_limit = args.time_limit if args.time_limit else 5000.0
    heuristic = args.heuristic

    print(f"\n=== BFS vs A* Comparison (time_limit={time_limit}ms, A* heuristic={heuristic}) ===\n")
    print(f"{'#':<4} | {'BFS_N':<8} | {'BFS_d':<6} | {'BFS_ms':<8} | {'BFS_ok':<6} | "
          f"{'AStar_N':<8} | {'AStar_d':<6} | {'AStar_ms':<8} | {'AStar_ok':<6} | "
          f"{'BFS_len':<8} | {'AStar_len':<10}")
    print("-" * 110)

    rows = []
    for i, puzzle_str in enumerate(puzzles):
        state = parse_rush_hour_string(puzzle_str)

        bfs = BreadthFirstSearch()
        bfs_sol = bfs.search(RushHourProblem(state, heuristic_type='h1'), time_limit_ms=time_limit)
        bm = bfs.metrics.get_metrics_summary()

        astar = AStarSearch()
        astar_sol = astar.search(RushHourProblem(state, heuristic_type=heuristic), time_limit_ms=time_limit)
        am = astar.metrics.get_metrics_summary()

        bfs_len = len(bfs_sol.get_solution_path()) if bfs_sol else -1
        astar_len = len(astar_sol.get_solution_path()) if astar_sol else -1

        print(f"{i+1:<4} | {bm['N']:<8} | {bm['d/N']:<6} | {bm['Time(ms)']:<8.1f} | {'Y' if bfs_sol else 'N':<6} | "
              f"{am['N']:<8} | {am['d/N']:<6} | {am['Time(ms)']:<8.1f} | {'Y' if astar_sol else 'N':<6} | "
              f"{bfs_len:<8} | {astar_len:<10}")

        rows.append({
            'Problem': i + 1,
            'BFS_N': bm['N'], 'BFS_dN': bm['d/N'], 'BFS_ms': bm['Time(ms)'],
            'BFS_ok': 1 if bfs_sol else 0, 'BFS_sol_len': bfs_len,
            'AStar_N': am['N'], 'AStar_dN': am['d/N'], 'AStar_ms': am['Time(ms)'],
            'AStar_ok': 1 if astar_sol else 0, 'AStar_sol_len': astar_len,
        })

    df = pd.DataFrame(rows)
    print("\n--- Summary ---")
    print(f"BFS  solved: {df['BFS_ok'].sum()}/40   avg N={df[df['BFS_ok']==1]['BFS_N'].mean():.0f}   avg ms={df[df['BFS_ok']==1]['BFS_ms'].mean():.1f}")
    print(f"A*   solved: {df['AStar_ok'].sum()}/40  avg N={df[df['AStar_ok']==1]['AStar_N'].mean():.0f}  avg ms={df[df['AStar_ok']==1]['AStar_ms'].mean():.1f}")

    os.makedirs("results", exist_ok=True)
    df.to_csv("results/bfs_vs_astar.csv", index=False)
    print("Saved to results/bfs_vs_astar.csv")
```

2. In `main()`, add the flag to `part_a_parser` (after the `--batch` line):
```python
part_a_parser.add_argument('--compare', action='store_true', help='Compare BFS vs A* on all puzzles')
```

3. In `run_part_a`, add before `if args.generate_depth:`:
```python
    if args.compare:
        run_comparison(args)
        return
```

**Steps:**
1. Create branch: `git checkout -b task/2-bfs-vs-astar-compare`
2. Apply the three changes above to `main.py`.
3. Verify: `python main.py part_a --board_file data/rh.txt --compare --heuristic h1 --time_limit 5000` — confirm table and summary print without errors, CSV saved.
4. Commit: `git add main.py && git commit -m "feat: --compare flag for BFS vs A* side-by-side analysis"`
5. Push and open PR: `git push -u origin task/2-bfs-vs-astar-compare && gh pr create --title "Task 2: --compare flag BFS vs A*" --body "Adds --compare flag to part_a that runs both algorithms on all 40 puzzles under the same time limit and prints a side-by-side table with summary statistics."`

---

## Task 3 — Part A: Category breakdown + given-solution comparison

**Branch:** `task/3-category-and-given-solutions`

**Prompt:**

You are working in the repository at `c:\Users\אייל. ש\Documents\HUP\AI lab`.

This task depends on Task 2 being merged first (the `run_comparison` function must exist in `main.py`). Base this branch off `main` after Task 2 is merged.

The assignment requires:
- Comparing algorithm performance across difficulty categories (Beginner 1–10, Intermediate 11–20, Advanced 21–30, Expert 31–40).
- Comparing your solution lengths against the provided solutions in `data/rh.txt` (the `Soln:` lines after `--- end RH-input ---`).

**What to add to `main.py`:**

1. Add `parse_given_solutions` after `parse_all_board_file`:

```python
def parse_given_solutions(filepath: str) -> list:
    """Parse the Soln: lines from rh.txt after --- end RH-input ---."""
    solutions = []
    in_solutions = False
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '--- end RH-input ---':
                in_solutions = True
                continue
            if in_solutions and line.startswith('Soln:'):
                soln_str = line[len('Soln:'):].strip().rstrip('.')
                tokens = [t for t in soln_str.split() if t != '.']
                solutions.append(len(tokens))
    return solutions
```

2. At the end of `run_comparison`, replace `df.to_csv(...)` and the final print with:

```python
    # Category labels
    def category(n):
        if n <= 10: return 'Beginner'
        elif n <= 20: return 'Intermediate'
        elif n <= 30: return 'Advanced'
        return 'Expert'
    df['Category'] = df['Problem'].apply(category)

    # Given solution lengths from rh.txt
    given = parse_given_solutions(args.board_file)
    df['Given_sol_len'] = given if len(given) == len(df) else -1

    print("\n--- Category Breakdown (A*) ---")
    cat_df = df[df['AStar_ok'] == 1].groupby('Category').agg(
        Solved=('AStar_ok', 'sum'),
        Avg_N=('AStar_N', 'mean'),
        Avg_ms=('AStar_ms', 'mean'),
        Avg_sol_len=('AStar_sol_len', 'mean'),
    )
    print(cat_df.to_string())

    print("\n--- Solution Length: Ours (A*) vs Given ---")
    comp = df[df['AStar_ok'] == 1][['Problem', 'Category', 'AStar_sol_len', 'Given_sol_len']].copy()
    comp['diff'] = comp['AStar_sol_len'] - comp['Given_sol_len']
    print(comp.to_string(index=False))
    shorter = (comp['diff'] < 0).sum()
    equal = (comp['diff'] == 0).sum()
    longer = (comp['diff'] > 0).sum()
    print(f"\nOurs shorter: {shorter}  Equal: {equal}  Longer: {longer}")

    os.makedirs("results", exist_ok=True)
    df.to_csv("results/bfs_vs_astar.csv", index=False)
    print("Saved to results/bfs_vs_astar.csv")
```

**Steps:**
1. Create branch (from updated main): `git checkout -b task/3-category-and-given-solutions`
2. Apply both changes to `main.py`.
3. Verify: `python main.py part_a --board_file data/rh.txt --compare --heuristic h1 --time_limit 5000` — confirm "Category Breakdown" and "Solution Length" sections appear.
4. Commit: `git add main.py && git commit -m "feat: compare shows category breakdown and given-solution length comparison"`
5. Push and open PR: `git push -u origin task/3-category-and-given-solutions && gh pr create --title "Task 3: category breakdown and given-solution comparison" --body "Extends --compare output with performance grouped by difficulty category and a table comparing our solution lengths against the reference solutions in rh.txt."`

---

## Task 4 — Part A: Generator validity checks

**Branch:** `task/4-generator-validity`

**Prompt:**

You are working in the repository at `c:\Users\אייל. ש\Documents\HUP\AI lab`.

The puzzle generator in `src/part_a/generator.py` currently places vehicles randomly without enforcing the assignment constraints:
- At least 1 vehicle blocking X's path to the exit.
- Between 1 and 3 vertical blockers in the exit lane.
- Minimum board occupancy of 12 cells.
- At least one blocker that cannot move directly (both ends blocked — "dependent" blocker).

**Replace `src/part_a/generator.py` entirely** with:

```python
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
```

**Steps:**
1. Create branch: `git checkout -b task/4-generator-validity`
2. Replace `src/part_a/generator.py` with the code above.
3. Verify: `python main.py part_a --generate_depth 5` — runs without error (may print "Failed" if unlucky — that's OK, no crash).
4. Commit: `git add src/part_a/generator.py && git commit -m "feat: generator enforces blocker count, occupancy, and dependency constraints"`
5. Push and open PR: `git push -u origin task/4-generator-validity && gh pr create --title "Task 4: generator validity constraints" --body "Adds _is_valid_board check to generate_puzzle: enforces 1-3 vertical blockers in exit lane, min 12 occupied cells, and at least one dependent blocker that cannot move directly."`

---

## Task 5 — Part B: GA early stopping

**Branch:** `task/5-ga-early-stopping`

**Prompt:**

You are working in the repository at `c:\Users\אייל. ש\Documents\HUP\AI lab`.

The assignment requires multiple stopping conditions for the GA. Currently `src/part_b/ga_engine.py` only stops after a fixed number of generations (`generations=200`). Add two more:
1. **Stagnation**: stop if `best_fitness` hasn't improved for `stagnation_limit` consecutive generations (default 30).
2. **Entropy convergence**: stop if population entropy drops below `entropy_threshold` (default 0.05), meaning the population has converged structurally.

**Changes to `src/part_b/ga_engine.py`:**

1. Change the `__init__` signature to add the two new parameters (keep all existing defaults):

```python
def __init__(self, problem: SetCoverProblem, seed: int = 42,
             pop_size: int = 300, mutation_rate: float = 0.05,
             crossover_rate: float = 0.8, generations: int = 200,
             selection_method: str = 'tournament',
             stagnation_limit: int = 30, entropy_threshold: float = 0.05):
    self.problem = problem
    self.pop_size = pop_size
    self.mutation_rate = mutation_rate
    self.crossover_rate = crossover_rate
    self.generations = generations
    self.selection_method = selection_method
    self.stagnation_limit = stagnation_limit
    self.entropy_threshold = entropy_threshold

    self.random = random.Random(seed)
    self.population: List[Chromosome] = []
    self.history: List[Dict[str, Any]] = []
```

2. Replace the `run` method:

```python
def run(self) -> Chromosome:
    start_time = time.perf_counter()
    self.initialize_population()
    self.record_metrics(0, start_time)

    best_fitness = float('inf')
    stagnation_counter = 0
    stop_reason = f"max_generations ({self.generations})"

    for gen in range(1, self.generations + 1):
        new_population = []
        self.population.sort(key=lambda c: c.fitness)

        esize = max(1, int(self.pop_size * 0.1))
        new_population.extend([Chromosome(list(c.genes)) for c in self.population[:esize]])

        while len(new_population) < self.pop_size:
            p1 = self.select()
            p2 = self.select()
            c1, c2 = self.crossover(p1, p2)
            self.mutate(c1)
            self.mutate(c2)
            new_population.extend([c1, c2])

        new_population = new_population[:self.pop_size]
        for c in new_population:
            c.evaluate(self.problem)

        self.population = new_population
        self.record_metrics(gen, start_time)

        current_best = self.history[-1]['best_fitness']
        current_entropy = self.history[-1]['entropy']

        if current_best < best_fitness:
            best_fitness = current_best
            stagnation_counter = 0
        else:
            stagnation_counter += 1

        if stagnation_counter >= self.stagnation_limit:
            stop_reason = f"stagnation ({self.stagnation_limit} gens no improvement)"
            break

        if current_entropy < self.entropy_threshold:
            stop_reason = f"entropy_convergence (entropy={current_entropy:.4f})"
            break

    self.population.sort(key=lambda c: c.fitness)
    self.history[-1]['stop_reason'] = stop_reason
    return self.population[0]
```

**Steps:**
1. Create branch: `git checkout -b task/5-ga-early-stopping`
2. Apply both changes to `src/part_b/ga_engine.py`.
3. Verify: `python main.py part_b --dataset data/setcover/scp41.txt` — runs and terminates without error.
4. Commit: `git add src/part_b/ga_engine.py && git commit -m "feat: GA early stopping on stagnation and entropy convergence"`
5. Push and open PR: `git push -u origin task/5-ga-early-stopping && gh pr create --title "Task 5: GA early stopping (stagnation + entropy)" --body "Adds two stopping conditions to GAEngine.run(): stagnation_limit (default 30 gens without improvement) and entropy_threshold (default 0.05). Stops whichever triggers first. stop_reason is recorded in history."`

---

## Task 6 — Part B: Optimal values, gap%, and parameter sensitivity plot

**Branch:** `task/6-optimal-gap-sensitivity`

**Prompt:**

You are working in the repository at `c:\Users\אייל. ש\Documents\HUP\AI lab`.

The assignment requires comparing GA results against known optimal values from OR-Library. Currently `run_batch_part_b` in `main.py` has no gap column and never calls `Visualizer.plot_parameter_sensitivity`.

**Changes to `main.py`:**

1. Add this constant before `run_batch_part_b` (around line 177):

```python
OPTIMAL_VALUES = {
    'scp41.txt': 429, 'scp42.txt': 512, 'scp43.txt': 516, 'scp44.txt': 494,
    'scp51.txt': 253, 'scp52.txt': 302, 'scp53.txt': 226,
    'scpa1.txt': 253, 'scpa2.txt': 252, 'scpa3.txt': 232,
}
```

2. Replace `run_batch_part_b` entirely:

```python
def run_batch_part_b(args):
    datasets = ['scp41.txt', 'scp42.txt', 'scp43.txt', 'scp44.txt',
                'scp51.txt', 'scp52.txt', 'scp53.txt',
                'scpa1.txt', 'scpa2.txt', 'scpa3.txt']
    seeds = [42, 123, 999, 2026, 7]
    configs = {
        'Crossover Only': {'mut_rate': 0.0, 'cx_rate': 0.8},
        'Mutation Only': {'mut_rate': 0.05, 'cx_rate': 0.0},
        'Both': {'mut_rate': 0.05, 'cx_rate': 0.8}
    }

    results = []
    base_dir = 'data/setcover'

    print(f"Running Part B Batch Experiments on {len(datasets)} datasets...")

    for ds in datasets:
        filepath = os.path.join(base_dir, ds)
        if not os.path.exists(filepath):
            print(f"Warning: Dataset {filepath} not found. Skipping.")
            continue

        print(f"\nProcessing {ds}...")
        problem = SetCoverProblem.from_file(filepath)
        optimal = OPTIMAL_VALUES.get(ds)

        greedy = GreedySetCover()
        greedy_cost, _, greedy_time = greedy.solve(problem)
        greedy_gap = round((greedy_cost - optimal) / optimal * 100, 2) if optimal else None
        results.append({
            'Dataset': ds, 'Config': 'Greedy', 'Seed': 'N/A',
            'Valid': True, 'Cost': greedy_cost, 'Time(ms)': greedy_time,
            'Generations': 0, 'Optimal': optimal, 'Gap(%)': greedy_gap
        })

        for config_name, params in configs.items():
            for seed in seeds:
                engine = GAEngine(
                    problem=problem, seed=seed,
                    pop_size=300, mutation_rate=params['mut_rate'],
                    crossover_rate=params['cx_rate'], generations=200,
                    selection_method='tournament'
                )
                best_chrom = engine.run()
                algo_time = engine.history[-1]['elapsed_ms']
                actual_gens = engine.history[-1]['generation']
                cost = best_chrom.cost
                gap = round((cost - optimal) / optimal * 100, 2) if optimal and best_chrom.is_valid else None
                results.append({
                    'Dataset': ds, 'Config': config_name, 'Seed': seed,
                    'Valid': best_chrom.is_valid, 'Cost': cost,
                    'Time(ms)': algo_time, 'Generations': actual_gens,
                    'Optimal': optimal, 'Gap(%)': gap
                })

    df = pd.DataFrame(results)
    os.makedirs('results', exist_ok=True)
    df.to_csv('results/part_b_batch_results.csv', index=False)

    agg_df = df[df['Valid'] == True].groupby(['Dataset', 'Config']).agg(
        Cost_mean=('Cost', 'mean'),
        Cost_min=('Cost', 'min'),
        Cost_std=('Cost', 'std'),
        Time_mean=('Time(ms)', 'mean'),
        Gap_mean=('Gap(%)', 'mean'),
        Gens_mean=('Generations', 'mean'),
    ).reset_index()

    print("\n--- Aggregated Results ---")
    print(agg_df.to_string())
    agg_df.to_csv('results/part_b_batch_aggregated.csv', index=False)

    for ds in df['Dataset'].unique():
        ds_df = df[(df['Dataset'] == ds) & (df['Config'] != 'Greedy') & (df['Valid'] == True)]
        if ds_df.empty:
            continue
        config_dfs = {cfg: ds_df[ds_df['Config'] == cfg] for cfg in configs}
        save_path = os.path.join('results', f'param_sensitivity_{ds}.png')
        Visualizer.plot_parameter_sensitivity(config_dfs, save_path)

    print("\nBatch processing complete. Results saved to results/")
```

**Steps:**
1. Create branch: `git checkout -b task/6-optimal-gap-sensitivity`
2. Add `OPTIMAL_VALUES` dict and replace `run_batch_part_b` in `main.py`.
3. Verify: `python main.py part_b --dataset data/setcover --experiment_batch` — check that aggregated table has a `Gap_mean` column and PNG sensitivity files appear in `results/`.
4. Commit: `git add main.py && git commit -m "feat: batch adds optimal gap%, actual generation count, and parameter sensitivity plots"`
5. Push and open PR: `git push -u origin task/6-optimal-gap-sensitivity && gh pr create --title "Task 6: optimal gap% and parameter sensitivity plot" --body "Adds OPTIMAL_VALUES dict with OR-Library known optima, Gap(%) column in batch results, actual generation count from early stopping, and calls Visualizer.plot_parameter_sensitivity per dataset after batch."`

---

## Task 7 — Cleanup: empty script, .gitignore, --verbose

**Branch:** `task/7-cleanup`

**Prompt:**

You are working in the repository at `c:\Users\אייל. ש\Documents\HUP\AI lab`.

Three small cleanup items:

**A. Remove `docs/` from `.gitignore`**
The `docs/` folder contains the assignment PDFs and `report.md` but is currently excluded from git. Remove the `docs/` line from `.gitignore`.

**B. Delete `scripts/lab1try.py`**
The file is empty and unused.

**C. Implement `--verbose` in `run_part_a`**
The flag is defined in argparse but does nothing. After the `print(f"Path: {formatted_path}")` line in `run_part_a`, add:

```python
        if args.verbose:
            print("\n--- Step-by-Step Solution ---")
            current = initial_state
            for step_num, action in enumerate(path, 1):
                v_id, offset = action
                v = current.get_vehicle(v_id)
                if v.is_horizontal:
                    direction = 'R' if offset > 0 else 'L'
                else:
                    direction = 'D' if offset > 0 else 'U'
                print(f"  Step {step_num}: Move {v_id} {direction}{abs(offset)}")
                problem_step = RushHourProblem(current)
                current = problem_step.get_result(current, action)
```

**Steps:**
1. Create branch: `git checkout -b task/7-cleanup`
2. Remove `docs/` from `.gitignore`.
3. Delete `scripts/lab1try.py`.
4. Add the verbose block to `run_part_a` in `main.py`.
5. Verify verbose: `python main.py part_a --board_file data/rh.txt --puzzle_index 1 --algorithm astar --heuristic h1 --verbose` — should print step-by-step moves.
6. Commit: `git add .gitignore main.py && git rm scripts/lab1try.py && git commit -m "fix: remove docs/ from gitignore, implement --verbose, delete empty script"`
7. Push and open PR: `git push -u origin task/7-cleanup && gh pr create --title "Task 7: cleanup — gitignore, verbose, empty script" --body "Three small fixes: removes docs/ exclusion from .gitignore so report and PDFs are tracked, implements --verbose step-by-step output in part_a, and deletes the empty scripts/lab1try.py."`
