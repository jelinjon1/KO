#!/usr/bin/env python3
import sys
import gurobipy as g

'''
  Verze kódu, kde jsem se pokusil změnit variable definition na dvě 2D pole místo jednoho 3D
  Momentálně infeasible
'''

print("TIMESTAMP:", __file__, flush=True)
import time; print(time.time(), flush=True)
# 1778276597.1546643
# 1778276607.9048347

def arc_feasible(u, v, T, Tlower, Tupper, N):
    if v == 0:
        return True
    if u == 0:
        return T[0][v] <= Tupper[v-1]
    return Tlower[u-1] + T[u][v] <= Tupper[v-1]

def main():
  # input_path = sys.argv[1]
  input_path = "./homework/contest2/instances/test1.txt"
  # output_path = sys.argv[2]
  output_path = "./homework/contest2/public-1-out.txt"

  with open(input_path, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

  # customers, max vans, van capacity, van cost
  N, K, Q, G = map(int, lines[0].split())

  parcelSizes = [0 for i in range(N)]
  Tlower = [0 for i in range(N)]
  Tupper = [0 for i in range(N)]

  maxT = 0

  for d in range(1, N+1):
    # parcel size, time window lower bound, time window upper bound
    si, til, tiu = map(int, lines[d].split())

    if (tiu > maxT):
      maxT = tiu
    
    parcelSizes[d - 1] = si
    Tlower[d - 1] = til
    Tupper[d - 1] = tiu

  # T[u, v] = time from Cu to Cv
  T = [ [0]*(N+1) for i in range(N+1)]
  j = 0
  for d in range(N+1, 2*N+2):
    T[j] = [int(x) for x in map(int, lines[d].split())]
    j += 1

  # C[u, v] = cost? from Cu to Cv
  C = [ [0]*(N+1) for i in range(N+1)]
  j = 0
  for d in range(2*N+2, 3*N+3):
    C[j] = [int(x) for x in map(int, lines[d].split())]
    j += 1

  model = g.Model()
  # model.Params.MIPFocus = 1
  # model.Params.TimeLimit = 28
  model.Params.Presolve = 0
  model.Params.Aggregate = 0

  valid_arcs = [
    (u, v)
    for u in range(N+1)
    for v in range(N+1)
    if u != v and arc_feasible(u, v, T, Tlower, Tupper, N)
  ]

  for v in range(1, N+1):
    incoming = [(u,v) for (u,w) in valid_arcs if w == v]
    outgoing = [(v,w) for (u,w) in valid_arcs if u == v]
    print(f"Node {v}: incoming={incoming}, outgoing={outgoing}")
  
  '''
  2)
  a[u, v] = 1 if any truck goes from u to v
  b[u, d] = 1 if truck d visits node u
  c[u] = t arrival time of the one truck that visits u
  
  s.t.:
    c[v] <= c[u] + d[u, v] for each a[u, v] == 1
    ...
  '''

  # travels[u,v] = 1 if ANY truck travels arc (u,v)
  travels = model.addVars(valid_arcs, vtype=g.GRB.BINARY, name="travels")

  # visits[u,d] = 1 if truck d visits node u
  visits = model.addVars([(u,d) for u in range(N+1) for d in range(K)], vtype=g.GRB.BINARY, name="visits")

  # t[u] = arrival time at node u
  t = model.addVars(N+1, lb=0, ub=g.GRB.INFINITY, vtype=g.GRB.INTEGER, name="t")
  model.update()
  t[0].ub = 0  # force t[0] = 0 via bounds, not just constraint

  # auxilary z[i] = 1 iff truck 1 was used, 0 otherwise
  z = model.addVars(K, vtype=g.GRB.BINARY, name="z")

  for d in range(K):
    model.addConstr(visits[0,d] == z[d])
  # for d in range(K):
  #   model.addConstr(visits.sum("*", d) <= z[d] * (N+1))
  #   model.addConstr(z[d] <= visits.sum("*", d))

  for d in range(K-1):
    model.addConstr(z[d] >= z[d+1])
  

  # incoming
  for v in range(1, N+1):
      model.addConstr(g.quicksum(travels[i,v] for (i,j) in valid_arcs if j == v) == 1)

  # outgoing
  for u in range(1, N+1):
      model.addConstr(g.quicksum(travels[u,j] for (i,j) in valid_arcs if i == u) == 1)

  # depot
  model.addConstr(g.quicksum(travels[0,j] for (i,j) in valid_arcs if i == 0) == g.quicksum(z[d] for d in range(K)))
  model.addConstr(g.quicksum(travels[i,0] for (i,j) in valid_arcs if j == 0) == g.quicksum(z[d] for d in range(K)))

  # flow conservation on travels: exactly one arc in and out per customer
  # for v in range(1, N+1):
  #     model.addConstr(travels.sum("*", v) == 1)
  # for u in range(1, N+1):
  #     model.addConstr(travels.sum(u, "*") == 1)
  
  # depot arcs limited by trucks used
  # model.addConstr(travels.sum(0, "*") == g.quicksum(z[d] for d in range(K)))
  # model.addConstr(travels.sum("*", 0) == g.quicksum(z[d] for d in range(K)))

  # linking
  # if truck d visits u and arc (u,v) is traveled, then truck d visits v
  for d in range(K):
    for (i,j) in valid_arcs:
        if j != 0:
            model.addConstr(visits[j,d] >= visits[i,d] + travels[i,j] - 1)
  # permits visits[v, d] = 1 >= visits[u, d] = 0 + travels[u, v] = 1 - 1
  # permits visits[v, d] = 1 >= visits[u, d] = 1 + travels[u, v] = 0 - 1
  
  # if arc (i,j) is traveled, exactly one truck must claim both endpoints
  for (i,j) in valid_arcs:
      if i != 0 and j != 0:
          for d in range(K):
              model.addConstr(visits[i,d] >= visits[j,d] + travels[i,j] - 1)
              # backward direction too — if j is visited by d and arc used, i must be d
  
  for d in range(K):
    for (i,j) in valid_arcs:
        if i != 0 and j != 0:
            model.addConstr(visits[i,d] >= visits[j,d] + travels[i,j] - 1)

  # each customer visited by exactly one truck
  for u in range(1, N+1):
      model.addConstr(g.quicksum(visits[u,d] for d in range(K)) == 1)

  # depot handled via z as before
  for d in range(K):
    model.addConstr(visits[0,d] == z[d])

  # capacity per truck
  for d in range(K):
      model.addConstr(
          g.quicksum(parcelSizes[v-1] * visits[v,d] for v in range(1,N+1)) <= Q
      )

  # arrival times — no truck dimension needed
  for v in range(1, N+1):
      model.addConstr(t[v] >= Tlower[v-1])
      model.addConstr(t[v] <= Tupper[v-1])

  Mt = maxT - min(Tlower)
  # sequencing
  for (i,j) in valid_arcs:
      if j != 0:
          model.addConstr(t[j] >= t[i] + T[i][j] - Mt * (1 - travels[i,j]))

  # objective
  model.setObjective(
      g.quicksum(travels[i,j] * C[i][j] for (i,j) in valid_arcs)
      + g.quicksum(z[d] * G for d in range(K)),
      g.GRB.MINIMIZE
  )

  model.optimize()
  print(f"MODEL HAS {model.NumVars} vars and {model.NumConstrs} constrs")
  print(f"Status: {model.status}, SolCount: {model.SolCount}")
  
  # for d in range(K):
  #   visited = [u for u in range(1,N+1) if visits[u,d].X > 0.5]
  #   visited.sort(key=lambda u: t[u].X)
  #   print(f"Truck {d}: {visited.__str__}" )
  #   for u in visited:
  #      print(f"{u} -> arrived at {t[u].X}")
    

  with open(output_path, "w") as f:
    if model.status == g.GRB.INFEASIBLE or model.SolCount == 0:
      f.write("-1")
      model.computeIIS()
      model.write("model1.ilp")
      model.computeIIS()
      for c in model.getConstrs():
          if c.IISConstr:
              print(f"IIS: {c.ConstrName}")
      for v in model.getVars():
          if v.IISLB or v.IISUB:
              print(f"IIS bound: {v.VarName} lb={v.lb} ub={v.ub}")
      return

    vansUsed = sum(int(z[d].X) for d in range(K))

    f.write(f"{float(round(model.ObjVal))} {vansUsed}\n")

    for d in range(K):
      # skip unused vans
      if (z[d].X < 0.5):
        continue

if __name__ == "__main__":
  main()
