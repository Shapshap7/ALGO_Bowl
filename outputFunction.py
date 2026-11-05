"""Build an Akari solution and write the required AlgoBOWL output format."""
import sys
import optimizedAkarialgorithm
from validator import read_input, count_violations


def main(input_path='input_group1293.txt', output_path='output.txt', attempts=6):
    original = read_input(input_path)
    result = optimizedAkarialgorithm.main(input_path, attempts=attempts)
    final_board = [''.join(row) for row in result]
    r1, r2, unlit = count_violations(original, final_board)
    if unlit:
        raise RuntimeError(f'Solver left {unlit} cells unlit')
    with open(output_path, 'w', encoding='utf-8', newline='\n') as out:
        out.write(f'{r1 + r2}\n')  # Output must start with ONE integer, not '10 10000'
        for row in final_board:
            out.write(row + '\n')
    print(f'Wrote {output_path} with {r1 + r2} violations')


if __name__ == '__main__':
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'input_group1293.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'output.txt'
    attempts = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    main(input_path, output_path, attempts)
