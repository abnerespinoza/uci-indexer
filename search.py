#Note implement tf-idf, timer
import json
import ast
from os import set_blocking

from partA import tokenize_string

def mergePostings(postingList): #return array of DocIds where they occur.
    # query = [cristina, lopes]
    #Ex. christina [{docID: 234, freq: 3}, { docID: 400, freq: 2}]
    # lopes [{docID: 232, freq: 5}, {docID: 400, freq: 4}, {docID: 623, freq: 1}]

    if not postingList:
        return []

    docIDList = []
    for postings in postingList:
        individualDocList = []
        for posting in postings:
            individualDocList.append(str(posting['docID']))
        docIDList.append(individualDocList)
    #now we have bunch of lists of docIDs for each token in the query. 
    print(docIDList)
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
    seek_f = open('seek.json')
    indexOfIndex = json.load(seek_f)
    docLookup_f = open('docLookup.json')
    docLookup = json.load(docLookup_f)
    # prompt user for query
    query = input("Enter a query: ").lower().strip()
    # get query

    #make sure alphanum
    queryArr = tokenize_string(query)
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

    if not urls:
        print("no results!!!")                
    else:
        print(urls)

            
    