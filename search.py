# search.py

import json
import time
import math

from numpy import dot
from numpy.linalg import norm

from buildIndex import process_text


def length_normalize(vector):
    length = norm(vector)
    for index, item in enumerate(vector):
        vector[index] = item / length

    return vector


# returns list of docIDs
def mergePostings(postingList): 
    if not postingList:
        return []

    docIDList = []
    for postings in postingList:
        docIDList.append([str(posting['doc']) for posting in postings])

    docIDList = sorted(docIDList, key=lambda x: len(x))

    while len(docIDList) > 1:
        docIDList[0] = list(set(docIDList[0]) & set(docIDList[-1]))
        docIDList.pop()

    return docIDList[0]


# returns list of ranked docIDs
def rankPostings(postingList): 
    if not postingList:
        return []

    ranks = dict()
    for postings in postingList:
        for posting in postings:
            if posting['doc'] in ranks:
                ranks[posting['doc']] += (posting['tfidf']) * posting['fi']
            else:
                ranks[posting['doc']] = (posting['tfidf']) * posting['fi']

    docIDList = [str(w) for w in sorted(ranks, key=ranks.get, reverse=True)]
    return docIDList

    
if __name__ == '__main__':
    N = 55393

    with open('index.txt', 'r') as f, open('seek.json', 'r') as seek_f, open('docLookup.json', 'r') as docLookup_f:
        indexOfIndex = json.load(seek_f)
        docLookup = json.load(docLookup_f)

        while True:
            query = input("enter a query: ")

            t1 = time.time()
            queryLi = process_text(query)

            # removing tokens not in index
            li = []
            for index, token in enumerate(queryLi):
                if token not in indexOfIndex:
                    li.append(index)
            
            index = len(li) - 1
            while index >= 0:
                queryLi.pop(li[index])
                index -= 1

            # calculating frequencies of query to find tf
            qfrequencies = dict()
            for token in queryLi:
                if token in qfrequencies:
                    qfrequencies[token] += 1
                else:
                    qfrequencies[token] = 1

            qvector = list(qfrequencies.values())
            for index, item in enumerate(qvector):
                qvector[index] = 1 + math.log10(item)

            # removes duplicates
            seen = set()
            seen_add = seen.add
            queryLi = [x for x in queryLi if not (x in seen or seen_add(x))]

            dvectors = dict()
            dfields = dict()
            blank_vector = []

            postingList = []
            for index, word in enumerate(queryLi):
                position = indexOfIndex[word]
                
                # jump to position in index.txt
                f.seek(position)
                line = f.readline()

                postings = json.loads(line[len(word) + 1: ])

                idf = math.log10(N / len(postings))
                qvector[index] *= idf

                for posting in postings:
                    if posting['doc'] in dvectors:
                        dvectors[posting['doc']].append(posting['tfidf'])
                        dfields[posting['doc']] += posting['fi']
                    else:
                        dvectors[posting['doc']] = list(blank_vector)
                        dvectors[posting['doc']].append(posting['tfidf'])
                        dfields[posting['doc']] = posting['fi']
                
                for vector in dvectors:
                    if len(dvectors[vector]) < len(blank_vector) + 1:
                        dvectors[vector].append(0)

                postingList.append(postings)
                blank_vector.append(0)

            qvector = length_normalize(qvector)

            dscore = dict()
            for vector in dvectors:
                dscore[vector] = dot(length_normalize(dvectors[vector]), qvector) * dfields[vector]

            docIDMatches = sorted(dscore, key=dscore.get, reverse=True)

            urls = []
            for docID in docIDMatches:
                id = str(docID)
                urls.append(docLookup[id])

            t2 = time.time() - t1

            if not urls:
                print('\nno results - {}'.format(query))                
            else:
                print('\ntop results: ')
                for i in range(20):
                    if i == len(urls):
                        break

                    if i < 9:
                        print(' {}.  {}'.format(i + 1, urls[i]))
                    else:
                        print('{}.  {}'.format(i + 1, urls[i]))

            print('\nsearch time (ms): {}\n'.format(t2 * 1000))