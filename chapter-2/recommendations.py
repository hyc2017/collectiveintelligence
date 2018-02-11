# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

from math import sqrt

def sim_distance(prefs,person1,person2):
    s1 = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            s1[item] = 1
    if len(s1) == 0:    return 0

    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])

    return 1 / (1 + sqrt(sum_of_squares))

def sim_pearson(prefs,person1,person2):
    s1 = {}

    for item in prefs[person1]:
        if item in prefs[person2]:
            s1[item] = 1
    n = len(s1)
    if n == 0:  return 0

    sum1 = sum([prefs[person1][item] for item in s1])
    sum2 = sum([prefs[person2][item] for item in s1])

    sum1Sq = sum(pow(prefs[person1][item],2) for item in s1)
    sum2Sq = sum(pow(prefs[person2][item],2) for item in s1)

    pSum = sum([prefs[person1][item] * prefs[person2][item] for item in s1])

    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1,2) / n) * (sum2Sq - pow(sum2,2) / n))
    if den == 0: return 0

    r = num / den

    return r

def topMatches(prefs,person,n=5,similarity=sim_pearson):
    scores = [(similarity(prefs,person,other),other) for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

def getRecommendations(prefs,person,similarity=sim_pearson):
    totalSum = {}
    rateSum = {}
    for other in prefs:
        if other == person: continue
        sim = similarity(prefs,person,other)
        if sim <= 0:    continue
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item] == 0:
                totalSum.setdefault(item,0)
                totalSum[item] += prefs[other][item] * sim
                rateSum.setdefault(item,0)
                rateSum[item] += sim
    rankings = [(total / rateSum[item],item) for item,total in totalSum.items()]
    rankings.sort()
    rankings.reverse()
    return rankings

def transform(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            result[item][person] = prefs[person][item] 

    return result

def calculateSimilarItems(prefs,n=10):
    result = {}
    itemPrefs = transform(prefs)
    c = 0
    for item in itemPrefs:
        c += 1
        if c % 100 == 0:print("%d / %d" % (c,len(itemPrefs)))
        scores = topMatches(itemPrefs,item,n = n,similarity=sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs,itemMatch,user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    for (item,rating) in userRatings.items():
        for (similarity,item2) in itemMatch[item]:
            if item2 in userRatings: continue
            scores.setdefault(item2,0)
            scores[item2] += rating * similarity
            totalSim.setdefault(item2,0)
            totalSim[item2] += similarity

    rankings = [(score / totalSim[item],item) for item,score in scores.items()]
    rankings.sort()
    rankings.reverse()
    return rankings

def loadMovieLens(path='ml-100k'):
  # Get movie titles
  movies={}
  for line in open(path+'/u.item','r',encoding = 'iso-8859-15'):
    (id,title)=line.split('|')[0:2]
    movies[id]=title
  
  # Load data
  prefs={}
  for line in open(path+'/u.data','r',encoding = 'iso-8859-15'):
    (user,movieid,rating,ts)=line.split('\t')
    prefs.setdefault(user,{})
    prefs[user][movies[movieid]]=float(rating)
  return prefs
