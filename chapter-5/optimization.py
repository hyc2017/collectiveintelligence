import time
import random
import math

people = [('Seymour', 'BOS'), ('Franny', 'DAL'), ('Zooey', 'CAK'), ('Walt', 'MIA'), ('Buddy', 'ORD'), ('Les', 'OMA')]

destination = 'LGA'

flights = {}

for line in open('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])
    flights[(origin, dest)].append((depart, arrive, int(price)))

def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]

def printschedule(r):
    for d in range(int(len(r) / 2)):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[2 * d]]
        ret = flights[(destination, origin)][r[2 * d + 1]]
        print('%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin, out[0], out[1], out[2], ret[0], ret[1], ret[2]))



def schedulecost(sol):
    totalprice = 0
    lastestarrival = 0
    earliestdep = 24 * 60

    for d in range(int(len(sol) /  2)):
        origin = people[d][1]
        out = flights[(origin, destination)][int(sol[2 * d])]
        ret = flights[(destination, origin)][int(sol[2 * d + 1])]
        totalprice += out[2]
        totalprice += ret[2]
        if getminutes(out[1]) > lastestarrival: lastestarrival = getminutes(out[1])
        if getminutes(ret[0]) < earliestdep:    earliestdep = getminutes(ret[0])

    totalwait = 0
    for d in range(int(len(sol) / 2)):
        origin = people[d][1]
        out = flights[(origin, destination)][int(sol[2 * d])]
        ret = flights[(destination, origin)][int(sol[2 * d + 1])]
        totalwait += lastestarrival - getminutes(out[1])
        totalwait += getminutes(ret[0]) - earliestdep

    if lastestarrival < earliestdep:    totalprice += 50

    return  totalprice + totalwait

def randomoptimize(domain, costf):
    best = 999999999
    bestr = None

    for i in range(10000):
        r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
        cost = costf(r)
        if cost < best:
            best = cost
            bestr = r

    return r
