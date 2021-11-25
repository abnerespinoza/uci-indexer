# mergeIndex.py

import os
import json

 
def mergePartialIndices():
    # list of partial inverted index files 
    fileNames = os.listdir(PARTIAL_INDICES_DIRECTORY)

    merged = 0
    while len(fileNames) > 1:
        # opens first two files in directory
        f1_path = os.path.join(PARTIAL_INDICES_DIRECTORY, fileNames[0])
        f2_path = os.path.join(PARTIAL_INDICES_DIRECTORY, fileNames[1])
        f1 = open(f1_path)
        f2 = open(f2_path)

        # joined index
        f3 = open(os.path.join(PARTIAL_INDICES_DIRECTORY, f'merged{merged}.txt'), 'w')

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


def createIndexOfIndex():
    # directory should just contain the final index
    fileNames = os.listdir(PARTIAL_INDICES_DIRECTORY)
    if len(fileNames) != 1:
        print('final index was not created correctly')
        return

    # rename index
    indexName = os.path.join(PARTIAL_INDICES_DIRECTORY, 'index.txt')
    os.rename(os.path.join(PARTIAL_INDICES_DIRECTORY, fileNames[0]), indexName)

    # iterate through index
    indexOfIndex = {}
    with open(indexName, 'r') as f:
        position = 0

        line = '?'
        while line:
            token = line.split()[0]
            indexOfIndex[token] = position

            if token == 'd':
                print('d', position)
                print(indexOfIndex[token])
            if token == 'doe':
                print ('does', position)
                print(indexOfIndex[token])

            position = f.tell()
            line = f.readline()

    with open('seek.json', 'w') as f:
        json.dump(indexOfIndex, f)


if __name__ == '__main__':
    # partial_indices folder path
    PARTIAL_INDICES_DIRECTORY = 'partial_indices'

    mergePartialIndices()
    createIndexOfIndex()