# search.py

import json
import time

from buildIndex import process_text


# returns list of docIDs
# E.g.
# query = [cristina, lopes]
# christina [{doc: 234, fre: 3}, { doc: 400, fre: 2}] ->[234, 400]
# lopes [{doc: 232, fre: 5}, {doc: 400, fre: 4}, {doc: 623, fre: 1}] ->[232, 400, 623]
def mergePostings(postingList): 
    if not postingList:
        return []

    docIDList = []
    for postings in postingList:
        individualDocList = []
        for posting in postings:
            individualDocList.append(str(posting['doc']))
        docIDList.append(individualDocList)

    docIDList = sorted(docIDList, key = lambda x: len(x))

    while len(docIDList) > 1:
        # intersection of docIDList[0] and docIDList[1]
        docIDList[1] = list(set(docIDList[0]) & set(docIDList[1]))
        docIDList.pop(0)

    return docIDList[0] 

    
if __name__ == '__main__':
    with open('seek.json', 'r') as seek_f, open('docLookup.json', 'r') as docLookup_f:
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

            possibleIndexes = "0123456789abcdefghijklmnopqrstuvwxyz"

            # use binary search to find the token
            # may need to track EOF index for Z case

            postingsList = []
            for word in queryLi:
                if word in indexOfIndex.keys():
                    position = indexOfIndex[word]
                    
                    # jump to position in index.txt
                    f = open('index.txt', 'r')
                    f.seek(position)
                    line = f.readline()

                    token = line.split()[0]
                    postings = json.loads(line[len(token) + 1: ])
                    postingsList.append(postings)

            docIDMatches = mergePostings(postingsList)

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