# mergeIndex.py

import os
import json
import math
import zipfile

from buildIndex import savePartialIndex


def processAnchorPageRank():
    anchorLookup = None
    processedPageRankLookup = dict()

    li_rm = []  # list of tokens to remove from anchorLookup

    with open('docLookup.json', 'r') as dl, open('anchorLookup.json', 'r') as al, open('pageRankLookup.json', 'r') as prl:
        docLookup = json.load(dl)
    
        invertedDocLookup = dict()
        for key, value in docLookup.items():
            invertedDocLookup[value] = key

        anchorLookup = json.load(al)
        for key, value in anchorLookup.items():
            docs = []
            for url in value:
                if url in invertedDocLookup:
                    docs.append(invertedDocLookup[url])
                
            # calculating frequencies
            frequencies = dict()
            for docID in docs:
                if docID in frequencies:
                    frequencies[docID] += 1
                else:
                    frequencies[docID] = 1

            # calculating tf
            for docID in frequencies:
                count = frequencies[docID]
                frequencies[docID] = 1 + math.log10(count)

            postings = []
            for docID, freq in frequencies.items():
                K = len(invertedDocLookup)
                idf = math.log10(K / len(frequencies))

                posting = {
                    'doc': docID,
                    'tfidf' : round(freq * idf, 5)
                }
                postings.append(posting)

            anchorLookup[key] = postings
            if not postings:
                li_rm.append(key)
        
        pageRankLookup = json.load(prl)
        for url, value in pageRankLookup.items():
            if url in invertedDocLookup:
                processedPageRankLookup[invertedDocLookup[url]] = value
    
    for key in li_rm:
        del anchorLookup[key]
    
    for key, value in processedPageRankLookup.items():
        if value == 1:
            processedPageRankLookup[key] = 1.2
        else:
            processedPageRankLookup[key] = 1 + math.log10(value)
        
    savePartialIndex(anchorLookup, 'anchorIndex.txt')
    with open('pagerank.json', 'w') as prl:
        json.dump(processedPageRankLookup, prl)
    
    os.remove('anchorLookup.json')
    os.remove('pageRankLookup.json')

 
def mergePartialIndices():
    # list of partial inverted index files 
    fileNames = os.listdir(PARTIAL_INDICES_DIRECTORY)

    merged = 0
    while len(fileNames) > 1:
        # opens first two files in directory
        f1_path = os.path.join(PARTIAL_INDICES_DIRECTORY, fileNames[0])
        f2_path = os.path.join(PARTIAL_INDICES_DIRECTORY, fileNames[1])
        f1 = open(f1_path, encoding= "utf-8")
        f2 = open(f2_path, encoding= "utf-8")

        # joined index
        f3 = open(os.path.join(PARTIAL_INDICES_DIRECTORY, f'merged{merged}.txt'), 'w',encoding= "utf-8")

        # cursor to iterate file
        line1 = f1.readline()
        line2 = f2.readline()
        
        # while both files have contents
        while line1 and line2:
            # split to get token
            line1Token = line1.split()[0]
            line2Token = line2.split()[0]            

            #if equal, then combine line 1 and line 2 into fullIndex
            if line1Token == line2Token:
                postings1 = json.loads(line1[len(line1Token) + 1:])
                postings2 = json.loads(line2[len(line2Token) + 1:])
                postings3 = mergePostings(postings1, postings2)
                f3.write(f'{line1Token} {json.dumps(postings3)}\n')

                line1 = f1.readline()
                line2 = f2.readline()

            #if line1Token < line2Token, increment line1Token
            elif line1Token < line2Token:
                f3.write(line1)
                line1 = f1.readline()
            #else increment line2Token
            else:
                f3.write(line2)
                line2 = f2.readline()

        # close files
        f1.close()
        f2.close()
        f3.close()

        # delete previous indices
        os.remove(f1_path)
        os.remove(f2_path)
        fileNames = os.listdir(PARTIAL_INDICES_DIRECTORY)

        merged += 1
    
    # directory should just contain the final index
    fileNames = os.listdir(PARTIAL_INDICES_DIRECTORY)
    if len(fileNames) != 1:
        print('final index was not created correctly')
        return

    # rename index
    os.rename(os.path.join(PARTIAL_INDICES_DIRECTORY, fileNames[0]), T_INDEX_FILE)
    os.rmdir(PARTIAL_INDICES_DIRECTORY)


def mergePostings(postings1, postings2):
    # iterate through list of postings
    p1 = 0
    p2 = 0
    newPosting = []
    
    while p1 < len(postings1) and p2 < len(postings2): 
        # posting1 has a smaller docID
        if postings1[p1]['doc'] < postings2[p2]['doc']:
            newPosting.append(postings1[p1])
            p1 += 1
        # posting2 has a smaller doc
        elif postings1[p1]['doc'] > postings2[p2]['doc']:
            newPosting.append(postings2[p2])
            p2 += 1
        # should never happen
        elif postings1[p1]['doc'] == postings2[p2]['doc']:
            print('uh oh')

    # add leftovers postings
    if p1 < len(postings1):
        newPosting += postings1[p1:]
    if p2 < len(postings2):
        newPosting += postings2[p2:]

    return newPosting


def addScore():
    with open(T_INDEX_FILE, 'r') as t, open(INDEX_FILE, 'w') as f, open('pagerank.json', 'r') as pr:
        pagerank = json.load(pr)

        for line in t:
            text = line.split()
            token = text[0]

            postings = json.loads(line[len(token) + 1: ])

            idf = math.log10(N / len(postings))
            for posting in postings:
                # page rank
                pr = 1
                if str(posting['doc']) in pagerank:
                    pr = pagerank[str(posting['doc'])]

                # two gram
                tg = 1
                if '_' in token:
                    tg = 2
                
                tfidf = round(posting['tf'] * idf, 5)
                posting['score'] = tfidf * posting['fi'] * pr * tg

                del posting['tf']
                del posting['fi']
            
            f.write(f'{token} {json.dumps(postings)}\n')
    
    with zipfile.ZipFile('t_index.txt.zip', 'w') as z:
        z.write(T_INDEX_FILE)
    os.remove(T_INDEX_FILE)


def createIndexOfIndex():
    # iterate through index
    indexOfIndex = {}
    with open(INDEX_FILE, 'r') as f:
        position = 0

        line = '?'
        while line:
            token = line.split()[0]
            indexOfIndex[token] = position

            position = f.tell()
            line = f.readline()

        del indexOfIndex['?']

    with open('seek.json', 'w') as f:
        json.dump(indexOfIndex, f)


if __name__ == '__main__':
    # partial_indices folder path
    PARTIAL_INDICES_DIRECTORY = 'partial_indices/'
    T_INDEX_FILE = 't_index.txt'
    INDEX_FILE = 'index.txt'

    N = 55393

    processAnchorPageRank()
    mergePartialIndices()
    addScore()
    createIndexOfIndex()