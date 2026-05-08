# AI Lab 1 - Search and Genetic Algorithms

This repository contains the solution for the AI Lab 1 assignment, split into two parts:

1. **Part A** – Rush Hour puzzle solver using BFS and A* with custom heuristics.
2. **Part B** – Set Cover solver using a Genetic Algorithm.

## Project Structure

- `src/` – Source code (part_a, part_b, utils)
- `data/` – Datasets (`rh.txt`, `scp*.txt`)
- `docs/` – Assignment PDFs and reports
- `main.py` – Application entry point
- `requirements.txt` – Python dependencies
- `README.md` – This file

## Setup & Installation

Ensure Python 3.9+ is installed and run:

pip install -r requirements.txt

## Running the Code

All functionality is accessed through `main.py`.

- **Part A – Rush Hour Solver**
  - Run a specific puzzle:
    python main.py part_a --board_file data/rh.txt --puzzle_index 1 --algorithm astar --heuristic h2
  - Run batch evaluation on all puzzles:
    python main.py part_a --board_file data/rh.txt --batch --algorithm astar --heuristic h2

- **Part B – Set Cover Solver**
  - Visualize a single dataset:
    python main.py part_b --dataset data/setcover/scp41.txt --visualize
  - Run full batch comparison on all datasets:
    python main.py part_b --dataset data/setcover --experiment_batch

## Input Formats

- **Rush Hour (`rh.txt`)**: Each puzzle is a single line of 36 characters representing a 6×6 board read row‑wise. Empty cells are `.`; each vehicle is identified by a unique character.
- **Set Cover (`scp*.txt`)**: Files specify the number of elements `m`, the number of sets `n`, followed by `n` lines describing each set (list of element indices). This follows the standard Set Cover problem format.

## GA Features

- Smart repair for invalid solutions
- Elitism and top‑half mating strategies
- Configurable mutation and crossover rates

This repository contains the solution for the AI Lab 1 assignment. It is divided into two main parts:

1. **Part A:** Rush Hour Puzzle Solver using Informed and Uninformed Search Algorithms (BFS, A* with custom heuristics).
2. **Part B:** Set Cover Problem Solver using an advanced Genetic Algorithm (incorporating smart initialization, elitism, repair heuristics, and redundancy exploitation).

## Project Structure

```
HW1/
├── src/                    # Source code
├── data/                   # Datasets
├── main.py                 # Entry point
└── README.md               # This file
```

## Input Formats
- **Rush Hour:** Text files specifying board dimensions and vehicle coordinates.
- **Set Cover:** Standard SCP text format defining universe elements and available sets with associated costs.

## Running the Code
- **Rush Hour:** `python main.py part_a --board_file <file> --algorithm <alg>`
- **Set Cover:** `python main.py part_b --dataset <file> --visualize`

## GA Features
- **Smart Repair:** Invalid solutions automatically select cheap sets to become valid.
- **Exploitation:** Redundant sets are automatically turned off.
- **Strong Elitism:** Top 10% of the population is preserved across generations.
- **Top-Half Mating:** Only the top 50% of the population is allowed to cross over.
