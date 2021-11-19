#Note implement tf-idf, timer
import json
import ast
from os import set_blocking
import nltk
from nltk.stem.snowball import SnowballStemmer
import time

from buildIndex import process_text

def mergePostings(postingList): #return array of DocIds where they occur.
    # query = [cristina, lopes]
    #Ex. christina [{docID: 234, freq: 3}, { docID: 400, freq: 2}] ->[234, 400]
    # lopes [{docID: 232, freq: 5}, {docID: 400, freq: 4}, {docID: 623, freq: 1}] ->[232, 400, 623]

    if not postingList:
        return []

    docIDList = []
    for postings in postingList:
        individualDocList = []
        for posting in postings:
            individualDocList.append(str(posting['docID']))
        docIDList.append(individualDocList)
    #now we have bunch of lists of docIDs for each token in the query. 
    docIDList = sorted(docIDList, key = lambda x: len(x))

    while len(docIDList) > 1:
        #get intersect of docIDList[0] and docIDList[1]
        docIDList[1] = list(set(docIDList[0]) & set(docIDList[1]))
        docIDList.pop(0)

    #search indexOfIndex for where c starts
    #go to our actual Index search for christina
    #get list of postings and do a mergeSearch

    return docIDList[0] 

    
if __name__ == '__main__':
    STEMMER = SnowballStemmer('english')
    seek_f = open('seek.json', 'r')
    indexOfIndex = json.load(seek_f)
    docLookup_f = open('docLookup.json', 'r')
    docLookup = json.load(docLookup_f)

    while True:
        # prompt user for query
        query = input("Enter a query: ").lower().strip()
        # get query

        t1 = time.time()
        #make sure alphanum
        queryArr = process_text(query)
        possibleIndexes = "0123456789abcdefghijklmnopqrstuvwxyz"
        # possibly use binary search to find the correct token ex: c[h] we search for the halfway point in the "c" files and check
        # if 2nd character is < > h.
        # may need to track EOF index for Z case
        # search for seek position
        postingsList = []
        for word in queryArr:
            if word[0] in indexOfIndex.keys():
                position = indexOfIndex[word[0]]
                
                #jump to position in index.txt
                f = open('index.txt', 'r')
                f.seek(position)
                line = f.readline()
                #this is assuming there is a match
                #may have to stem the query as well in case there are no matches
                #postings = []
                while line:
                    token = line.split()[0]
                    #postings.append(line[len(token) + 1: -2])

                    #if word is the same, store posting
                    if token == word:
                        postings = json.loads(line[len(token) + 1: ])
                        postingsList.append(postings)
                        break
                    line = f.readline()

                if not line:
                    print("token not found!!") 

        docIDMatches = mergePostings(postingsList)


        urls = []

        for docId in docIDMatches:
            urls.append(docLookup[docId])

        t2 = time.time() - t1
        print("Search time in ms: " + str(t2 * 1000))
        if not urls:
            print("no results!!!")                
        else:
            print("Top 5 urls:")
            for i in range(5):
                print(urls[i])
            
    