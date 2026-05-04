import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.cluster.hierarchy as sch
from typing import List, Dict, Any
import os

class Visualizer:
    @staticmethod
    def plot_ga_convergence(history: List[Dict[str, Any]], save_path: str, title: str = "GA Convergence"):
        df = pd.DataFrame(history)
        plt.figure(figsize=(10, 6))
        plt.plot(df['generation'], df['best_fitness'], label='Best Fitness', color='green')
        plt.plot(df['generation'], df['avg_fitness'], label='Average Fitness', color='blue')
        plt.plot(df['generation'], df['worst_fitness'], label='Worst Fitness', color='red', alpha=0.5)
        
        plt.title(title)
        plt.xlabel('Generation')
        plt.ylabel('Fitness (Cost + Penalty)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def plot_ga_diversity(history: List[Dict[str, Any]], save_path: str, metric: str = 'entropy'):
        df = pd.DataFrame(history)
        plt.figure(figsize=(10, 6))
        if metric == 'std_dev':
            plt.plot(df['generation'], df['std_dev'], color='purple')
            plt.ylabel('Standard Deviation of Fitness')
            title_metric = 'Standard Deviation'
        elif metric == 'hamming_distance':
            plt.plot(df['generation'], df['hamming_distance'], color='teal')
            plt.ylabel('Average Pairwise Hamming Distance')
            title_metric = 'Hamming Distance'
        else:
            plt.plot(df['generation'], df['entropy'], color='orange')
            plt.ylabel('Shannon Entropy (Diversity)')
            title_metric = 'Entropy'
            
        plt.title(f'Population Diversity over Generations ({title_metric})')
        plt.xlabel('Generation')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def plot_selection_pressure(history: List[Dict[str, Any]], save_path: str):
        df = pd.DataFrame(history)
        plt.figure(figsize=(10, 6))
        plt.plot(df['generation'], df['selection_pressure'], color='darkred')
        
        plt.title('Selection Pressure over Generations (Avg / Best)')
        plt.xlabel('Generation')
        plt.ylabel('Selection Pressure Ratio')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def plot_parameter_sensitivity(results_dfs: Dict[str, pd.DataFrame], save_path: str):
        plt.figure(figsize=(10, 6))
        for config_name, df in results_dfs.items():
            plt.plot(df['generation'], df['best_fitness'], label=config_name)
            
        plt.title('Parameter Sensitivity (Convergence Speed)')
        plt.xlabel('Generation')
        plt.ylabel('Best Fitness')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()
        
    @staticmethod
    def plot_dendrogram(population_matrix: np.ndarray, save_path: str, title="Population Clustering"):
        plt.figure(figsize=(12, 8))
        if len(population_matrix) > 100:
            indices = np.random.choice(len(population_matrix), 100, replace=False)
            data = population_matrix[indices]
        else:
            data = population_matrix
            
        linkage_matrix = sch.linkage(data, method='ward')
        sch.dendrogram(linkage_matrix, truncate_mode='level', p=5)
        
        plt.title(title)
        plt.xlabel('Sample Index (or cluster)')
        plt.ylabel('Distance')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()
