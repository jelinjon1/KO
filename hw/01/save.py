import matplotlib.pyplot as plt


# shift length: 8 hrs
# array X where Xi is num of people starting their shift at that hour
# num of people at work at a given hour j = sum of Xi where i in range(j-8, j)
# minimize sum of people assigned to a day

# constraint: people assigned to an hour must be at least the required amount

# v ukolu
# minimalizovat rozdily mezi shift coverage a demand spis nez rikat ze musime
# mit alespon tolik

# rikal nceo na zpusob ze pokud je jich tam treba 11, ale melo jich tam bejt 13
# tak to asi zvladnou

# minimalizovat sumu |c_1i - c_2i|
# absolutni hodnota potreba udelat pomoci promenne, gurobi neumi
# zi >= c_1i - c_2i and
# zi >= c_2i - c_1i
# a pak delat min ze sum(24) zi

# odstranit constraint na to ze tam mame tolik a tolik lidi

# pro cases kde bude demand hodne prerustat coverage, budeme to omezovat promennou D
# rozdil nemuze prerust coverage o vic nez D

d = [6, 6, 6, 6, 6, 8, 9, 12, 18, 22, 25, 21, 21, 20, 18, 21, 21, 24, 24, 18, 18, 18, 12, 8]
e = [3, 3, 3, 3, 3, 4, 4, 6, 9, 11, 12, 10, 10, 10, 9, 10, 10, 12, 12, 9, 9, 9, 6, 4]
D = 2

with open('./hw/01/instances/public' + str(1) + '.txt') as f:
  lines = f.readlines()
  
  i = 0
  for line in lines:
      line = line.strip()
      if line:
          if i == 0:
            d = [int(item.strip()) for item in line.split(' ')]
            i += 1
            continue
          if i == 1:
            e = [int(item.strip()) for item in line.split(' ')]
            i += 1
            continue
          if i == 2:
            D = int(line)
            continue

def plot_shifts(x_start):
  num_shifts = [sum([x_start[k % 24] for k in range(i-7, i+1)]) for i in range(24)]
  margin = 0.2
  width = 0.3
  plt.figure(figsize=(8, 4))
  plt.bar([h + margin for h in range(24)], d, width=width, color='green')
  plt.bar([h + margin + width for h in range(24)], num_shifts, width=width, color='yellow')
  plt.xlabel("hour")
  plt.legend(['demand', 'number shifts'], ncol=2, bbox_to_anchor=(0.8, 1.1))
  plt.xlim(0, 24)
  plt.ylim(0, max(num_shifts + d) + 1)
  plt.xticks(range(24), [i % 24 for i in range(24)])
  plt.grid()
  plt.show()

def plot_shifts_week(x_start):
  hours = 168
  demand = []
  for i in range(hours):
      hour_of_day = i % 24
      day = i // 24
      if day < 5:
          demand.append(d[hour_of_day])
      else:
          demand.append(e[hour_of_day])

  num_shifts = [
      sum([x_start[k % hours] for k in range(i - 7, i + 1)])
      for i in range(hours)
  ]

  margin = 0.2
  width = 0.3
  plt.figure(figsize=(14, 5))

  plt.bar([h + margin for h in range(hours)], demand, width=width, color='green')
  plt.bar([h + margin + width for h in range(hours)], num_shifts, width=width, color='yellow')

  plt.xlabel("hour (week)")
  plt.legend(['demand', 'number shifts'], ncol=2, bbox_to_anchor=(0.8, 1.1))

  plt.xlim(0, hours)
  plt.ylim(0, max(num_shifts + demand) + 1)

  day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  plt.xticks(range(0, hours, 24), day_labels)

  plt.grid()
  plt.show()

print("MY SOLUTION")
# First line: objective value (integer)
print(int(round(model.ObjVal)))

# Second line: x0 x1 x2 ... x167
solution = [str(int(round(x[i].X))) for i in range(168)]
print(" ".join(solution))

print("EXPECTED SOLUTION")
with open('./hw/01/solutions/public' + str(1) + '.txt') as f:
    lines = f.readlines()
    i = 0
    for line in lines:
        line = line.strip()
        if line:
            print(line)

plot_shifts_week([x[i].x for i in range(168)])