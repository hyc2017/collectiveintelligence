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

def hillclimb(domain, costf):
    sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

    while 1:
        neighbors = []
        current = costf(sol)
        best = current

        for i in range(len(domain)):
            if sol[i] > domain[i][0]:   neighbors.append(sol[0:i] + [sol[i] - 1] + sol[i + 1:])
            if sol[i] > domain[i][1]:   neighbors.append(sol[0:i] + [sol[i] + 1] + sol[i + 1:])
        for j in range(len(neighbors)):
            if costf(neighbors[j]) < best:
                best = costf(neighbors[j])
                sol = neighbors[j]
        if current == best:
            break

    return sol

def annealingoptimize(domain, costf, T = 10000.0, cool = 0.95, step = 1):
    sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

    while T > 0.1:
        i = random.randint(0, len(domain) - 1)
        dir = random.randint(-step, step)
        solB = sol[:]
        solB[i] += dir
        if solB[i] < domain[i][0]:  solB[i] = domain[i][0]
        if solB[i] > domain[i][1]:  solB[i] = domain[i][1]

        cost = costf(sol)
        costB = costf(solB)
        if costB < cost or random.random() < pow(math.e, -(costB - cost) / T):
            sol = solB

        T = T * cool

    return sol

def geneticoptimize(domain, costf, popsize = 50, step = 1, mutprob = 0.2, elite = 0.2, maxiter = 100):
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)

        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i] - step] + vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [vec[i] + step] + vec[i+1:]
            
        return vec

    def crossover(vec1, vec2):
        i = random.randint(1, len(domain) - 2)
        return vec1[0:i] + vec2[i:]

    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
        pop.append(vec)

    topelite = int(popsize * elite)

    for i in range(maxiter):
        scores = [(costf(vec), vec) for vec in pop]
        scores.sort()
        ranked = [vec for (score, vec) in scores]
        pop = ranked[0:topelite]

        while len(pop) < popsize:
            if random.random() < mutprob:
                c = random.randint(0, topelite)
                pop.append(mutate(ranked[c]))
            else:
                c1 = random.randint(0, topelite)
                c2 = random.randint(0, topelite)
                pop.append(crossover(ranked[c1], ranked[c2]))
        print(scores[0][0])

    return scores[0][1]
