# AI Lab 1 — Finish & Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete all missing assignment requirements in both Part A (Rush Hour) and Part B (Set Cover GA) so the project can be submitted.

**Architecture:** All code changes are confined to `main.py`, `src/part_a/generator.py`, and `src/part_b/ga_engine.py`. No new files are needed except the plan. The report at `docs/report.md` needs corrections too.

**Tech Stack:** Python 3, pandas, numpy, matplotlib, scipy — all already in `requirements.txt`.

---

## Part A Tasks

---

### Task 1: Solution file output in `run_batch`

**Files:**
- Modify: `main.py` — `run_batch` function (lines 104–131)

The assignment explicitly requires a file with one solution line per puzzle (or "FAILED"). Currently `run_batch` only prints a table to stdout with no file output.

- [ ] **Step 1: Add solution-file writing to `run_batch`**

Replace the existing `run_batch` function in `main.py` with this:

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

    # Write solution file
    with open(solutions_file, 'w') as f:
        for line in solution_lines:
            f.write(line + "\n")
    print(f"Solutions written to: {solutions_file}")

    # Statistics summary per heuristic
    df = pd.DataFrame(rows)
    solved = df[df['Success'] == 'Y']
    print(f"\n--- Statistics Summary ({args.heuristic}, {args.algorithm}) ---")
    if not solved.empty:
        for col in ['N', 'd/N', 'Time(ms)', 'EBF', 'Havg', 'Min Depth', 'Avg Depth', 'Max Depth']:
            print(f"  Avg {col}: {solved[col].mean():.4f}")

    # Save to CSV
    csv_file = os.path.join("results", f"batch_results_{algo_tag}_{args.heuristic}.csv")
    df.to_csv(csv_file, index=False)
    print(f"Batch results saved to: {csv_file}")
```

- [ ] **Step 2: Verify manually**

Run:
```
python main.py part_a --board_file data/rh.txt --batch --algorithm astar --heuristic h1 --time_limit 5000
```
Expected: table printed, then "Solutions written to: results/solutions_astar_h1.txt", then stats summary, then CSV path.
Check `results/solutions_astar_h1.txt` — should have 40 lines.

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: part_a batch writes solution file, stats summary, and CSV"
```

---

### Task 2: BFS vs A* comparison (`--compare` flag)

**Files:**
- Modify: `main.py` — add `run_comparison` function and `--compare` flag

The assignment requires comparing BFS (uninformed) vs A* (informed) under the same time limit.

- [ ] **Step 1: Add `run_comparison` function** (insert before `run_part_a`):

```python
def run_comparison(args):
    """Run BFS and A* on all puzzles and print a side-by-side comparison."""
    puzzles = parse_all_board_file(args.board_file)
    time_limit = args.time_limit if args.time_limit else 5000.0
    heuristic = args.heuristic  # used for A* only

    print(f"\n=== BFS vs A* Comparison (time_limit={time_limit}ms, A* heuristic={heuristic}) ===\n")
    print(f"{'#':<4} | {'BFS_N':<8} | {'BFS_d':<6} | {'BFS_ms':<8} | {'BFS_ok':<6} | "
          f"{'AStar_N':<8} | {'AStar_d':<6} | {'AStar_ms':<8} | {'AStar_ok':<6} | "
          f"{'BFS_sol_len':<11} | {'Astar_sol_len':<13}")
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
              f"{bfs_len:<11} | {astar_len:<13}")

        rows.append({
            'Problem': i+1,
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

- [ ] **Step 2: Add `--compare` flag to argparse** (in `main()`, after the `--batch` line in `part_a_parser`):

```python
part_a_parser.add_argument('--compare', action='store_true', help='Compare BFS vs A* on all puzzles')
```

- [ ] **Step 3: Wire it in `run_part_a`** (add before the existing `if args.generate_depth:` block):

```python
    if args.compare:
        run_comparison(args)
        return
