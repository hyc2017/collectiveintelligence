import random
import math

dorms=['Zeus','Athena','Hercules','Bacchus','Pluto']

prefs=[('Toby', ('Bacchus', 'Hercules')),
       ('Steve', ('Zeus', 'Pluto')),
       ('Karen', ('Athena', 'Zeus')),
       ('Sarah', ('Zeus', 'Pluto')),
       ('Dave', ('Athena', 'Bacchus')), 
       ('Jeff', ('Hercules', 'Pluto')), 
       ('Fred', ('Pluto', 'Athena')), 
       ('Suzie', ('Bacchus', 'Hercules')), 
       ('Laura', ('Bacchus', 'Hercules')), 
       ('James', ('Hercules', 'Athena'))]

domain = [(0, len(dorms) * 2 - i - 1) for i in range(0, len(dorms) * 2)]

def printsolution(vec):
    slots = []
    for i in range(len(dorms)): slots += [i, i]

    for i in range(len(vec)):
        x = int(vec[i])
        dorm = dorms[slots[x]]
        print(prefs[i][0], dorm)
        del(slots[x])

def dormcost(vec):
    slots = []
    for i in range(len(dorms)): slots += [i,i]

    totalcost = 0
    for i in range(len(vec)):
        x = int(vec[i])
        dorm = dorms[slots[x]]
        pref = prefs[i][1]
        if dorm == pref[0]:     totalcost += 0
        elif dorm == pref[1]:   totalcost += 1
        else:                   totalcost += 3
        del(slots[x])

    return totalcost
