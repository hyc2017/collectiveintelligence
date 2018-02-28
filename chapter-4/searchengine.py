import urllib.request as request
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3
import re

ignorewords = set(['the','of','to','and','a','in','is','it'])

class crawler:
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def getentryid(self, table, field, value, createnew = True):
        cur = self.con.execute("select rowid from %s where %s = '%s'" % (table, field, value))
        res = cur.fetchone()
        if res == None:
            cur = self.con.execute("insert into %s (%s) values ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return res[0]

    def addtoindex(self, url, soup):
        if self.isindexed(url): return
        print('indexing %s' % url)

        text = self.gettextonly(soup)
        words = self.separatewords(text)

        urlid = self.getentryid('urllist', 'url', url)

        for i in range(len(words)):
            word = words[i]
            if word in ignorewords: continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute('insert into wordlocation(urlid, wordid, location) values (%d, %d, %d)' % (urlid, wordid, i))

    def gettextonly(self, soup):
        v = soup.string
        if v == None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()

    def separatewords(self, text):
        splitter = re.compile('\\W+')
        return [s.lower() for s in  splitter.split(text) if s != '']

    def isindexed(self, url):
        u = self.con.execute("select rowid from urllist where url = '%s'" % url).fetchone()
        if u != None:
            v = self.con.execute('select * from wordlocation where urlid = %d' % u[0]).fetchone()
            if v != None: return True
        return False

    def addlinkhref(self, urlFrom, urlTo, linkText):
        pass

    def crawl(self, pages, depth = 2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = request.urlopen(page)
                except:
                    print("Could not open %s" % page)
                    continue
                try:
                    soup = BeautifulSoup(c.read(), 'lxml')
                    self.addtoindex(page, soup)
                    links = soup('a')
                    for link in links:
                        if ('href' in dict(link.attrs)):
                            url = urljoin(page, link['href'])
                            if url.find("'") != -1 : continue
                            url = url.split('#')[0]  # remove location portion
                            if url[0:4] == 'http' and not self.isindexed(url):
                                newpages.add(url)
                            linkText = self.gettextonly(link)
                            self.addlinkhref(page,url,linkText)
                    self.dbcommit()
                except:
                    print("Could not parse page %s" % page)
            pages = newpages

    def createindextables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid, wordid, location)')
        self.con.execute('create table link(fromid integer, toid integer)')
        self.con.execute('create table linkwords(wordid, linkid)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()

class searcher:
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)

    def __del__(self):
        self.con.close()

    def getmatchrows(self, q):
        fieldlist = 'w0.urlid'
        tablelist = ''
        clauselist = ''
        wordids = []

        words = q.split(" ")
        tablenumber = 0

        for word in words:
            wordrow = self.con.execute("select rowid from wordlist where word = '%s'" % word)

            if wordrow != None:
                wordid = wordrow.fetchone()[0]
                wordids.append(wordid)
                if tablenumber > 0:
                    tablelist += ','
                    clauselist += ' and '
                    clauselist += 'w%d.urlid = w%d.urlid and ' % (tablenumber - 1, tablenumber)
                fieldlist += ',w%d.location' % tablenumber
                tablelist += 'wordlocation w%d' % tablenumber
                clauselist += 'w%d.wordid = %d' % (tablenumber, wordid)
                tablenumber += 1

        fullquery = 'select %s from %s where %s' % (fieldlist, tablelist, clauselist)
        cur = self.con.execute(fullquery)
        rows = [row for row in cur]

        return rows, wordids

    def getscorelist(self, rows, wordids):
        totalscores = dict([(row[0], 0) for row in rows])
        weights = [(1.0, self.frequencyscore(rows)), (1.0, self.locationscore(rows)), (1.0, self.distancescore(rows))]

        for (weight,score) in weights:
            for url in totalscores:
                totalscores[url] += weight * score[url]

        return totalscores

    def geturlname(self, urlid):
        return self.con.execute('select url from urllist where rowid = %d' % urlid).fetchone()[0]

    def query(self, q):
        rows, wordids = self.getmatchrows(q)
        scores = self.getscorelist(rows, wordids)
        rankedscores = sorted([(score,url) for (url,score) in scores.items()], reverse = 1)
        for (score, url) in rankedscores[0:10]:
            print("%f\t%s" % (score, self.geturlname(url)))

    def normalizescores(self, scores, smallIsBetter = 0):
        vsmall = 0.00001

        if smallIsBetter:
            minScore = min(scores.values())
            return dict([(u,float(minScore) / max(vsmall, s)) for (u, s) in scores.items()])
        else:
            maxScore = max(scores.values())
            if maxScore == 0:   maxScore = vsmall
            return dict([(u, float(s) / maxScore) for (u, s) in scores.items()])

    def frequencyscore(self, rows):
        counts = dict([(row[0], 0) for row in rows])
        for row in rows:    counts[row[0]] += 1;
        return self.normalizescores(counts)

    def locationscore(self, rows):
        location = dict([(row[0], 1000000) for row in rows])

        for row in rows:
            loc = sum(row[1:])
            if loc < location[row[0]]:  location[row[0]] = loc

        return self.normalizescores(location, smallIsBetter = 1)
                    
    def distancescore(self, rows):
        if len(rows[0]) <= 2:   return dict([(row[0], 1.0) for row in rows])

        mindistance = dict([(rows[0], 1000000) for row in rows])

        for row in rows:
            dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
            if dist < mindistance[row[0]] : mindistance[row[0]] = dist

        return self.normalizescores(mindistance, smallIsBetter = 1)
