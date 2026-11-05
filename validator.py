"""Independent Akari output checker for an AlgoBOWL input/output pair."""
import sys


def read_input(path):
    with open(path, encoding='utf-8') as f:
        rows, cols = map(int, f.readline().split())
        data = [f.readline().rstrip('\r\n') for _ in range(rows)]
    assert len(data) == rows and all(len(x) == cols for x in data)
    return data


def count_violations(original, output):
    R, C = len(original), len(original[0])
    if len(output) != R or any(len(row) != C for row in output):
        raise ValueError('Output has incorrect grid dimensions')

    for r in range(R):
        for c in range(C):
            if original[r][c] == '.':
                if output[r][c] not in '.L':
                    raise ValueError(f'Invalid bulb placement at {(r, c)}')
            elif original[r][c] != output[r][c]:
                raise ValueError(f'Original clue was modified at {(r, c)}')

    lit_h = [bytearray(C) for _ in range(R)]
    lit_v = [bytearray(C) for _ in range(R)]
    conflicting = set()
    blocked = 'X01234'

    for r in range(R):
        c = 0
        while c < C:
            if output[r][c] in blocked:
                c += 1
                continue
            start = c
            bulbs = []
            while c < C and output[r][c] not in blocked:
                if output[r][c] == 'L':
                    bulbs.append((r, c))
                c += 1
            if bulbs:
                lit_h[r][start:c] = b'\x01' * (c - start)
            if len(bulbs) > 1:
                conflicting.update(bulbs)

    for c in range(C):
        r = 0
        while r < R:
            if output[r][c] in blocked:
                r += 1
                continue
            start = r
            bulbs = []
            while r < R and output[r][c] not in blocked:
                if output[r][c] == 'L':
                    bulbs.append((r, c))
                r += 1
            if bulbs:
                for rr in range(start, r):
                    lit_v[rr][c] = 1
            if len(bulbs) > 1:
                conflicting.update(bulbs)

    unlit = 0
    r2 = 0
    for r in range(R):
        for c in range(C):
            cell = output[r][c]
            if cell == '.' and not (lit_h[r][c] or lit_v[r][c]):
                unlit += 1
            if cell in '01234':
                neighbors = sum(
                    0 <= r + dr < R and 0 <= c + dc < C
                    and output[r + dr][c + dc] == 'L'
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
                )
                if neighbors != int(cell):
                    r2 += 1
    return len(conflicting), r2, unlit


def forced_wall_lower_bound(original):
    """Number of clues that are impossible even without considering other clues."""
    rows, cols = len(original), len(original[0])
    impossible = 0
    for r in range(rows):
        for c in range(cols):
            target = original[r][c]
            if target not in '01234':
                continue
            available = sum(
                0 <= r + dr < rows and 0 <= c + dc < cols
                and original[r + dr][c + dc] == '.'
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
            )
            if available < int(target):
                impossible += 1
    return impossible


def validate(original_path, output_path):
    original = read_input(original_path)
    with open(output_path, encoding='utf-8') as f:
        claimed = int(f.readline().strip())
        output = [x.rstrip('\r\n') for x in f]
    r1, r2, unlit = count_violations(original, output)
    print(f'R1 conflicting bulbs: {r1}')
    print(f'R2 incorrect numbered cells: {r2}')
    print(f'Unlit blank cells: {unlit}')
    print(f'Total violations: {r1 + r2} (file claims {claimed})')
    print(f'Forced impossible numbered walls (lower bound): {forced_wall_lower_bound(original)}')
    assert unlit == 0, 'INVALID: not every cell is lit'
    assert claimed == r1 + r2, 'INVALID: claimed score does not match'
    print('VALID OUTPUT')
    return r1 + r2


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: python validator.py input.txt output.txt')
    validate(sys.argv[1], sys.argv[2])
