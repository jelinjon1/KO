#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy


def main():
    input_path = sys.argv[1]
    # input_path = "./test/instances/inst4.txt"
    output_path = sys.argv[2]
    # output_path = "./test/1-out.txt"

    with open(input_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # family members, boats, incompatiblity pairs
    n, m, r = map(int, lines[0].split())

    weights = [int(x) for x in map(int, lines[1].split())]
    capacities = [int(x) for x in map(int, lines[2].split())]
    prices = [int(x) for x in map(int, lines[3].split())]

    if sum(capacities) < sum(weights):
        with open(output_path, "w") as f:
            f.write(str(-1))
        return

    incompatibilities = []
    for i in range(4, r + 4):
        u, v = map(int, lines[i].split())
        incompatibilities.append((u, v))

    model = g.Model()

    # x[i, j] = 1 ~ boat i carries person j
    x = model.addVars(m, n, vtype=g.GRB.BINARY, name="x")

    # z[i] = 1 ~ boat i was hired
    # sum of x[i, j] for boat i is > 0
    z = model.addVars(m, vtype=g.GRB.BINARY, name="z")
    M = n + 1
    for i in range(m):
        model.addConstr(z[i] <= 1)
        model.addConstr(x.sum(i, "*") <= z[i] * M)
        model.addConstr(z[i] <= x.sum(i, "*"))

    # a person is carried exactly once
    # for each person, the sum of him being carried by all the
    for i in range(n):
        model.addConstr(x.sum("*", i) == 1)

    # pro kazdou lod musime dodrzet kapacitu
    # for each boat
    # the sum of weights of each person being carried is less than or equal to the boat capacity
    for i in range(m):
        model.addConstr(
            g.quicksum(x[i, k] * weights[k] for k in range(n)) <= capacities[i]
        )

    # pro kazdyho family membera nemuze bejt na ty stejny lodi nikdo z jeho incompatible dvojice
    for u, v in incompatibilities:
        for i in range(m):
            model.addConstr(x[i, u] + x[i, v] <= 1)

    # udelat binary na to jesli je boat hired
    model.setObjective(
        g.quicksum(z[i] * prices[i] for i in range(m)),
        g.GRB.MINIMIZE,
    )
    model.optimize()

    with open(output_path, "w") as f:
        if model.status != g.GRB.OPTIMAL:
            f.write("-1")
            return
        for i in range(n):
            for j in range(m):
                if x[j, i].X > 0.5:
                    f.write(f"{j}")
                    if i < n - 1:
                        f.write(" ")
                    break


if __name__ == "__main__":
    main()
