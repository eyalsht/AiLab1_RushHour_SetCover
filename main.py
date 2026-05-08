import argparse
import sys
import os
import pandas as pd
import numpy as np

# Part A Imports
from src.part_a.state import State, Vehicle
from src.part_a.problem import RushHourProblem
from src.part_a.search import BreadthFirstSearch, AStarSearch
from src.part_a.generator import generate_puzzle

# Part B Imports
from src.part_b.problem import SetCoverProblem
from src.part_b.greedy import GreedySetCover
from src.part_b.ga_engine import GAEngine
from src.utils.visualizer import Visualizer

def parse_rush_hour_string(s: str) -> State:
    grid = [list(s[i*6:(i+1)*6]) for i in range(6)]
    vehicles_dict = {}
    
    for r in range(6):
        for c in range(6):
            char = grid[r][c]
            if char != '.':
                if char not in vehicles_dict:
                    vehicles_dict[char] = []
                vehicles_dict[char].append((r, c))
                
    vehicles = []
    for v_id, coords in vehicles_dict.items():
        coords.sort()
        r, c = coords[0]
        length = len(coords)
        if length > 1:
            if coords[1][0] == r:
                is_horiz = True
            else:
                is_horiz = False
        else:
            is_horiz = True
            
        vehicles.append(Vehicle(v_id, is_horiz, length, r, c))
        
    return State(frozenset(vehicles))

def parse_all_board_file(filepath: str) -> list:
    puzzles = []
    with open(filepath, 'r') as f:
        in_input = False
        for line in f:
            line = line.strip()
            if line == '--- RH-input ---':
                in_input = True
                continue
            if line == '--- end RH-input ---':
                break
            if in_input and len(line) == 36:
                puzzles.append(line)
    return puzzles

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

def parse_board_file(filepath: str, puzzle_index: int = 1) -> State:
    if filepath.endswith('rh.txt'):
        puzzles = parse_all_board_file(filepath)
        if puzzle_index < 1 or puzzle_index > len(puzzles):
            print(f"Error: puzzle_index must be between 1 and {len(puzzles)}")
            sys.exit(1)
        return parse_rush_hour_string(puzzles[puzzle_index - 1])
    else:
        # Fallback for manual TXT formats
        vehicles = []
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        v_id = parts[0]
                        is_horiz = (parts[1].lower() == 'h')
                        length = int(parts[2])
                        row = int(parts[3])
                        col = int(parts[4])
                        vehicles.append(Vehicle(v_id, is_horiz, length, row, col))
            return State(frozenset(vehicles))
        except FileNotFoundError:
            print(f"Error: Board file not found at {filepath}")
            sys.exit(1)

def format_solution(path: list, initial_state: State) -> str:
    formatted = []
    for step in path:
        v_id, offset = step
        v = initial_state.get_vehicle(v_id)
        if v.is_horizontal:
            direction = 'R' if offset > 0 else 'L'
        else:
            direction = 'D' if offset > 0 else 'U'
        formatted.append(f"{v_id}{direction}{abs(offset)}")
    return " ".join(formatted)

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
    bfs_solved = df[df['BFS_ok'] == 1]
    astar_solved = df[df['AStar_ok'] == 1]
    print(f"BFS  solved: {df['BFS_ok'].sum()}/40   avg N={bfs_solved['BFS_N'].mean():.0f}   avg ms={bfs_solved['BFS_ms'].mean():.1f}")
    print(f"A*   solved: {df['AStar_ok'].sum()}/40  avg N={astar_solved['AStar_N'].mean():.0f}  avg ms={astar_solved['AStar_ms'].mean():.1f}")

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

def run_part_a(args):
    if args.compare:
        run_comparison(args)
        return

    if args.generate_depth:
        print(f"Generating puzzle with depth {args.generate_depth}...")
        p = generate_puzzle(args.generate_depth)
        if p:
            print(f"Generated puzzle:\n{p}")
        else:
            print("Failed to generate puzzle.")
        return

    if args.batch:
        run_batch(args)
        return

    print(f"Loading Rush Hour board from: {args.board_file} (Puzzle Index: {args.puzzle_index})")
    initial_state = parse_board_file(args.board_file, args.puzzle_index)
    problem = RushHourProblem(initial_state, heuristic_type=args.heuristic)

    if args.algorithm == 'bfs':
        print("Running Breadth-First Search...")
        algo = BreadthFirstSearch()
    elif args.algorithm == 'astar':
        print("Running A* Search...")
        algo = AStarSearch()
    else:
        print(f"Unknown algorithm: {args.algorithm}")
        return

    time_limit = args.time_limit if args.time_limit else None
    solution = algo.search(problem, time_limit_ms=time_limit)
    
    metrics_summary = algo.metrics.get_metrics_summary()
    print("\n--- Metrics ---")
    for k, v in metrics_summary.items():
        print(f"{k}: {v}")
        
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
                direction = ('R' if offset > 0 else 'L') if v.is_horizontal else ('D' if offset > 0 else 'U')
                print(f"  Step {step_num}: Move {v_id} {direction}{abs(offset)}")
                current = problem.get_result(current, action)
    else:
        print("\nFAILED - No solution found or timeout reached.")

