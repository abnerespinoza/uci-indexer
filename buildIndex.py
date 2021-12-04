# buildIndex.py

import re
import os
import json
import math
import nltk

from nltk.util import ngrams
from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer


# returns directories of all non-hidden files
def listDirNoHidden(path):
    f_names = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            f_names.append(f)
    return f_names
 

# {'docID': x, 'tf-idf': y, 'fields': z}
def savePartialIndex(invertedIndex, filePath): 
    with open(filePath, 'w', encoding='utf-8') as f:
        # iterate through sorted keys of inverted index
        for token in sorted(invertedIndex):
            f.write(f'{token} {json.dumps(invertedIndex[token])}\n')


def get_twograms(tokens):
    twograms = ngrams(tokens, 2)
    twograms = ['_'.join(grams) for grams in twograms]
    return twograms


def process_text(text: str, n: int = 10_000_000):
    # replacement pairs for regex
    REP = {"'": '', ".": '', ",": ' ', "/": ' '}
    REP = dict((re.escape(k), v) for k, v in REP.items()) 
    PATTERN = re.compile("|".join(REP.keys()))

    # STEMMER object
    STEMMER = SnowballStemmer('english')

    text = PATTERN.sub(lambda m: REP[re.escape(m.group(0))], text)

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

    twograms = get_twograms(tokens)
    tokens.extend(twograms)

    return tokens


def main():
    docLookup = dict()
    anchorLookup = dict()
    pageRankLookup = dict()
    
    postingCounter = 0
    partialIndexCounter = 0
    partialInvertedIndex = dict()

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
        # sanity's sake
        if (docID % 100) == 0:
            print(docID)

        with open(file_path, 'r',  encoding="utf-8") as f:
            page = json.load(f)
            docLookup[docID] = page['url']

            content = page['content']
            soup = BeautifulSoup(content, 'lxml')

            # gathering text
            text = soup.get_text()

            # tokenizing
            tokens = process_text(text)

            # calculating frequencies
            frequencies = dict()
            for token in tokens:
                if token in frequencies:
                    frequencies[token] += 1
                else:
                    frequencies[token] = 1

            # calculating tf
            for token in frequencies:
                count = frequencies[token]
                frequencies[token] = 1 + math.log10(count)

            # searching for important text
            fields = dict()
            for token in frequencies:
                fields[token] = 0

            tags = ['title', 'b', 'strong', 'h1', 'h2', 'h3']
            for tag in tags:
                elements = soup.find_all(tag)
                for element in elements:
                    text = element.get_text()
                    if text:
                        # tokenizing
                        tokens = process_text(text)

                        for token in tokens:
                            if token in fields:
                                fields[token] += 1
            
            # indexing anchor text, implementing pagerank
            for element in soup.find_all('a', href=True):
                url = element['href']
                text = element.get_text()
                if text:
                    # tokenizing
                    tokens = process_text(text)

                    # indexing anchor text
                    if token in anchorLookup:
                        anchorLookup[token].append(url)
                    else:
                        anchorLookup[token] = [url]
                
                # implementing page rank
                if url != page['url']:
                    if url in pageRankLookup:
                        pageRankLookup[url] += 1
                    else:
                        pageRankLookup[url] = 1

            # log normalize fields
            for token in fields:
                if fields[token] == 0:
                    fields[token] = 1
                elif fields[token] == 1:
                    fields[token] = 1.2
                else:
                    fields[token] = 1 + math.log10(fields[token])
 
            # adding to inverted index
            for token, freq in frequencies.items():
                # expandable to include positions
                posting = {
                    'doc': docID,
                    'tf' : freq, 
                    'fi' : fields[token]    
                }

                if token in partialInvertedIndex:
                    partialInvertedIndex[token].append(posting)
                else:
                    partialInvertedIndex[token] = [posting]

                postingCounter += 1

                if postingCounter > NUM_POSTINGS:
                    fileName = os.path.join(PARTIAL_INDICES_DIRECTORY, f'partial_index_{partialIndexCounter}.txt')
                    savePartialIndex(partialInvertedIndex, fileName)

                    partialInvertedIndex = dict()
                    partialIndexCounter += 1
                    postingCounter = 0

    fileName = os.path.join(PARTIAL_INDICES_DIRECTORY, f'partial_index_{partialIndexCounter}.txt')
    savePartialIndex(partialInvertedIndex, fileName)

    # save docLookup, anchorLookup
    with open('docLookup.json', 'w') as dl, open('anchorLookup.json', 'w') as al, open('pageRankLookup.json', 'w') as prl:
        json.dump(docLookup, dl)
        json.dump(anchorLookup, al)
        json.dump(pageRankLookup, prl)


if __name__ == '__main__':
    # DEV folder path
    DEV_DIRECTORY = 'DEV'

    # partial_indices folder path
    PARTIAL_INDICES_DIRECTORY = 'partial_indices'

    # allowed number of postings per index
    NUM_POSTINGS = 100_000

    # uncomment if you've never used nltk - it's a necessary download, else nltk can't tokenize
    nltk.download('punkt')

    main()