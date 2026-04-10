#!/usr/bin/env python3
import sys
import gurobipy as g

# visit all clients along the path from depot
# note arrival times for client idx
def extractRoute(x, t, d, N):
  route = []
  times = []

  current = 0

  while True:
    found = False
    for v in range(N+1):
      if (x[current, v, d].X > 0.5):
        
        # returned to depot - finished
        if v == 0:
          return route, times

        route.append(v)
        times.append(int(round(t[v].X)))

        current = v
        found = True
        break

    if not found:
      break

  return route, times

def main():
  # input_path = sys.argv[1]
  input_path = "./homework/contest1/instances/public-1.txt"
  # output_path = sys.argv[2]
  output_path = "./homework/contest1/public-1-out.txt"

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

  # x[u, v, d] = 1 iff truck d goes from customer u to customer v
  x = model.addVars(N+1, N+1, K, vtype=g.GRB.BINARY, name="x")
  
  # t[u, d] arrival time of truck d to customer u
  t = model.addVars(N+1, lb=0, ub=maxT, vtype=g.GRB.INTEGER, name="t")
  
  # auxilary z[i] = 1 iff truck 1 was used, 0 otherwise
  # sum of all outgoing edges from depot for said truck <= z[d]
  z = model.addVars(K, vtype=g.GRB.BINARY, name="z")
  
  for d in range(K-1):
    model.addConstr(z[d] >= z[d+1])

  load = model.addVars(N+1, K, lb=0, ub=Q, vtype=g.GRB.CONTINUOUS, name="load")
  for d in range(K):
    for u in range(N+1):
      for v in range(1, N+1):
        if u != v:
          model.addConstr(
            load[v, d] >= load[u, d] + parcelSizes[v-1] - Q * (1 - x[u, v, d])
          )
  for d in range(K):
    model.addConstr(load[0, d] == 0)

  # must start and end in depot if at all
  # sum of out and in edges for the depot node  euqal binary truck used variable
  for d in range(K):
    model.addConstr(x.sum(0, "*", d) == z[d])
    model.addConstr(x.sum("*", 0, d) == z[d])
  
  # deliver all packages - exactly one edge enters each node, excl depots
  for v in range(1, N+1):
    model.addConstr(x.sum("*", v, "*") == 1)
    # model.addConstr(x.sum(customer, "*", "*") == 1)

  # kirchhoff law for entering and leaving node
  for d in range(K):
    for u in range(1, N+1):
      model.addConstr(x.sum(u, "*", d) == x.sum("*", u, d))

  # capacity
  # DO NOT REMOVE, had a generally positive effect on time complexity
  for d in range(K):
    model.addConstr(
      g.quicksum(
        parcelSizes[v-1] * x[u, v, d] for u in range(N+1) for v in range(1, N+1)
      ) <= Q
    )

  Mt = maxT - min(Tlower)
  # Mt = maxT
  # Mt = maxT + max(max(row) for row in T)

  # arrival times
  for d in range(K):
    # default arrival times for depots is 0
    model.addConstr(t[0] == 0)
    # fit within timewindows for each travel to u, only applies if truck visits u
    for u in range(1, N+1):
      model.addConstr(t[u] >= Tlower[u-1] - Mt * (1 - x.sum("*", u, d)))
      model.addConstr(t[u] <= Tupper[u-1] + Mt * (1 - x.sum("*", u, d)))

  # forbid self loops
  # and handle time sequencing within the route of each truck
  for d in range(K):
    for u in range(N+1):

      # forbid self loops
      model.addConstr(x[u, u, d] == 0)

      # for each pair of clients and each truck, the time to arrive at v >= time
      # to arrvie at u + T[u, v], if v comes immmediately after u in a sequence
      for v in range(1, N+1):
        # if (u != v) and (T[u][v] <= Tupper[v-1] - Tlower[u-1]):
        if (u != v):

          model.addConstr(
            t[v] >= t[u] + T[u][v] - Mt * (1 - x[u, v, d])
          )

  # total miles cost = quicksum of x[u, v, d] * C[u, v] for all d, u, v
  # total driver cost = truck used * constant
  model.setObjective(
    g.quicksum(
      x[u, v, d] * C[u][v] 
      for d in range(K) 
      for u in range(N+1) 
      for v in range(N+1)
    ) 
    + g.quicksum(z[d] * G for d in range(K)),
    g.GRB.MINIMIZE
  )

  model.optimize()

  for d in range(K):
    print(f"\n truck {d}")
    for u in range(N+1):
      for v in range(N+1):
        if x[u,v,d].X > 0.5:
          print(f"{u} -> {v} arrives at time {t[v].X}")

  with open(output_path, "w") as f:
    if model.status != g.GRB.OPTIMAL:
      f.write("-1")
      # model.computeIIS()
      # model.write("model.ilp")
      return

    vansUsed = sum(int(z[d].X) for d in range(K))

    f.write(f"{float(round(model.ObjVal))} {vansUsed}\n")

    for d in range(K):
      # skip unused vans
      if (z[d].X < 0.5):
        continue

      customers, arrivalTimes = extractRoute(x, t, d, N)
      customers = [v for v in customers if v != 0]
      
      f.write(f"{len(customers)} ")

      for customer, time in zip(customers, arrivalTimes):
        # skip depot
        if (customer == 0):
          continue

        f.write(f"{customer} {time} ")

      f.write("\n")

if __name__ == "__main__":
  main()
