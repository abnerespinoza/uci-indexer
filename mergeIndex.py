import os
import json

from buildIndex import PARTIAL_INDEX_FOLDER

def mergePartialIndices():
    # given list of partial indices files, merge into 1 file
    fileNames = os.listdir(PARTIAL_INDEX_FOLDER)
    merged = 0
    while len(fileNames) > 1:
        # opens first two files in directory
        f1_path = os.path.join(PARTIAL_INDEX_FOLDER, fileNames[0])
        f2_path = os.path.join(PARTIAL_INDEX_FOLDER, fileNames[1])
        f1 = open(f1_path)
        f2 = open(f2_path)
        # joined index
        f3 = open(os.path.join(PARTIAL_INDEX_FOLDER, f'merged{merged}.txt'), 'w')

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
        fileNames = os.listdir(PARTIAL_INDEX_FOLDER)

        merged += 1

def mergePostings(postings1, postings2):
    # iterate through list of postings
    p1 = 0
    p2 = 0
    newPosting = []
    
    while p1 < len(postings1) and p2 < len(postings2): 
        # posting1 has a smaller docID
        if postings1[p1]['docID'] < postings2[p2]['docID']:
            newPosting.append(postings1[p1])
            p1 += 1
        # posting2 has a smaller docID
        elif postings1[p1]['docID'] > postings2[p2]['docID']:
            newPosting.append(postings2[p2])
            p2 += 1
        # should never happen
        elif postings1[p1]['docID'] == postings2[p2]['docID']:
            print('uh oh')

    # add leftovers postings
    if p1 < len(postings1):
        newPosting += postings1[p1:]
    if p2 < len(postings2):
        newPosting += postings2[p2:]

    return newPosting

if __name__ == '__main__':
    mergePartialIndices()