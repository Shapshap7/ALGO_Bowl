# CSCI 406 AlgoBOWL Akari — Improved Solver and Optimizer

This project keeps the NetworkX graph-based input format while providing a valid, conflict-free baseline solution and a **second, optional optimization step** for reducing numbered-wall violations.

## Requirements

```powershell
python -m pip install networkx scipy
```

`networkx` is used by the baseline code. `scipy` is only required for the optional optimizer; it's **not** required to generate or validate a baseline solution.

## Run it from the folder containing these files

**1. Create a valid initial solution** (if you don't already have one):

```powershell
python outputFunction.py input_group1293.txt initial.txt 6
```

**2. Optimize numbered-wall violations** (keeps all cells lit and R1 conflicts at zero):

```powershell
python improveOutput.py input_group1293.txt initial.txt improved.txt --window 28 --passes 2 --time-limit 1.0
```

The optimizer automatically checkpoints `improved.txt` every 50 windows and at the end of each pass. It can read `improved.txt` as its next starting input in a later run. To try larger windows, use `--window 42` or increase `--passes`, at a greater runtime cost. Since it's a heuristic using *local* integer programming problems, results can vary and the final solution isn't necessarily optimal.

**3. Independently verify the file:**

```powershell
python validator.py input_group1293.txt improved.txt
```

Expected: `R1 conflicting bulbs: 0`, `Unlit blank cells: 0`, a correct score on the first line, and `VALID OUTPUT`.

## Your 10 × 10,000 test input

- **Original uploaded output** (`output(1).txt`): 19,076 conflicting bulbs + 5,622 wrong numbered walls and 4,305 unlit cells (invalid).
- **Corrected baseline**: 9,378 wrong numbered walls, 0 bulb conflicts, 0 unlit cells.
- **Optimized output:** **7,159** wrong numbered walls, **0** bulb conflicts, **0** unlit cells (valid).
- **Proven lower bound:** 2,115 numbered walls require more bulbs than there are immediately adjacent blank cells. Those specific violations are impossible to eliminate. The actual minimum may be even higher due to other constraints.

## Why the old program produced so many violations

- It never updated `isLit`, so it continued to place bulbs beside already illuminated cells.
- Its recursive bulb-conflict check started *on* the bulb, which triggered a false self-conflict.
- It incremented `curAdj` before finishing checks for other neighboring numbered cells, then removed bulbs without rolling back all affected counts.
- It did not place bulbs to light all of the cells away from numbered walls.
- It didn't write the total violation count as the first line of the output file.

## What the new program does

1. `inputGenerator.py`: Parses `rows columns` and builds the 2D grid and NetworkX graph.
2. `optimizedAkarialgorithm.py`: Identifies uninterrupted row/column segments and greedily chooses a **maximal matching** between them, then performs local swaps. This **guarantees every blank cell is lit without bulb conflicts**.
3. `outputFunction.py`: Writes a valid AlgoBOWL `output.txt` with a single violation count on the first line.
4. `improveOutput.py`: Uses SciPy's MILP solver on overlapping windows to reduce wrong numbered-wall counts while locking the rest of the board. Every accepted change preserves coverage and no bulb-to-bulb conflict.
5. `validator.py`: Independently checks R1, R2, illumination, unchanged input walls, output dimensions, claimed score, and the obvious forced-violation lower bound.

For AlgoBOWL grading, **check that any required runtime environment supports your dependencies**. `scipy` is optional; the bundled `output.txt` is already precomputed and doesn't need to be solved again to inspect.
