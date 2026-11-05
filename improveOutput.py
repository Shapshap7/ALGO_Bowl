"""Reduce Akari numbered-wall violations while keeping a valid, conflict-free board.

Usage:
  python -m pip install networkx scipy
  python improveOutput.py input_group1293.txt output.txt output_improved.txt

The optimization uses SciPy/HiGHS MILP on overlapping vertical windows. Each
window is solved with the rest of the puzzle fixed. The objective minimizes
incorrect numbered gray cells; constraints preserve illumination and R1=0.
This is a local optimizer, not a proof of the global optimum.
"""
import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array

from optimizedAkarialgorithm import SegmentSolver
from validator import count_violations, read_input


class LocalMILPOptimizer:
    def __init__(self, board, chosen, solver=None):
        self.solver = solver if solver is not None else SegmentSolver([list(row) for row in board])
        self.chosen = set(chosen)
        s = self.solver
        self.h_count = [0] * s.hn
        self.v_count = [0] * s.vn
        self.clue_count = [0] * len(s.targets)
        self.by_column = [[] for _ in range(s.cols)]
        self.clue_edges = [[] for _ in s.targets]
        for i, (r, c) in enumerate(s.positions):
            self.by_column[c].append(i)
            for j in s.adj[i]:
                self.clue_edges[j].append(i)
        for i in self.chosen:
            self._adjust(i, 1)
        if max(self.h_count, default=0) > 1 or max(self.v_count, default=0) > 1:
            raise ValueError('Starting board contains bulb conflicts; use outputFunction.py first.')
        self.score = sum(x != t for x, t in zip(self.clue_count, s.targets))
        self.impossible = sum(t > len(self.clue_edges[j]) for j, t in enumerate(s.targets))

    def _adjust(self, i, step):
        s = self.solver
        self.h_count[s.eh[i]] += step
        self.v_count[s.ev[i]] += step
        for j in s.adj[i]:
            self.clue_count[j] += step

    def optimize_window(self, start, stop, time_limit=1.0):
        s = self.solver
        ids = [i for c in range(start, min(stop, s.cols)) for i in self.by_column[c]]
        n = len(ids)
        if not n:
            return 0
        old = {i for i in ids if i in self.chosen}
        hvars, vvars, cluevars = defaultdict(list), defaultdict(list), defaultdict(list)
        for k, i in enumerate(ids):
            hvars[s.eh[i]].append(k)
            vvars[s.ev[i]].append(k)
            for j in s.adj[i]:
                cluevars[j].append(k)

        outside_h = {h: self.h_count[h] - sum(ids[k] in old for k in ks)
                     for h, ks in hvars.items()}
        outside_v = {v: self.v_count[v] - sum(ids[k] in old for k in ks)
                     for v, ks in vvars.items()}

        rows, cols, values, lb, ub = [], [], [], [], []

        def constraint(coeff, lower=-np.inf, upper=np.inf):
            j = len(lb)
            for k, value in coeff.items():
                rows.append(j)
                cols.append(k)
                values.append(float(value))
            lb.append(float(lower))
            ub.append(float(upper))

        # Never put multiple bulbs into one uninterrupted horizontal/vertical run.
        for h, ks in hvars.items():
            constraint({k: 1 for k in ks}, upper=1 - outside_h[h])
        for v, ks in vvars.items():
            constraint({k: 1 for k in ks}, upper=1 - outside_v[v])

        # Every white cell in a run touched by the window must remain illuminated.
        affected = set()
        for h in hvars:
            affected.update(s.hedges[h])
        for v in vvars:
            affected.update(s.vedges[v])
        added_coverage = set()
        for i in affected:
            h, v = s.eh[i], s.ev[i]
            existing_h = outside_h[h] if h in outside_h else self.h_count[h]
            existing_v = outside_v[v] if v in outside_v else self.v_count[v]
            if existing_h or existing_v:
                continue
            candidate_vars = set(hvars.get(h, [])) | set(vvars.get(v, []))
            key = tuple(sorted(candidate_vars))
            if not key:
                raise ValueError('A cell has no possible illuminating bulb.')
            if key not in added_coverage:
                added_coverage.add(key)
                constraint({k: 1 for k in key}, lower=1)

        # For each numbered wall, penalty y_j=1 permits an incorrect count.
        # Impossible walls are already fixed violations, so no variable needed.
        adjustable = [j for j in cluevars
                      if s.targets[j] <= len(self.clue_edges[j])]
        for z, j in enumerate(adjustable):
            ks = cluevars[j]
            outside = self.clue_count[j] - sum(ids[k] in old for k in ks)
            needed = s.targets[j] - outside
            coeff = {k: 1 for k in ks}
            constraint({**coeff, n + z: -4}, upper=needed)
            constraint({**coeff, n + z: 4}, lower=needed)

        variables = n + len(adjustable)
        mat = coo_array(
            (np.asarray(values, dtype=np.float64),
             (np.asarray(rows, dtype=np.int32), np.asarray(cols, dtype=np.int32))),
            shape=(len(lb), variables)
        ).tocsr()
        objective = np.concatenate((np.full(n, 0.0001), np.ones(len(adjustable))))
        result = milp(
            objective, integrality=np.ones(variables, dtype=np.int32),
            bounds=Bounds(np.zeros(variables), np.ones(variables)),
            constraints=LinearConstraint(mat, np.asarray(lb), np.asarray(ub)),
            options={'time_limit': time_limit, 'mip_rel_gap': 0.01}
        )
        if result.x is None:
            return 0
        new = {ids[k] for k in range(n) if result.x[k] > 0.5}

        # Calculate the *actual* difference, independently of the MILP objective.
        before = sum(self.clue_count[j] != s.targets[j] for j in cluevars)
        after = sum(
            (self.clue_count[j]
             - sum(i in old for i in self.clue_edges[j])
             + sum(i in new for i in self.clue_edges[j])) != s.targets[j]
            for j in cluevars
        )
        change = after - before
        if change <= 0:
            for i in old - new:
                self._adjust(i, -1)
            for i in new - old:
                self._adjust(i, +1)
            self.chosen.difference_update(old - new)
            self.chosen.update(new - old)
            self.score += change
        return min(change, 0)

    def write_output(self, original, destination):
        s = self.solver
        rows = [list(row) for row in original]
        for i in self.chosen:
            r, c = s.positions[i]
            rows[r][c] = 'L'
        text_rows = [''.join(row) for row in rows]
        r1, r2, unlit = count_violations(original, text_rows)
        assert r1 == 0 and unlit == 0 and r2 == self.score, (r1, r2, unlit, self.score)
        Path(destination).write_text(str(self.score) + '\n' + '\n'.join(text_rows) + '\n', encoding='utf-8')
        return self.score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Original Akari puzzle text file')
    parser.add_argument('existing', help='Valid, conflict-free output text file to improve')
    parser.add_argument('improved', help='Where to write the improved output')
    parser.add_argument('--window', type=int, default=28)
    parser.add_argument('--passes', type=int, default=2)
    parser.add_argument('--time-limit', type=float, default=1.0,
                        help='Seconds allowed per small optimization window')
    args = parser.parse_args()
    if args.window < 2 or args.passes < 1 or args.time_limit <= 0:
        parser.error('window >= 2, passes >= 1 and time-limit > 0 are required')
    original = read_input(args.input)
    data = Path(args.existing).read_text(encoding='utf-8').splitlines()
    try:
        declared = int(data[0])
    except (ValueError, IndexError) as e:
        raise ValueError('Existing output must have the score on the first line') from e
    r1, r2, unlit = count_violations(original, data[1:])
    if (r1, unlit) != (0, 0) or r1 + r2 != declared:
        raise ValueError(f'Existing solution must be valid with R1=0: got R1={r1}, R2={r2}, unlit={unlit}')
    solver = SegmentSolver([list(row) for row in original])
    indices = {pos: i for i, pos in enumerate(solver.positions)}
    chosen = [indices[r, c] for r, line in enumerate(data[1:]) for c, cell in enumerate(line) if cell == 'L']
    optimizer = LocalMILPOptimizer(original, chosen, solver=solver)
    print(f'Starting violations: {optimizer.score} | Proven impossible walls: {optimizer.impossible}', flush=True)
    for pass_no in range(args.passes):
        offset = (pass_no % 2) * (args.window // 2)
        improvement = 0
        for count, start in enumerate(range(offset, solver.cols, args.window), start=1):
            improvement += optimizer.optimize_window(start, start + args.window, args.time_limit)
            if count % 50 == 0:
                optimizer.write_output(original, args.improved)
                print(f'Pass {pass_no + 1}: {count} windows, score {optimizer.score}', flush=True)
        optimizer.write_output(original, args.improved)
        print(f'Finished pass {pass_no + 1}: {optimizer.score} violations ({improvement:+d})', flush=True)
    print(f'Wrote verified solution to {args.improved}', flush=True)


if __name__ == '__main__':
    main()
