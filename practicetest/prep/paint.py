#!/usr/bin/env python3
import sys
import gurobipy as g


def main():
    #   input_path = sys.argv[1]
    input_path = "./practicetest/2.txt"
    #   output_path = sys.argv[2]
    output_path = "./practicetest/2-out.txt"

    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # houses, pairs, paint types
    n, m, c = map(int, lines[0].split())

    cost = []
    volume = []
    for i in range(1, c + 1):
        ci, vi = map(int, lines[i].split())
        cost.append(ci)
        volume.append(vi)

    edges = []
    for i in range(c + 1, c + 1 + m + 1):
        u, v = map(int, lines[i].split())
        edges.append((u - 1, v - 1))

    model = g.Model()

    # Variables: x[i,k] = 1 if house i uses color k
    x = model.addVars(n, c, vtype=g.GRB.BINARY, name="x")

    # Each house gets exactly one color
    for i in range(n):
        model.addConstr(g.quicksum(x[i, k] for k in range(c)) == 1)
        # model.addConstr(x.sum(i, "*") == 1)

    # Adjacent houses cannot share color
    for u, v in edges:
        for k in range(c):
            model.addConstr(x[u, k] + x[v, k] <= 1)

    # Volume constraints
    for k in range(c):
        model.addConstr(g.quicksum(x[i, k] for i in range(n)) <= volume[k])

    # Objective: minimize cost
    model.setObjective(
        g.quicksum(cost[k] * x[i, k] for i in range(n) for k in range(c)),
        g.GRB.MINIMIZE,
    )

    model.optimize()

    with open(output_path, "w") as f:
        if model.status != g.GRB.OPTIMAL:
            f.write("-1\n")
            return

        for i in range(n):
            for k in range(c):
                if x[i, k].X > 0.5:
                    f.write(f"{k+1}\n")
                    break


if __name__ == "__main__":
    main()
