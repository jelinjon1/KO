#!/usr/bin/env python3
import sys
import gurobipy as g

def main():
  input_path = sys.argv[1]
  output_path = sys.argv[2]

  with open(input_path, "r") as f:
    lines = f.readlines()

  d = list(map(int, lines[0].split(' ')))
  e = list(map(int, lines[1].split(' ')))
  D = int(lines[2])

  model = g.Model()
  
  x = model.addVars(168, vtype=g.GRB.INTEGER, name="shifts started")
  z = model.addVars(168, vtype=g.GRB.INTEGER, name="auxiliary var")

  for hour in range(168):
    zi = z[hour]
    coverage = g.quicksum(x[j%168] for j in range(hour - 7, hour + 1))
    
    demand = e[hour%24]
    if (hour <= 119):
      demand = d[hour%24]

    # model.addConstr(demand <= coverage)
    model.addConstr(demand - coverage <= zi)
    model.addConstr(coverage - demand <= zi)
    model.addConstr(zi >= 0)
    model.addConstr(demand - coverage <= D)

  model.setObjective(z.sum(), sense=g.GRB.MINIMIZE)
  # model.setObjective(x.sum(), sense=g.GRB.MINIMIZE)
  model.optimize()

  with open(output_path, "w") as f:
    f.write(str(int(round(model.ObjVal))) + "\n")
    f.write(" ".join(str(int(round(x[i].X))) for i in range(168)))

if __name__ == "__main__":
  main()