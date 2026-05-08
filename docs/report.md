# AI Lab 1 — Search Algorithms and Genetic Algorithms

## 1. Introduction

This lab covers two problems. The first is Rush Hour, a sliding-block puzzle on a 6×6 grid where the goal is to move a target car (X) to the exit. We implemented BFS and A* with two heuristics and ran them on 40 puzzles across four difficulty levels. The second problem is Weighted Set Cover, which is NP-hard. We built a Genetic Algorithm with a repair-based fitness function and compared it against a greedy baseline and known OR-Library optima.

---

## 2. Part A: Rush Hour Solver

### 2.1 Problem Representation

The board is a 6×6 grid. Each vehicle has an ID, orientation (horizontal or vertical), length (2 or 3), and a top-left position (row, col). We represented the state as a `State` dataclass wrapping a `frozenset` of `Vehicle` dataclasses. Using a frozenset means states are hashable with no extra work, so membership checks in the explored set are O(1).

```python
@dataclass(frozen=True)
class Vehicle:
    id: str
    is_horizontal: bool
    length: int
    row: int
    col: int

@dataclass(frozen=True)
class State:
    vehicles: frozenset  # frozenset of Vehicle
    grid_size: int = 6
```

The goal is satisfied when vehicle X's right edge reaches column 6. Actions are all valid single-cell moves for every vehicle. The branching factor is not fixed — it depends on how many open cells border each car on the current board.

### 2.2 Algorithms

**BFS** uses a `deque` as the frontier and a `set` for the explored states. It processes nodes level by level, guaranteeing the first solution found is the shortest. Every state is added to explored exactly once so cycles are prevented.

**A\*** uses a `heapq` (min-heap) ordered by f(n) = g(n) + h(n), where g is the path cost and h is the heuristic. We store the best known g-cost per state in the explored dict and skip any node whose g-cost is worse than what we already found. This handles the case where a state is reached via multiple paths.

### 2.3 Heuristics

**h1 — Blocking cars count:**

```
h1(s) = |{vertical cars in X's exit lane}| + 1
```

The +1 is for X itself. Every blocking car must move at least once, and X must move at least once, so this never overestimates. Admissible.

**h2 — Blocking cars + stuck blockers:**

```
h2(s) = h1(s) + |{blocking cars that cannot move in either direction}|
```

A blocking car is "stuck" if both its top and bottom ends are blocked (grid boundary or another vehicle). A stuck blocker requires at least one extra move to free it before it can move out of X's path, so adding 1 per stuck blocker is still a lower bound. h2 >= h1 always, so h2 is the more informed heuristic.

```python
# From problem.py
h2 = h1
for car_id in blocking_cars:
    car = state.get_vehicle(car_id)
    if not car.is_horizontal:
        can_move_up = car.row > 0 and grid[car.row - 1][car.col] is None
        can_move_down = (car.row + car.length < state.grid_size
                         and grid[car.row + car.length][car.col] is None)
        if not can_move_up and not can_move_down:
            h2 += 1
```

**Admissibility:** Both h1 and h2 count only moves that must happen, so they never exceed the true cost.

