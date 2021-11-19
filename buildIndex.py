# buildIndex.py


import os
import re
import json
import nltk

from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer


# hidden files raised errors when opening
def listDirNoHidden(path):
    f_names = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            f_names.append(f)
    return f_names


# invertedIndex is dict[{'doc': x, 'fre': y, 'fie': z}]
                        # docID, frequency, fields
def savePartialIndex(invertedIndex, filePath): 
    with open(filePath, 'w') as f:
        # iterate through sorted keys of inverted index
        for token in sorted(invertedIndex):
            # for each token, write in format-- token [Posting]
            f.write(f'{token} {json.dumps(invertedIndex[token])}\n')

<<<<<<< HEAD
def process_text(text: str, n: int = 10_000_000):
    STEMMER = SnowballStemmer('english')
=======

def processText(text: str, n: int = 10_000_000):
    text = PATTERN.sub(lambda m: REP[re.escape(m.group(0))], text)

>>>>>>> 6c921174f95f867537e65ca8c8d5a8faada65534
    raw_tokens = []
    if len(text) > n:
        split_text = []
        for index in range(0, len(text), n):
            split_text.append(text[index : index + n])

        li_raw_tokens = []
        for text in split_text:
            li_raw_tokens.append(nltk.word_tokenize(text))

        for li in li_raw_tokens:
            for token in li:
                raw_tokens.append(token)
    else:
        raw_tokens = nltk.word_tokenize(text)  

    # removing all tokens that are not alphanumeric
    index = len(raw_tokens) - 1
    while index >= 0:
        if not raw_tokens[index].isalnum():
            raw_tokens[index] = '?'
        index -= 1

    # stemming
    tokens = []
    for token in raw_tokens:
        if token != '?':
            tokens.append(STEMMER.stem(token))

    return tokens


def main():
    docLookup = dict()

    partialInvertedIndex = dict()
    partialIndexCounter = 0
    postingCounter = 0

    # extracting folders from DEV
    folders = listDirNoHidden(DEV_DIRECTORY)

    # extracting json files from folders
    jsonFiles = [] 
    for folder_name in folders:
        files = os.listdir(os.path.join(DEV_DIRECTORY, folder_name))  # json files

        for index, file_path in enumerate(files):
            files[index] = os.path.join(DEV_DIRECTORY, folder_name, file_path)

        jsonFiles.extend(files)

    # create directory to store partial indices
    if not os.path.exists(PARTIAL_INDICES_DIRECTORY):
        os.makedirs(PARTIAL_INDICES_DIRECTORY)

    # creating lookup for documents, building inverted index
    for docID, file_path in enumerate(jsonFiles):
        # print(docID)    # sanity check
        with open(file_path, 'r',  encoding="utf-8") as f:
            page = json.load(f)
            docLookup[docID] = page['url']

            content = page['content']
            soup = BeautifulSoup(content, 'lxml')

            # gathering text
            text = soup.get_text()

            # tokenizing
            tokens = processText(text)

            # calculating frequencies
            frequencies = dict()
            for token in tokens:
                if token in frequencies:
                    frequencies[token] += 1
                else:
                    frequencies[token] = 1

            # searching for important text
            fields = dict()
            for token in frequencies:
                fields[token] = 0

            tags = ['title', 'b', 'strong', 'h1', 'h2', 'h3']
            for tag in tags:
                for element in soup.find_all(tag):
                    text = element.get_text()
                    if text:
                        # tokenizing
                        tokens = processText(text)

                        for token in tokens:
                            if token in fields:
                                fields[token] += 1

            # adding to partialIndexCounter
            for token, freq in frequencies.items():
                # expandable to include positions
                posting = {
                    'doc': docID,
                    'fre': freq, 
                    'fie': fields[token]    
                }

                if token in partialInvertedIndex:
                    partialInvertedIndex[token].append(posting)
                else:
                    partialInvertedIndex[token] = [posting]

                postingCounter += 1

                # saves partialInvertedIndex to txt if postingCounter is > NUM_POSTINGS
                if postingCounter > NUM_POSTINGS:
                    fileName = os.path.join(PARTIAL_INDICES_DIRECTORY, f'partial_index_{partialIndexCounter}.txt')
                    savePartialIndex(partialInvertedIndex, fileName)

                    partialInvertedIndex = dict()
                    partialIndexCounter += 1
                    postingCounter = 0

    # save docLookup
    with open('docLookup.json', 'w') as dl:
        json.dump(docLookup, dl)


if __name__ == '__main__':
    # directories
    DEV_DIRECTORY = 'DEV'
    PARTIAL_INDICES_DIRECTORY = 'partial_indices'

    # number of postings per inverted index
    NUM_POSTINGS = 100_000

<<<<<<< HEAD
    PARTIAL_INDEX_FOLDER = 'partial_indices/'
    # constant, STEMMER object
=======
    # Porter2/Snowball stemmer for english from nltk
    STEMMER = SnowballStemmer('english')
>>>>>>> 6c921174f95f867537e65ca8c8d5a8faada65534

    # replacement pairs for regex
    REP = {"'": '', ".": '', ",": ' ', "/": ' '}
    REP = dict((re.escape(k), v) for k, v in REP.items()) 
    PATTERN = re.compile("|".join(REP.keys()))

    # uncomment if you've never downloaded nltk - it's a  necessary download
    # nltk.download('punkt')

    main()