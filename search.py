# search.py

import json
import time
import math

from buildIndex import process_text


def length_normalize(vector):
    length = 0
    for item in vector:
        length += pow(item, 2)
    length = math.sqrt(length)

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
                ranks[posting['doc']] += posting['score']
            else:
                ranks[posting['doc']] = posting['score']

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

            # removes duplicates
            seen = set()
            seen_add = seen.add
            queryLi = [x for x in queryLi if not (x in seen or seen_add(x))]

            postingList = []
            for word in queryLi:
                if word in indexOfIndex:
                    position = indexOfIndex[word]
                    
                    # jump to position in index.txt
                    f.seek(position)
                    line = f.readline()

                    postings = json.loads(line[len(word) + 1: ])
                    postingList.append(postings)

            docIDMatches = rankPostings(postingList)

            urls = []
            for docId in docIDMatches:
                urls.append(docLookup[docId])

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