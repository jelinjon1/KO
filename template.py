#!/usr/bin/env python3
import sys
import gurobipy as g
import numpy

def my_callback(model, where):
  if where == g.GRB.Callback.MIPSOL:
    
    x = model._x
    n = model._n
    
    solution = model.cbGetSolution(x)
    
    if 1:
      model.cbLazy(1 <= 2)

def main():
  input_path = sys.argv[1]
  # input_path = "./homework/02_TSP_image_shredding/instances/triangle.txt"
  output_path = sys.argv[2]
  # output_path = "./homework/02_TSP_image_shredding/output.txt"

  with open(input_path, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

  conf1, onf2, onf3 = map(int, lines[0].split())

  model = g.Model()
#   model.Params.lazyConstraints = 1

  x = model.addVars(conf1, conf1, vtype=g.GRB.BINARY, name="x")
  
  model._x = x
  model._n = conf1
  
  for i in range(conf1):
    model.addConstr(x.sum(i, '*') == 1)
    model.addConstr(x.sum('*', i) == 1)
    model.addConstr(x[i, i] == 0)
  
  model.setObjective(
    g.quicksum(x[i, j] * x[i, j] for i in range(conf1) for j in range(conf1)),
    g.GRB.MINIMIZE
  )
  model.optimize(my_callback)

  with open(output_path, "w") as f:
    f.write(str(int(round(model.ObjVal))) + "\n")
    f.write(" ".join(str(int(round(x[i].X))) for i in range(168)))

if __name__ == "__main__":
  main()
