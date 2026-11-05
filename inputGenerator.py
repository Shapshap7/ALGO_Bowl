"""Read an AlgoBOWL Akari instance into a 2D grid and a NetworkX graph."""
import networkx as nx


def input(path="input_group1293.txt"):
    with open(path, encoding="utf-8") as f:
        rows, cols = map(int, f.readline().split())
        board = [list(f.readline().rstrip("\r\n")) for _ in range(rows)]

    if len(board) != rows or any(len(row) != cols for row in board):
        raise ValueError("Input dimensions don't match the first line")
    if any(ch not in ".X01234" for row in board for ch in row):
        raise ValueError("Input contains an invalid character")

    graph = nx.Graph()
    for r in range(rows):
        for c in range(cols):
            value = board[r][c]
            cell_type = "white" if value == "." else ("black" if value == "X" else "#black")
            graph.add_node(
                (r, c), cellType=cell_type,
                MaxAdj=int(value) if value in "01234" else None,
                curAdj=0, isLit=False, hasBulb=False
            )
            # Add each undirected edge only once.
            if r > 0:
                graph.add_edge((r, c), (r - 1, c))
            if c > 0:
                graph.add_edge((r, c), (r, c - 1))
    return board, graph


def main(path="input_group1293.txt"):
    return input(path)


if __name__ == "__main__":
    board, graph = main()
    print(f"Loaded {len(board)} x {len(board[0])} board with {graph.number_of_nodes()} nodes")
