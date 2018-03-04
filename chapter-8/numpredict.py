from random import random, randint
import math
from pylab import *

def wineprice(rating, age):
    peak_age = rating - 50

    price = rating / 2
    if age > peak_age:
        price = price * (5 - (age - peak_age) / 2)
    else:
        price = price * (5 * (age + 1) / peak_age)

    if price < 0:   price = 0

    return price

def wineset1():
    rows = []

    for i in range(300):
        rating = random() * 50 + 50
        age = random() * 50
        price = wineprice(rating, age)
        price *= (random() * 0.4 + 0.8)
        rows.append({'input' : (rating, age), 'result' : price})

    return rows

def euclidean(v1, v2):
    d = 0.0

    for i in range(len(v1)):
        d += (v1[i] - v2[i]) ** 2

    return math.sqrt(d)

def getdistances(data, vec1):
    distancelist = []

    for i in range(len(data)):
        vec2 = data[i]['input']
        distancelist.append((euclidean(vec1, vec2), i))

    distancelist.sort()
    return distancelist

def knnestimate(data, vec1, k = 5):
    distancelist = getdistances(data, vec1)

    avg = 0.0
    for i in range(k):
        idx = distancelist[i][1]
        avg += data[idx]['result']

    return avg / k

def inverseweight(dist, num = 1.0, const = 0.1):
    return num / (dist + const)

def subtractweight(dist, const = 1.0):
    if dist >=  const:
        return 0
    else:
        return const - dist

def gaussian(dist, sigma = 5.0):
    return math.e ** (-dist ** 2 / (2 * sigma ** 2))

def weightedknn(data, vec1, k = 5, weightf = gaussian):
    distancelist = getdistances(data, vec1)

    avg = 0.0
    totalweight = 0.0
    for i in range(k):
        distance = distancelist[i][0]
        idx = distancelist[i][1]
        weight = weightf(distance)
        avg += data[idx]['result'] * weight
        totalweight += weight

    return avg / totalweight

def dividedata(data, test = 0.1):
    trainset = []
    testset = []

    for row in data:
        if random() < test:
            testset.append(row)
        else:
            trainset.append(row)

    return trainset, testset

def testalgorithm(algf, trainset, testset):
    error = 0.0

    for row in testset:
        guess = algf(trainset, row['input'])
        error += (row['result'] - guess) ** 2

    return error / len(testset)

def crossvalidate(algf, data, trials = 100, test = 0.1):
    error = 0.0

    for i in range(trials):
        trainset, testset = dividedata(data, test)
        error += testalgorithm(algf, trainset, testset)

    return error / trials

def wineset2():
    rows = []

    for i in range(300):
        rating = random() * 50 + 50
        age = random() * 50
        aisle = float(randint(1, 20))
        bottlesize = [375.0, 750.0, 1500.0][randint(0, 2)]
        price = wineprice(rating, age)
        price *= (bottlesize / 750)
        price *= (random() * 0.2 + 0.9)
        rows.append({'input' : (rating, age, aisle, bottlesize), 'result' : price})

    return rows

def rescale(data, scale):
    scaleddata = []

    for row in data:
        scaled = [scale[i] * row['input'][i] for i in range(len(scale))]
        scaleddata.append({'input' : scaled, 'result' : row['result']})

    return scaleddata

weightdomain = [(0, 10)] * 4

def createcostfunction(algf, data):
    def costf(scale):
        sdata = rescale(data, scale)
        return crossvalidate(algf, sdata, trials = 20)

    return costf

def wineset3():
    rows = wineset1()

    for row in rows:
        if random() < 0.5:
            row['result'] *= 0.5

    return rows

def probguess(data, vec1, low, high, k = 5, weightf = gaussian):
    dlist = getdistances(data, vec1)
    nweight = 0.0
    tweight = 0.0

    for i in range(k):
        distance = dlist[i][0]
        idx = dlist[i][1]
        weight = weightf(distance)
        v = data[idx]['result']

        if v >= low and v <= high:
            nweight += weight
        tweight += weight

    if tweight == 0:    return 0
    return nweight / tweight

def cumulativegraph(data, vec1, high, k = 5, weightf = gaussian):
    t1 = arange(0.0, high, 0.1)
    cprob = [probguess(data, vec1, 0, v, k, weightf) for v in t1]
    plot(t1, cprob)
    show()

def probabilitygraph(data, vec1, high, k = 5, weightf = gaussian, ss = 5.0):
    t1 = arange(0.0, high, 0.1)

    probs = [probguess(data, vec1, v, v + 0.1, k, weightf) for v in t1]

    smoothed = []

    for i in range(len(probs)):
        sv = 0.0
        for j in range(0, len(probs)):
            dist = abs(i - j) * 0.1
            weight = gaussian(dist, sigma = ss)
            sv += weight * probs[j]
        smoothed.append(sv)

    smoothed = array(smoothed)
    plot(t1, smoothed)
    show()

