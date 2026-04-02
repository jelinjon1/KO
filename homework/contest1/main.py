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
#   input_path = sys.argv[1]
  input_path = "./hw/contest1/instances/public-1.txt"
#   output_path = sys.argv[2]
  output_path = "./hw/contest1/instances/public-1-out.txt"

  with open(input_path, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

  N, K, Q, G = map(int, lines[0].split())

  params = {}

  for i in range(1, N+1):
    si, til, tiu = map(int, lines[i].split())
    params[i]["size"] = si
    params[i]["time_l"] = til
    params[i]["time_u"] = tiu

  T = int[N+1][N+1]
  for i in range(N+1, 2*N+1):
    T[i%N-1] = lines[i]

  C = int[N+1][N+1]
  for i in range(2*N+1, 3*N+1):
    C[i%N-1] = lines[i]

  model = g.Model()
#   model.Params.lazyConstraints = 1

  # was truck used
  # 1 if yes, 0 no
  x = model.addVars(G, vtype=g.GRB.BINARY, name="x")
  s = model.addVars(N, vtype=g.GRB.INTEGER, name="start times")

#   pathCost = g.quicksum( + )
  
#   for i in range(conf1):
#     model.addConstr(x.sum(i, '*') == 1)
#     model.addConstr(x.sum('*', i) == 1)
#     model.addConstr(x[i, i] == 0)
  
#   model.setObjective(
#     g.quicksum(x[i, j] * x[i, j] for i in range(conf1) for j in range(conf1)),
#     g.GRB.MINIMIZE
#   )
  model.optimize(my_callback)

  with open(output_path, "w") as f:
    f.write(str(int(round(model.ObjVal))) + "\n")
    f.write(" ".join(str(int(round(x[i].X))) for i in range(168)))

if __name__ == "__main__":
  main()
