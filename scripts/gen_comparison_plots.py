import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from src.part_b.problem import SetCoverProblem
from src.part_b.ga_engine import GAEngine
from src.utils.visualizer import Visualizer

os.makedirs('results', exist_ok=True)
problem = SetCoverProblem.from_file('data/setcover/scp41.txt')

configs = {
    'crossover-only': {'mut_rate': 0.0,  'cx_rate': 0.8},
    'mutation-only':  {'mut_rate': 0.05, 'cx_rate': 0.0},
    'both':           {'mut_rate': 0.05, 'cx_rate': 0.8},
}

all_histories = {}
for name, params in configs.items():
    print(f'Running {name}...')
    engine = GAEngine(
        problem=problem, seed=42,
        pop_size=300,
        mutation_rate=params['mut_rate'],
        crossover_rate=params['cx_rate'],
        generations=200,
        entropy_threshold=0.0,
        stagnation_limit=30,
    )
    engine.run()
    all_histories[name] = engine.history
    Visualizer.plot_ga_convergence(
        engine.history,
        f'results/convergence-scp41-{name}.png',
        title=f'GA Convergence — scp41 ({name})'
    )
    Visualizer.plot_ga_diversity(
        engine.history,
        f'results/diversity-entropy-scp41-{name}.png',
        metric='entropy'
    )
    Visualizer.plot_selection_pressure(
        engine.history,
        f'results/selection-pressure-scp41-{name}.png'
    )
    print(f'  -> gens={engine.history[-1]["generation"]}  best={engine.history[-1]["best_fitness"]}')

history_dfs = {k: pd.DataFrame(v) for k, v in all_histories.items()}
Visualizer.plot_parameter_sensitivity(
    history_dfs,
    'results/param_sensitivity_scp41_3configs.png'
)
print('Done. PNGs saved to results/')
