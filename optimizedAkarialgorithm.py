"""Akari heuristic: full illumination + no bulb conflicts, then optimize clues.

Rows and columns of open white cells are split into uninterrupted segments.
A bulb occupies one horizontal and one vertical segment. Selecting a maximal
matching between the segment sets guarantees every white cell is illuminated,
and selecting a matching guarantees no two bulbs see one another.

The input's NetworkX graph is updated so other team code can still inspect
node attributes (hasBulb, isLit, curAdj).
"""
import random
import inputGenerator


class SegmentSolver:
    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])
        R, C = self.rows, self.cols
        h = [[-1] * C for _ in range(R)]
        v = [[-1] * C for _ in range(R)]
        hn = vn = 0

        for r in range(R):
            for c in range(C):
                if board[r][c] == '.':
                    if c == 0 or board[r][c - 1] != '.':
                        hn += 1
                    h[r][c] = hn - 1
        for c in range(C):
            for r in range(R):
                if board[r][c] == '.':
                    if r == 0 or board[r - 1][c] != '.':
                        vn += 1
                    v[r][c] = vn - 1
        self.hn, self.vn = hn, vn
        self.positions = []
        self.eh, self.ev, self.adj = [], [], []
        self.hedges = [[] for _ in range(hn)]
        self.vedges = [[] for _ in range(vn)]
        self.clue_positions = []
        self.targets = []
        clue_at = {}
        for r in range(R):
            for c in range(C):
                if board[r][c] in "01234":
                    clue_at[r, c] = len(self.targets)
                    self.clue_positions.append((r, c))
                    self.targets.append(int(board[r][c]))

        for r in range(R):
            for c in range(C):
                if board[r][c] != '.':
                    continue
                i = len(self.positions)
                hi, vi = h[r][c], v[r][c]
                self.positions.append((r, c))
                self.eh.append(hi)
                self.ev.append(vi)
                self.hedges[hi].append(i)
                self.vedges[vi].append(i)
                around = []
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    idx = clue_at.get((r + dr, c + dc))
                    if idx is not None:
                        around.append(idx)
                self.adj.append(around)
        self.intersection = {
            (self.eh[i], self.ev[i]): i for i in range(len(self.positions))
        }

    def clue_counts(self, chosen):
        counts = [0] * len(self.targets)
        for i in chosen:
            for j in self.adj[i]:
                counts[j] += 1
        return counts

    def errors(self, chosen):
        counts = self.clue_counts(chosen)
        return sum(got != want for got, want in zip(counts, self.targets))

    def greedy(self, seed):
        """A weighted randomized *maximal matching*, not arbitrary placement."""
        rng = random.Random(seed)
        # Preference for cells adjoining positive numbers, and away from zeros.
        weights = {0: -10, 1: 2, 2: 2.5, 3: 3, 4: 5}
        order = list(range(len(self.positions)))
        priorities = [
            sum(weights[self.targets[j]] for j in self.adj[i]) + rng.random() * 4
            for i in order
        ]
        order.sort(key=lambda i: priorities[i], reverse=True)
        used_h = bytearray(self.hn)
        used_v = bytearray(self.vn)
        chosen = []
        for i in order:
            hi, vi = self.eh[i], self.ev[i]
            if not used_h[hi] and not used_v[vi]:
                used_h[hi] = used_v[vi] = 1
                chosen.append(i)
        return chosen

    def improve_single_swaps(self, chosen, seed, rounds=5):
        """Move one bulb in its horizontal/vertical segment if score improves."""
        rng = random.Random(seed)
        hm = [-1] * self.hn
        vm = [-1] * self.vn
        for i in chosen:
            hm[self.eh[i]] = vm[self.ev[i]] = i
        counts = self.clue_counts(chosen)
        chosen = list(chosen)

        for _ in range(rounds):
            rng.shuffle(chosen)
            improvements = 0
            for pos, old in enumerate(chosen):
                oh, ov = self.eh[old], self.ev[old]
                # The vacated segment must still be illuminated by bulbs
                # in the other orientation, except for the preserved segment.
                free_v_ok = all(self.eh[k] == oh or hm[self.eh[k]] != -1
                                for k in self.vedges[ov])
                free_h_ok = all(self.ev[k] == ov or vm[self.ev[k]] != -1
                                for k in self.hedges[oh])
                candidates = []
                if free_v_ok:
                    candidates.extend(self.hedges[oh])
                if free_h_ok:
                    candidates.extend(self.vedges[ov])
                best_delta, best = 0, None
                old_adj = set(self.adj[old])
                for new in candidates:
                    if new == old:
                        continue
                    nh, nv = self.eh[new], self.ev[new]
                    if hm[nh] not in (-1, old) or vm[nv] not in (-1, old):
                        continue
                    affected = old_adj | set(self.adj[new])
                    delta = sum(
                        (counts[j] - (j in old_adj) + (j in self.adj[new]) != self.targets[j])
                        - (counts[j] != self.targets[j])
                        for j in affected
                    )
                    if delta < best_delta:
                        best_delta, best = delta, new
                if best is not None:
                    for j in self.adj[old]:
                        counts[j] -= 1
                    for j in self.adj[best]:
                        counts[j] += 1
                    hm[oh] = vm[ov] = -1
                    hm[self.eh[best]] = vm[self.ev[best]] = best
                    chosen[pos] = best
                    improvements += 1
            if improvements == 0:
                break
        return chosen

    def improve_four_cycles(self, chosen, seed, rounds=3):
        """Swap endpoints of two selected bulbs across a 4-cycle.

        This preserves every occupied segment, so illumination and R1 stay valid.
        """
        rng = random.Random(seed)
        hm = [-1] * self.hn
        vm = [-1] * self.vn
        for i in chosen:
            hm[self.eh[i]] = vm[self.ev[i]] = i
        chosen = set(chosen)
        counts = self.clue_counts(chosen)
        for _ in range(rounds):
            changed = 0
            order = list(chosen)
            rng.shuffle(order)
            for a in order:
                if a not in chosen:
                    continue
                ah, av = self.eh[a], self.ev[a]
                for x in self.hedges[ah]:
                    xv = self.ev[x]
                    b = vm[xv]
                    if b == -1 or b == a:
                        continue
                    y = self.intersection.get((self.eh[b], av))
                    if y is None or x in chosen or y in chosen:
                        continue
                    sa, sb, sx, sy = map(lambda i: set(self.adj[i]), (a, b, x, y))
                    delta = 0
                    for j in sa | sb | sx | sy:
                        after = counts[j] - (j in sa) - (j in sb) + (j in sx) + (j in sy)
                        delta += (after != self.targets[j]) - (counts[j] != self.targets[j])
                    if delta < 0:
                        chosen.difference_update((a, b))
                        chosen.update((x, y))
                        hm[ah], vm[xv] = x, x
                        hm[self.eh[b]], vm[av] = y, y
                        for j in self.adj[a]: counts[j] -= 1
                        for j in self.adj[b]: counts[j] -= 1
                        for j in self.adj[x]: counts[j] += 1
                        for j in self.adj[y]: counts[j] += 1
                        changed += 1
                        break
            if changed == 0:
                break
        return list(chosen)

    def solve(self, attempts=6):
        best, best_score = None, float('inf')
        for seed in range(attempts):
            bulbs = self.greedy(seed)
            bulbs = self.improve_single_swaps(bulbs, seed, rounds=5)
            bulbs = self.improve_four_cycles(bulbs, seed, rounds=3)
            bulbs = self.improve_single_swaps(bulbs, seed + 4, rounds=3)
            errors = self.errors(bulbs)
            if errors < best_score:
                best, best_score = bulbs, errors
        return best, best_score


def alg(graphs, attempts=6):
    board, graph = graphs
    solver = SegmentSolver(board)
    selected, errors = solver.solve(attempts=attempts)
    used_h = bytearray(solver.hn)
    used_v = bytearray(solver.vn)
    clue_counts = solver.clue_counts(selected)

    for i in selected:
        r, c = solver.positions[i]
        board[r][c] = 'L'
        graph.nodes[(r, c)]['hasBulb'] = True
        used_h[solver.eh[i]] = 1
        used_v[solver.ev[i]] = 1
    for i, (r, c) in enumerate(solver.positions):
        graph.nodes[(r, c)]['isLit'] = bool(used_h[solver.eh[i]] or used_v[solver.ev[i]])
    for (r, c), count in zip(solver.clue_positions, clue_counts):
        graph.nodes[(r, c)]['curAdj'] = count
    print(f'Bulbs: {len(selected)} | R1: 0 | R2: {errors} | unlit: 0')
    return board


def main(path='input_group1293.txt', attempts=6):
    return alg(inputGenerator.main(path), attempts=attempts)


if __name__ == '__main__':
    main()