**Monotonicity (consistency):** Each action costs 1. Moving a car can reduce the heuristic by at most 1 (we unblock at most one car or advance X). So h(n) ≤ 1 + h(n'), meaning f = g + h is non-decreasing along any path. A* with a consistent heuristic never needs to re-expand closed nodes.

### 2.4 Results

All three configurations — BFS, A\* h1, and A\* h2 — solved all 40 puzzles successfully. The table below shows per-category averages across 10 puzzles each.

**Table 1: Average N (nodes generated) per category**

| Category | BFS | A\* h1 | A\* h2 |
|---|---|---|---|
| Beginner (1–10) | 1,314 | 798 | 679 |
| Intermediate (11–20) | 2,370 | 1,553 | 1,420 |
| Advanced (21–30) | 3,179 | 2,997 | 2,817 |
| Expert (31–40) | 3,050 | 2,949 | 2,985 |
| **Overall avg** | **2,478** | **2,074** | **1,975** |

**Table 2: Average EBF per category**

| Category | BFS | A\* h1 | A\* h2 |
|---|---|---|---|
| Beginner | 2.36 | 1.81 | 1.77 |
| Intermediate | 1.61 | 1.39 | 1.38 |
| Advanced | 1.37 | 1.25 | 1.25 |
| Expert | 1.21 | 1.14 | 1.14 |
| **Overall avg** | **1.64** | **1.40** | **1.39** |

**Table 3: Summary statistics (all 40 puzzles)**

| Algorithm | Avg N | EBF | d/N | Havg | Avg Time (ms) |
|---|---|---|---|---|---|
| BFS | 2,478 | 1.635 | 0.0177 | — | 441 |
| A\* h1 | 2,074 | 1.399 | 0.0215 | 3.08 | 282 |
| A\* h2 | 1,975 | 1.388 | 0.0251 | 3.97 | 547 |

A few observations from the data:

The heuristic effect is most pronounced on beginner and intermediate puzzles, where A\* h1 uses about 40% fewer nodes than BFS. On expert puzzles the gap narrows — those boards have long solution paths with many branching points, and h1 and h2 provide less discrimination at deeper levels.

h2 consistently generates fewer nodes than h1 (1,975 vs 2,074 overall), but its per-node cost is higher because it does more work per evaluation. This shows up in the timing: A\* h2 is actually slower on average (547 ms vs 282 ms) despite visiting fewer nodes. For this problem size h1 is likely the better practical choice unless we need the absolute minimum node count.

All solutions produced by A\* matched the reference solution lengths in `rh.txt`, confirming the heuristics are admissible and A\* found optimal paths.

**d/N (penetrance)** increased from BFS (0.018) to A\* h1 (0.022) to A\* h2 (0.025), reflecting that the heuristics help focus the search on paths that lead more directly to the solution.

### 2.5 Puzzle Generator

We added a generator (`src/part_a/generator.py`) that produces valid puzzles with a specified solution depth. Random boards are generated and rejected unless they satisfy:

1. Between 1 and 3 vertical blockers in X's exit lane
2. At least 12 occupied cells
3. At least one blocker that is stuck (cannot move up or down)

Without these checks, the generator would produce mostly trivial boards with a clear path or no meaningful structure. Constraint 3 ensures there is at least one dependency chain to make the puzzle non-trivial. Each candidate is then solved with A\*, and only boards whose solution depth matches the target are returned.

---

## 3. Part B: Weighted Set Cover (Genetic Algorithm)

### 3.1 Problem Definition

Given m elements and n sets with costs, find the minimum-cost subset of sets that covers every element. We tested on 10 OR-Library benchmark instances: scp41–scp44 (200 elements, 1000 sets), scp51–scp53 (200 elements, 2000 sets), and scpa1–scpa3 (300 elements, 3000 sets). Known optimal values for all instances are available for comparison.

### 3.2 Chromosome Encoding

Each chromosome is a binary array of length n. Gene i = 1 means set i is included; 0 means it is excluded. A chromosome is decoded by collecting all sets where the gene is 1.

```python
# From chromosome.py
@dataclass
class Chromosome:
    genes: List[int]          # binary, length n
    fitness: float = inf
    is_valid: bool = False
    cost: float = inf
```

### 3.3 Fitness — Repair and Trim

A random binary chromosome will almost always miss some elements. Instead of penalizing invalid solutions, we repair them inside `evaluate()`. The key insight is that after repair the chromosome is always valid, so the GA only ever compares valid solutions and fitness is simply the total cost.

**Repair phase:** Find all uncovered elements. Greedily add the unselected set with the best cost/new-coverage ratio until all elements are covered.

**Trim phase:** Iterate over selected sets sorted by cost (descending). Remove any set whose elements are all covered by at least one other selected set. This removes expensive redundant sets.

```python
# Repair: add best-ratio sets until fully covered
while uncovered:
    best_set = min(unselected, key=lambda s: cost[s] / new_coverage(s))
    select(best_set)

# Trim: drop redundant sets (expensive first)
for s in selected_sets (sorted by cost, desc):
    if every element of s has count >= 2:
        deselect(s)

fitness = sum(cost[i] for i if genes[i] == 1)  # always valid
```

### 3.4 Initialization

Population of 300 chromosomes. Each gene is set to 1 with probability 2/n (very sparse). The repair phase then fills each chromosome into a valid solution. Starting sparse forces the repair mechanism to make the first selection decisions, which tends to produce a reasonably good initial population.

### 3.5 Selection

Tournament selection with k=3, from a mating pool of the top 50% of the population (sorted by fitness). Three candidates are drawn at random and the best wins. Restricting to the top 50% provides additional selection pressure without completely excluding the lower half.

### 3.6 Crossover

Uniform crossover at rate 0.8. For each gene position, we flip a coin to decide which parent to copy from. This allows any combination of gene blocks from both parents, not just a single split point.

### 3.7 Mutation

Bit-flip mutation at rate 0.05 per gene. Each gene flips independently with 5% probability. Because repair runs after mutation, flipping a 1 to 0 (removing a set) is safe — if that set was needed, the repair step will add back a suitable replacement.

### 3.8 Elitism

Top 10% of each generation are copied directly into the next generation without modification. This prevents good solutions from being lost.

### 3.9 Early Stopping

Two conditions stop the run early (before 200 generations):

- **Stagnation:** Best fitness unchanged for 30 consecutive generations
- **Entropy convergence:** Average per-position Shannon entropy drops below 0.05

### 3.10 Diversity Metrics

We tracked three metrics every generation:

- **Shannon entropy** (per-bit average) — approaches 0 when all chromosomes are identical
- **Average pairwise Hamming distance** — expected number of positions where two random chromosomes differ, computed as sum(2·p·(1−p)) across all positions
- **Fitness standard deviation** — spread of fitness values in the population

Convergence plots and diversity plots are saved to `results/` (e.g. `results/convergence-scp41.txt.png`, `results/diversity-entropy-scp41.txt.png`).

### 3.11 Greedy Baseline

At each step, pick the set with the lowest cost-per-new-element ratio. Runs in milliseconds. Used as a lower bar — the GA should beat it on every instance.

### 3.12 Results

The table below shows results for seed=42, pop=300, mutation=0.05, crossover=0.8 on all 10 datasets.

**Table 4: GA vs Greedy vs Optimal**

| Dataset | m | n | Optimal | Greedy | Gap | GA | Gap |
|---|---|---|---|---|---|---|---|
| scp41 | 200 | 1000 | 429 | 463 | +7.9% | 433 | +0.93% |
| scp42 | 200 | 1000 | 512 | 582 | +13.7% | 520 | +1.56% |
| scp43 | 200 | 1000 | 516 | 598 | +15.9% | 529 | +2.52% |
| scp44 | 200 | 1000 | 494 | 548 | +10.9% | 503 | +1.82% |
| scp51 | 200 | 2000 | 253 | 289 | +14.2% | 265 | +4.74% |
| scp52 | 200 | 2000 | 302 | 348 | +15.2% | 325 | +7.62% |
| scp53 | 200 | 2000 | 226 | 246 | +8.9% | 230 | +1.77% |
| scpa1 | 300 | 3000 | 253 | 288 | +13.8% | 259 | +2.37% |
| scpa2 | 300 | 3000 | 252 | 284 | +12.7% | 263 | +4.37% |
| scpa3 | 300 | 3000 | 232 | 270 | +16.4% | 241 | +3.88% |

The GA beat greedy on every instance, often by a large margin. Greedy gaps ranged from 8–16% above optimal, while GA gaps ranged from 0.9–7.6%. The largest remaining GA gap was scp52 at +7.62%, which is one of the larger and denser instances.

### 3.13 Observed Convergence Behavior

An important thing we noticed: on all tested instances, the GA triggered early stopping via entropy convergence at generation 1 (entropy ≈ 0.04 after the first full generation). This means the repair mechanism was powerful enough to push the entire population toward very similar solutions immediately after initialization. There was almost no genetic diversity left to evolve.

This is worth reflecting on. The repair-then-trim procedure effectively runs a greedy selection inside every chromosome evaluation. By the time generation 0 is fully evaluated, each chromosome is already a locally optimized valid solution. These solutions tend to look similar (same high-value sets get included), so entropy collapses before any crossover or mutation can run.

In practice the GA still found substantially better results than a plain greedy run — this is partly because the initialization samples many different starting configurations before repair, giving a wider spread of initial solutions than a single greedy pass. The best of those initial repairs is then kept and refined by the first generation.

If we were to continue this work, we would experiment with lower repair aggressiveness (e.g. only partially repairing chromosomes) to preserve more diversity and allow actual evolution to contribute. The current setup is essentially a parallel greedy search rather than a true evolutionary algorithm.

---

## 4. Conclusions

**Part A:** Even a simple heuristic like h1 makes a noticeable difference over BFS, reducing average node count by about 16% and EBF from 1.64 to 1.40. h2 improves further (EBF 1.39) but costs more per node, making it slower in wall time. All three algorithms found optimal solutions on all 40 puzzles, which confirms the admissibility argument. The biggest practical takeaway is that for this problem size, A\* with h1 is the right default — better node efficiency than BFS and faster per-node than h2.

**Part B:** The repair-based fitness function worked well: every chromosome is always valid, there is no penalty coefficient to tune, and the GA consistently reached within 1–8% of known optima — much better than the greedy baseline at 8–16% above optimal. The main limitation we found is that the repair mechanism is so aggressive it erases population diversity before evolution can happen. A less aggressive repair, or a different initialization strategy, would be needed to let the genetic operators contribute more meaningfully.