```

- [ ] **Step 4: Verify**

```
python main.py part_a --board_file data/rh.txt --compare --heuristic h1 --time_limit 5000
```
Expected: Table with BFS and A* side-by-side, summary line, CSV saved.

- [ ] **Step 5: Commit**

```bash
git add main.py
git commit -m "feat: part_a --compare flag for BFS vs A* side-by-side analysis"
```

---

### Task 3: Category analysis and given-solution comparison

**Files:**
- Modify: `main.py` — add `parse_given_solutions` and `run_category_analysis` functions, wire into `--compare`

- [ ] **Step 1: Add `parse_given_solutions` function** (after `parse_all_board_file`):

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
                # Remove trailing ' .' and split
                soln_str = line[len('Soln:'):].strip().rstrip('.')
                tokens = [t for t in soln_str.split() if t != '.']
                solutions.append(len(tokens))
    return solutions
```

- [ ] **Step 2: Extend `run_comparison` to include category and given-solution columns**

Replace the end of `run_comparison` (starting from `df = pd.DataFrame(rows)`) with:

```python
    df = pd.DataFrame(rows)

    # Category labels (1-10 Beginner, 11-20 Intermediate, 21-30 Advanced, 31-40 Expert)
    def category(n):
        if n <= 10: return 'Beginner'
        elif n <= 20: return 'Intermediate'
        elif n <= 30: return 'Advanced'
        return 'Expert'
    df['Category'] = df['Problem'].apply(category)

    # Given solution lengths
    given = parse_given_solutions(args.board_file)
    if len(given) == len(df):
        df['Given_sol_len'] = given
    else:
        df['Given_sol_len'] = -1

    print("\n--- Summary ---")
    print(f"BFS  solved: {df['BFS_ok'].sum()}/40   avg N={df[df['BFS_ok']==1]['BFS_N'].mean():.0f}   avg ms={df[df['BFS_ok']==1]['BFS_ms'].mean():.1f}")
    print(f"A*   solved: {df['AStar_ok'].sum()}/40  avg N={df[df['AStar_ok']==1]['AStar_N'].mean():.0f}  avg ms={df[df['AStar_ok']==1]['AStar_ms'].mean():.1f}")

    print("\n--- Category Breakdown (A*) ---")
    cat_df = df[df['AStar_ok'] == 1].groupby('Category').agg(
        Solved=('AStar_ok', 'sum'),
        Avg_N=('AStar_N', 'mean'),
        Avg_ms=('AStar_ms', 'mean'),
        Avg_sol_len=('AStar_sol_len', 'mean'),
    )
    print(cat_df.to_string())

    print("\n--- Solution Length: Ours vs Given (A*) ---")
    comp = df[df['AStar_ok'] == 1][['Problem', 'Category', 'AStar_sol_len', 'Given_sol_len']].copy()
    comp['shorter'] = comp['AStar_sol_len'] < comp['Given_sol_len']
    comp['equal'] = comp['AStar_sol_len'] == comp['Given_sol_len']
    comp['longer'] = comp['AStar_sol_len'] > comp['Given_sol_len']
    print(comp[['Problem', 'AStar_sol_len', 'Given_sol_len']].to_string(index=False))
    print(f"\nOurs shorter: {comp['shorter'].sum()}  Equal: {comp['equal'].sum()}  Longer: {comp['longer'].sum()}")

    os.makedirs("results", exist_ok=True)
    df.to_csv("results/bfs_vs_astar.csv", index=False)
    print("\nSaved to results/bfs_vs_astar.csv")
```

- [ ] **Step 3: Verify**

