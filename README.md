# AI Lab 1 - Search and Genetic Algorithms

This repository contains the solution for the AI Lab 1 assignment. It is divided into two main parts:

1. **Part A:** Rush Hour Puzzle Solver using Informed and Uninformed Search Algorithms (BFS, A* with custom heuristics).
2. **Part B:** Set Cover Problem Solver using an advanced Genetic Algorithm (incorporating smart initialization, elitism, repair heuristics, and redundancy exploitation).

## Project Structure

```
HW1/
├── src/                    # Source code
│   ├── part_a/             # Rush Hour Implementation
│   ├── part_b/             # Set Cover GA Implementation
│   └── utils/              # Visualization tools
├── data/                   # Datasets (rh.txt, scp*.txt)
├── docs/                   # Assignment PDFs and reports
├── scripts/                # Utility scripts (downloading datasets, parsing PDFs, old references)
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup & Installation

Ensure you have Python 3.9+ installed. Install the dependencies via:

```bash
pip install -r requirements.txt
```

## Running the Code

The project is orchestrated entirely through `main.py`.

### Part A: Rush Hour Solver

To run the Rush Hour solver on a specific puzzle:
```bash
python main.py part_a --board_file data/rh.txt --puzzle_index 1 --algorithm astar --heuristic h2
```

To run a batch evaluation on all 40 puzzles:
```bash
python main.py part_a --board_file data/rh.txt --batch --algorithm astar --heuristic h2
```

### Part B: Set Cover Genetic Algorithm

To run a single dataset visualization and see the convergence:
```bash
python main.py part_b --dataset data/setcover/scp41.txt --visualize
```

To run the full automated batch comparison over all 10 datasets, 3 configurations, and 5 seeds (Outputs to `results/` folder):
```bash
python main.py part_b --dataset data/setcover --experiment_batch
```

## GA Features
The Genetic Algorithm has been heavily optimized for the Set Cover problem:
- **Smart Repair:** Invalid solutions automatically select cheap sets to become valid.
- **Exploitation:** Redundant sets are automatically turned off.
- **Strong Elitism:** Top 10% of the population is preserved across generations.
- **Top-Half Mating:** Only the top 50% of the population is allowed to cross over.
