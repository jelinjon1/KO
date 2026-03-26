#!/usr/bin/env python3
import sys
import gurobipy as g

# traveling salesman problem

# 1
# naivní řešení je přes ten součet po řádcích a sloupcích, čím zajistíme že do vertexu vejdeme a z něj následně odejdeme
# jen jednou, ale neřeší to problém s tím když nám tam vzniknou nějaký disjunktní kružnice jako řešení

# approach je přes čas navštívení vertexu Si, kde chceme aby pro i,j kde vede hrana z i->j kterou jsme vzali, tak
# Si + cij <= Sj + M(1 - xij)
# pro všechna i z V a j z V \ {1}



# 2
# Alternativní formulace s časem ne pro vrcholy, ale pro hrany
# yij \in Z+0
# for all i,j in E
# yij pujde pro hrany od n-1 do 1
# pokud hrana není vybraná, hodnota je 0

# yij <= (n - 1) xij    for all ij in E

# pro všechny hrany pak chceme
# součet yij všech hran které vedou do uzlu j bez 1 
# se rovná součet yjk všech hran které vedou ven z uzlu j
# podmínka neplatí pro jeden uzel (začátek/konec) pro kterej uděláme vyjímku

# extra podmnka pro start
# součet hran vedoucích do start + (n - 1) se musí rovnat součtu všcech který vedou ze startu ven



# 3
# lazy constraints
# zadáme jen základní část podmínek, necháme si udělat řešení
# zkontrolujeme jestli je feasible
# pokud ne upravíme model tak aby se tam nevyskytlo to nalezené řešení a opakujeme

# pokud nalezneme v tomhle alg více kružnic naivní implementací
# vezmeme jen seznam vrcholů, který jí tvoří a na další run přidáme pravidlo který
# zakáže konkrétně její existenci


# image shredding

# budeme brát pásky obrázku jako vrcholy v grafu a hledáme cestu mezi vrcholy, jako posloupnost pásků obrázku

# prevedeme shortest hamiltonian path problem na tsp
# uděláme asi pomocí arbitrárního vertexu, který spojíme s každým ostatním vertexem a dáme hranám cenu 0
# řešení tak nemusí bejt zacyklenej obrázek kde levej a pravej edge sedí, ale rozloží se nám to jakoby

# vzdálenost počítat přes numpy jinak na brute neprojde
#  určitě dělat zaokrouhlení čísel co polezou z gurobi

def main():
  input_path = sys.argv[1]
  output_path = sys.argv[2]

  with open(input_path, "r") as f:
    lines = f.readlines()

    i = 0
    for line in lines:
        line = line.strip()
        if line:
            if (i == 0):
              conf = list(map(int, line.split(' ')))
              # no. of rows
              r = conf[0]
              # width of a stripe in pixel columns
              w = conf[1]
              # height of a stripe (number of rows in the stripe)
              h = conf[2]
            else:
              d = [int(item.strip()) for item in line.split(' ')]
              # add as a row to a matrix ig?

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