OPTIMAL_VALUES = {
    'scp41.txt': 429, 'scp42.txt': 512, 'scp43.txt': 516, 'scp44.txt': 494,
    'scp51.txt': 253, 'scp52.txt': 302, 'scp53.txt': 226,
    'scpa1.txt': 253, 'scpa2.txt': 252, 'scpa3.txt': 232,
}

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

def run_part_b(args):
    if getattr(args, 'experiment_batch', False):
        run_batch_part_b(args)
        return
        
    filepath = args.dataset
    if not os.path.exists(filepath):
        print(f"Dataset not found: {filepath}")
        return
        
    print(f"Loading Set Cover Dataset: {filepath}")
    problem = SetCoverProblem.from_file(filepath)
    print(f"Loaded: m={problem.m} elements, n={problem.n} sets")

    greedy = GreedySetCover()
    greedy_cost, greedy_sets, greedy_time = greedy.solve(problem)
    print(f"\n--- Greedy Baseline ---")
    print(f"Cost: {greedy_cost}")
    print(f"Time: {greedy_time:.2f} ms")
    
    if args.evaluate_only:
        return
        
    print(f"\n--- Genetic Algorithm ---")
    engine = GAEngine(
        problem=problem, seed=args.seed,
        pop_size=args.pop_size, mutation_rate=args.mut_rate,
        crossover_rate=args.cx_rate, generations=args.generations,
        selection_method='tournament'
    )
    
    best_chrom = engine.run()
    print(f"Best Configuration Found:")
    print(f"Valid: {best_chrom.is_valid}")
    print(f"Fitness (Cost+Penalty): {best_chrom.fitness}")
    print(f"Actual Cost: {best_chrom.cost}")
    print(f"Algorithm Time: {engine.history[-1]['elapsed_ms']:.2f} ms")
    
    if args.visualize:
        print("\nGenerating Visualizations in /results/...")
        Visualizer.plot_ga_convergence(engine.history, os.path.join("results", f"convergence-{os.path.basename(filepath)}.png"))
        Visualizer.plot_ga_diversity(engine.history, os.path.join("results", f"diversity-entropy-{os.path.basename(filepath)}.png"), metric='entropy')
        Visualizer.plot_ga_diversity(engine.history, os.path.join("results", f"diversity-stddev-{os.path.basename(filepath)}.png"), metric='std_dev')
        Visualizer.plot_ga_diversity(engine.history, os.path.join("results", f"diversity-hamming-{os.path.basename(filepath)}.png"), metric='hamming_distance')
        Visualizer.plot_selection_pressure(engine.history, os.path.join("results", f"selection-pressure-{os.path.basename(filepath)}.png"))
        
        matrix = np.array([c.genes for c in engine.population])
        Visualizer.plot_dendrogram(matrix, os.path.join("results", f"dendrogram-{os.path.basename(filepath)}.png"))
        print("Visualizations saved.")

def main():
    parser = argparse.ArgumentParser(description="AI Lab 1 - Search and Genetic Algorithms")
    subparsers = parser.add_subparsers(dest='command', help='Select Part A or Part B')

    # Part A Parser
    part_a_parser = subparsers.add_parser('part_a', help='Rush Hour Solver')
    part_a_parser.add_argument('--board_file', type=str, required=False, help='Path to board configuration file')
    part_a_parser.add_argument('--puzzle_index', type=int, default=1, help='Which puzzle index to run if using rh.txt (1-40)')
    part_a_parser.add_argument('--algorithm', type=str, choices=['bfs', 'astar'], default='astar', help='Algorithm to use')
    part_a_parser.add_argument('--heuristic', type=str, choices=['h1', 'h2'], default='h1', help='Heuristic function to use')
    part_a_parser.add_argument('--batch', action='store_true', help='Run all puzzles in the board file')
    part_a_parser.add_argument('--compare', action='store_true', help='Compare BFS vs A* on all puzzles')
    part_a_parser.add_argument('--time_limit', type=float, default=None, help='Max execution time in milliseconds')
    part_a_parser.add_argument('--generate_depth', type=int, default=None, help='Generate a random puzzle with specified solution depth')
    part_a_parser.add_argument('-v', '--verbose', action='store_true', help='Print step-by-step solution path')

    # Part B Parser
    part_b_parser = subparsers.add_parser('part_b', help='Set Cover GA solver')
    part_b_parser.add_argument('--dataset', type=str, required=True, help='Path to scp*.txt dataset or directory (for batch)')
    part_b_parser.add_argument('--seed', type=int, default=42, help='Random seed')
    part_b_parser.add_argument('--evaluate_only', action='store_true', help='Only run Baseline Greedy algorithm')
    part_b_parser.add_argument('--visualize', action='store_true', help='Generate convergence and diversity graphs')
    part_b_parser.add_argument('--experiment_batch', action='store_true', help='Run automated batch comparison for all configs and datasets')
    part_b_parser.add_argument('--pop_size', type=int, default=300)
    part_b_parser.add_argument('--mut_rate', type=float, default=0.05)
    part_b_parser.add_argument('--cx_rate', type=float, default=0.8)
    part_b_parser.add_argument('--generations', type=int, default=200)

    args = parser.parse_args()

    if args.command == 'part_a':
        run_part_a(args)
    elif args.command == 'part_b':
        run_part_b(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
