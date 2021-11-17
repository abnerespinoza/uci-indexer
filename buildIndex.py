# buildIndex.py

import os
import json
import nltk
import re

from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer

# for loop below (for folder_name in folders) raised an error when hidden files' names
#   were appended to DEV_DIRECTORY. Eg .DS_STORE
def listDirNoHidden(path):
    f_names = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            f_names.append(f)
    return f_names

#invertedIndex is dict[{'docID': 3, 'freq': 120}]
def savePartialIndex(invertedIndex, filePath): 
    print("creating partial index...")
    with open(filePath, 'w') as f:
        # iterate through sorted keys of inverted index
        for token in sorted(invertedIndex):
            # for each token, write in format-- token [Posting]
            f.write(f'{token} {json.dumps(invertedIndex[token])}\n')

def process_text(text: str, n: int = 10_000_000):
    raw_tokens = []
    if len(text) > n:
        split_text = []
        for index in range(0, len(text), n):
            split_text.append(text[index : index + n])

        split_raw_tokens = []
        for text in split_text:
            split_raw_tokens.append(nltk.word_tokenize(text))

        for li in split_raw_tokens:
            for token in li:
                raw_tokens.append(token)
    else:
        raw_tokens = nltk.word_tokenize(text)  

    # removing all tokens that are wholly not alphanumeric
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
    postingCounter = 0
    partialIndexCounter = 0
    # extracting folders from DEV
    folders = listDirNoHidden(DEV_DIRECTORY)

    # extracting json files from folders
    jsonFiles = [] 
    for folder_name in folders:
        files = os.listdir(os.path.join(DEV_DIRECTORY, folder_name))  # json files

        for index, file_path in enumerate(files):
            files[index] = os.path.join(DEV_DIRECTORY, folder_name, file_path)

        jsonFiles.extend(files)
    print(f'Found {len(jsonFiles)} files')    

    # create directory to store partial indices
    if not os.path.exists(PARTIAL_INDEX_FOLDER):
        os.makedirs(PARTIAL_INDEX_FOLDER)

    # creating lookup for documents, building inverted index
    for docID, file_path in enumerate(jsonFiles):
        print(file_path)
        with open(file_path, 'r',  encoding="utf-8") as f:
            page = json.load(f)
            docLookup[docID] = page['url']

            content = page['content']
            soup = BeautifulSoup(content, 'lxml')

            # gathering text
            text = soup.get_text()
            text = PATTERN.sub(lambda m: REP[re.escape(m.group(0))], text)
            # print(url_ID, len(text))  # debug

            # tokenizing
            tokens = process_text(text)

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
                        text = PATTERN.sub(lambda m: REP[re.escape(m.group(0))], text)

                        # tokenizing
                        tokens = process_text(text)

                        for token in tokens:
                            if token in fields:
                                fields[token] += 1

            # adding to inverted index
            for token, freq in frequencies.items():
                # expandable to include fields (tags), positions
                posting = {
                    'docID': docID,
                    'freq': freq, 
                    'fi': fields[token]     # fields
                }

                if token in partialInvertedIndex:
                    partialInvertedIndex[token].append(posting)
                else:
                    partialInvertedIndex[token] = [posting]

                postingCounter += 1
                # checks if partialInvertedIndex is > 100,000
                # after saving file, we need to find the file size.
                if postingCounter > NUM_ITEMS:
                    fileName = os.path.join(PARTIAL_INDEX_FOLDER, f'partial_index_{partialIndexCounter}.txt')
                    savePartialIndex(partialInvertedIndex, fileName)
                    partialInvertedIndex = dict()
                    partialIndexCounter += 1
                    postingCounter = 0


    # save docLookup
    with open('docLookup.json', 'w') as dl:
        json.dump(docLookup, dl)


if __name__ == '__main__':
    # constant, file path for DEV folder
    DEV_DIRECTORY = 'DEV'
        # constant, file path for RAW INDICES folder
    RAW_INDICES_DIRECTORY = 'raw_indices'

    # contant, tolerance for number of items per dictionary
    NUM_ITEMS = 100_000

    PARTIAL_INDEX_FOLDER = 'partial_indices/'
    # constant, STEMMER object
    STEMMER = SnowballStemmer('english')

    # constant, replacement pairs for regex
    REP = {"'": '', ".": '', ",": ' ', "/": ' '}
    REP = dict((re.escape(k), v) for k, v in REP.items()) 
    PATTERN = re.compile("|".join(REP.keys()))

    # uncomment if never used nltk - it's necessary download, else nltk can't tokenize
    nltk.download('punkt')

    main()