```
python main.py part_a --board_file data/rh.txt --compare --heuristic h1 --time_limit 5000
```
Expected: Category breakdown table printed, solution length comparison printed.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: part_a compare adds category analysis and given-solution comparison"
```

---

### Task 4: Generator validity checks

**Files:**
- Modify: `src/part_a/generator.py` — `generate_puzzle` function

The current generator doesn't enforce: (1) at least 1 blocker in X's path, (2) 1–3 vertical blockers, (3) min occupancy ≥ 12 cells, (4) at least 1 dependent blocker.

- [ ] **Step 1: Add validity-check helper and update `generate_puzzle`**

Replace `src/part_a/generator.py` entirely:

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
    """Return True only if the board meets the assignment constraints."""
    grid = [['.' for _ in range(state.grid_size)] for _ in range(state.grid_size)]
    for v in state.vehicles:
        for i in range(v.length):
            if v.is_horizontal:
                grid[v.row][v.col + i] = v.id
            else:
                grid[v.row + i][v.col] = v.id

    # Find X position
    x_vehicle = state.get_vehicle('X')
    if x_vehicle is None:
        return False
    x_right_end = x_vehicle.col + x_vehicle.length  # first blocked column index

    # 1. At least 1 vehicle blocking X's path (columns x_right_end..5, row 2)
    blockers = []
    for col in range(x_right_end, 6):
        cell = grid[2][col]
        if cell != '.' and cell != 'X':
            blocker_v = state.get_vehicle(cell)
            if blocker_v and not blocker_v.is_horizontal:
                blockers.append(blocker_v)
    if len(blockers) < 1:
        return False

    # 2. 1–3 vertical blockers in the exit lane
    if not (1 <= len(blockers) <= 3):
        return False

    # 3. Minimum occupancy: at least 12 cells occupied (out of 36)
    occupied = sum(1 for row in grid for cell in row if cell != '.')
    if occupied < 12:
        return False

    # 4. At least one blocker is "dependent" — cannot move directly (both ends blocked)
    has_dependent = False
    for v in blockers:
        top_row = v.row - 1
        bot_row = v.row + v.length
        top_blocked = (top_row < 0) or (grid[top_row][v.col] != '.')
        bot_blocked = (bot_row >= 6) or (grid[bot_row][v.col] != '.')
        if top_blocked and bot_blocked:
            has_dependent = True
            break
    if not has_dependent:
        return False

    return True


def generate_puzzle(target_depth: int, max_attempts: int = 1000) -> Optional[str]:
    """
    Randomly generates a valid Rush Hour board that has a solution depth of `target_depth`.
    Returns the 36-character string representation, or None if unsuccessful.
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
```

- [ ] **Step 2: Verify**

```
python main.py part_a --generate_depth 5
```
Expected: prints "Generated puzzle:" followed by a 36-char string, or "Failed to generate puzzle." — no crashes.

- [ ] **Step 3: Commit**

```bash
git add src/part_a/generator.py
git commit -m "feat: generator enforces blocker count, occupancy, and dependency constraints"
```

---

## Part B Tasks

---

### Task 5: Early stopping in `GAEngine`

**Files:**
- Modify: `src/part_b/ga_engine.py` — `__init__` and `run` methods

Currently only `generations=200` terminates the loop. Adding stagnation + entropy stopping meets the "multiple stopping conditions" requirement.

- [ ] **Step 1: Add `stagnation_limit` and `entropy_threshold` params to `__init__`**

Change the constructor signature and add attributes:

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

- [ ] **Step 2: Add early stopping logic to `run`**

Replace the `run` method:

```python
def run(self) -> Chromosome:
    start_time = time.perf_counter()
    self.initialize_population()
    self.record_metrics(0, start_time)

    best_fitness = float('inf')
    stagnation_counter = 0
    stop_reason = f"max generations ({self.generations})"

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
            stop_reason = f"stagnation ({self.stagnation_limit} gens)"
            break

        if current_entropy < self.entropy_threshold:
            stop_reason = f"entropy convergence ({current_entropy:.4f} < {self.entropy_threshold})"
            break

    self.population.sort(key=lambda c: c.fitness)
    self.history[-1]['stop_reason'] = stop_reason
    return self.population[0]
```

- [ ] **Step 3: Verify**

```
python main.py part_b --dataset data/setcover/scp41.txt
```
Expected: runs without error, terminates and prints result.

- [ ] **Step 4: Commit**

```bash
git add src/part_b/ga_engine.py
git commit -m "feat: GA early stopping on stagnation and entropy convergence"
```

---

### Task 6: Optimal values, gap%, and `plot_parameter_sensitivity` in batch

**Files:**
- Modify: `main.py` — `run_batch_part_b` function

- [ ] **Step 1: Add `OPTIMAL_VALUES` dict** (add before `run_batch_part_b`):

