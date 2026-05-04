import random
import time
import numpy as np
from typing import List, Tuple, Dict, Any
from src.part_b.problem import SetCoverProblem
from src.part_b.chromosome import Chromosome

class GAEngine:
    def __init__(self, problem: SetCoverProblem, seed: int = 42,
                 pop_size: int = 300, mutation_rate: float = 0.05,
                 crossover_rate: float = 0.8, generations: int = 200,
                 selection_method: str = 'tournament'):
        self.problem = problem
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations
        self.selection_method = selection_method
        
        self.random = random.Random(seed)
        self.population: List[Chromosome] = []
        self.history: List[Dict[str, Any]] = []

    def initialize_population(self):
        self.population = []
        # Initialize with very few random sets, rely on Repair to make them valid and diverse
        init_prob = 2.0 / self.problem.n if self.problem.n > 0 else 0.1
        for _ in range(self.pop_size):
            genes = [1 if self.random.random() < init_prob else 0 for _ in range(self.problem.n)]
            chrom = Chromosome(genes=genes)
            chrom.evaluate(self.problem)
            self.population.append(chrom)

    def select(self) -> Chromosome:
        # Mating pool: only select from the top 50% of the population (assumes population is sorted)
        mating_pool_size = max(2, self.pop_size // 2)
        mating_pool = self.population[:mating_pool_size]
        
        if self.selection_method == 'tournament':
            k = 3
            contenders = self.random.sample(mating_pool, k)
            return min(contenders, key=lambda c: c.fitness)
        elif self.selection_method == 'roulette':
            total_inverse_fitness = sum(1.0 / c.fitness for c in mating_pool if c.fitness > 0)
            pick = self.random.uniform(0, total_inverse_fitness)
            current = 0.0
            for c in mating_pool:
                if c.fitness > 0:
                    current += 1.0 / c.fitness
                    if current > pick:
                        return c
            return mating_pool[-1]

    def crossover(self, p1: Chromosome, p2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        if self.random.random() < self.crossover_rate:
            c1_genes = []
            c2_genes = []
            for g1, g2 in zip(p1.genes, p2.genes):
                if self.random.random() < 0.5:
                    c1_genes.append(g1)
                    c2_genes.append(g2)
                else:
                    c1_genes.append(g2)
                    c2_genes.append(g1)
            return Chromosome(c1_genes), Chromosome(c2_genes)
        return Chromosome(list(p1.genes)), Chromosome(list(p2.genes))

    def mutate(self, chrom: Chromosome) -> None:
        for i in range(len(chrom.genes)):
            if self.random.random() < self.mutation_rate:
                chrom.genes[i] = 1 - chrom.genes[i]

    def run(self) -> Chromosome:
        start_time = time.perf_counter()
        self.initialize_population()
        self.record_metrics(0, start_time)
        
        for gen in range(1, self.generations + 1):
            new_population = []
            self.population.sort(key=lambda c: c.fitness)
            
            # Elitism: keep top 10%
            esize = int(self.pop_size * 0.1)
            if esize < 1: esize = 1
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
            
        self.population.sort(key=lambda c: c.fitness)
        return self.population[0]

    def record_metrics(self, gen: int, start_time: float):
        fitness_values = [c.fitness for c in self.population]
        valid_costs = [c.cost for c in self.population if c.is_valid]
        
        best = min(fitness_values)
        avg = sum(fitness_values) / len(fitness_values)
        worst = max(fitness_values)
        std_dev = float(np.std(fitness_values))
        
        # Selection Pressure: For a minimization problem, higher avg relative to best = more pressure.
        selection_pressure = float(avg / best) if best > 0 else 1.0
        
        matrix = np.array([c.genes for c in self.population])
        p_1 = matrix.mean(axis=0)
        p_0 = 1 - p_1
        
        # Entropy
        p_1_clipped = np.clip(p_1, 1e-9, 1 - 1e-9)
        p_0_clipped = np.clip(p_0, 1e-9, 1 - 1e-9)
        entropy = float(-np.sum(p_1_clipped * np.log2(p_1_clipped) + p_0_clipped * np.log2(p_0_clipped)) / self.problem.n)
        
        # Hamming Distance (Expected pairwise average)
        # Average pairwise Hamming distance = sum(2 * p_1 * p_0)
        hamming_distance = float(np.sum(2 * p_1 * p_0))
        
        elapsed = (time.perf_counter() - start_time) * 1000.0
        
        best_valid_cost = min(valid_costs) if valid_costs else float('inf')
        
        self.history.append({
            "generation": gen,
            "best_fitness": best,
            "avg_fitness": avg,
            "worst_fitness": worst,
            "std_dev": std_dev,
            "entropy": entropy,
            "hamming_distance": hamming_distance,
            "selection_pressure": selection_pressure,
            "best_valid_cost": best_valid_cost,
            "elapsed_ms": elapsed
        })
