#!/usr/bin/env python3
import sys
import gurobipy as g


def main():
    #   input_path = sys.argv[1]
    input_path = "./practicetest/1.txt"
    #   output_path = sys.argv[2]
    output_path = "./practicetest/1-out.txt"

    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # rooks
    N = int(lines[0])

    cols = []
    rows = []

    for i in range(1, N + 1):
        coords = lines[i]

        col = ord(coords[0]) - ord("a")
        row = int(coords[1]) - 1

        cols.append(col)
        rows.append(row)

    model = g.Model()

    # 1 if placed on field [i, j], 0 no
    x = model.addVars(8, 8, vtype=g.GRB.BINARY, name="knight placements")

    for i in range(N):
        # in column and row of the rook placement, no knights
        model.addConstr(x.sum(rows[i], "*") == 0)
        model.addConstr(x.sum("*", cols[i]) == 0)

    moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    for i in range(8):
        for j in range(8):
            for di, dj in moves:
                ni, nj = i + di, j + dj
                if 0 <= ni < 8 and 0 <= nj < 8:
                    model.addConstr(x[i, j] + x[ni, nj] <= 1)

    model.setObjective(x.sum(), g.GRB.MAXIMIZE)
    model.optimize()

    with open(output_path, "w") as f:
        # f.write(str(int(round(model.ObjVal))) + "\n")

        for i in range(8):
            f.write(" ".join(str(int(round(x[i, j].X))) for j in range(8)))
            f.write("\n")


if __name__ == "__main__":
    main()