```python
OPTIMAL_VALUES = {
    'scp41.txt': 429, 'scp42.txt': 512, 'scp43.txt': 516, 'scp44.txt': 494,
    'scp51.txt': 253, 'scp52.txt': 302, 'scp53.txt': 226,
    'scpa1.txt': 253, 'scpa2.txt': 252, 'scpa3.txt': 232,
}
```

- [ ] **Step 2: Add gap% column and call `plot_parameter_sensitivity`**

Replace `run_batch_part_b` with:

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
        optimal = OPTIMAL_VALUES.get(ds, None)

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

    # Parameter sensitivity plot (one per dataset, comparing 3 configs)
    for ds in df['Dataset'].unique():
        ds_df = df[(df['Dataset'] == ds) & (df['Config'] != 'Greedy') & (df['Valid'] == True)]
        if ds_df.empty:
            continue
        config_dfs = {cfg: ds_df[ds_df['Config'] == cfg] for cfg in configs}
        save_path = os.path.join('results', f'param_sensitivity_{ds}.png')
        Visualizer.plot_parameter_sensitivity(config_dfs, save_path)

    print("\nBatch processing complete. Results saved to results/")
```

- [ ] **Step 3: Verify (dry run with one dataset)**

```
python main.py part_b --dataset data/setcover/scp41.txt --experiment_batch
```
Expected: runs, prints aggregated table, saves CSVs and PNG files without error.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: part_b batch adds optimal gap%, early-stopping gens, and param sensitivity plot"
```

---

## Small Fixes

---

### Task 7: Small code/config fixes

**Files:**
- Modify: `.gitignore` — remove `docs/` entry
- Delete: `scripts/lab1try.py` — empty file
- Modify: `main.py` — implement `--verbose` flag

- [ ] **Step 1: Remove `docs/` from `.gitignore`**

In `.gitignore`, remove the line `docs/`.

- [ ] **Step 2: Delete empty script**

```bash
rm scripts/lab1try.py
```

- [ ] **Step 3: Implement `--verbose` in `run_part_a`**

After the `if solution:` block in `run_part_a` (around line 169), add verbose step-by-step output:

```python
    if solution:
        path = solution.get_solution_path()
        formatted_path = format_solution(path, initial_state)
        print(f"\nSolution found! Path length: {len(path)}")
        print(f"Path: {formatted_path}")
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
                problem2 = RushHourProblem(current)
                current = problem2.get_result(current, action)
```

- [ ] **Step 4: Commit**

```bash
git add .gitignore main.py
git rm scripts/lab1try.py
git commit -m "fix: remove docs/ from gitignore, implement --verbose, delete empty script"
```

---

## Self-Review

### Spec Coverage Check

| Requirement | Task |
|---|---|
| Solution file per algorithm/heuristic (40 lines or FAILED) | Task 1 |
| Stats summary (avg N, d/N, Time, EBF, Havg, depths) per run | Task 1 |
| Save batch results to CSV | Task 1 |
| BFS vs A* comparison table | Task 2 |
| Category breakdown (Beginner/Intermediate/Advanced/Expert) | Task 3 |
| Comparison with given solutions from rh.txt | Task 3 |
| Generator: blocker count, occupancy, dependency constraints | Task 4 |
| GA: early stopping (stagnation + entropy) | Task 5 |
| GA: optimal values dict + gap(%) column | Task 6 |
| GA: plot_parameter_sensitivity called after batch | Task 6 |
| `scripts/lab1try.py` deleted | Task 7 |
| `docs/` removed from .gitignore | Task 7 |
| `--verbose` implemented | Task 7 |

### Not covered (report content — do manually):
- Writing the report text in `docs/report.md` — the report exists but has factual errors (says "penalty" when code uses "repair"). Must be corrected manually.
- The report currently says `Dynamic Penalty Algorithm` on line 23 — this contradicts the actual code which uses Repair + hill-climbing. Fix this section.

---

## Execution Order

Run tasks in order: 1 → 2 → 3 → 4 → 5 → 6 → 7. Tasks 1–4 are independent of Tasks 5–7 (different files), so Tasks 5–7 can be done in parallel with Tasks 1–4 if using subagent-driven execution.
