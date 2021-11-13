# buildIndex.py

import os
import json
import nltk

from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer

PARTIAL_INDEX_SIZE = 10000
PARTIAL_INDEX_FOLDER = 'partial_indices/'
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
        with open(file_path, 'r',  encoding="utf-8") as f:
            page = json.load(f)
            docLookup[docID] = page['url']

            content = page['content']
            soup = BeautifulSoup(content, 'lxml')

            # gathering text, counting words
            text = ''
            tags = set(t.name for t in soup.find_all())
            for tag in tags:
                if tag == 'script' or tag == 'style':
                    continue

                for element in soup.find_all(tag):
                    if element.string:
                        t = element.string.strip()
                        t.replace(',', ' ')
                        text += t + ' '

            # tokenizing
            raw_tokens = nltk.word_tokenize(text)  

            # removing all tokens that are wholly not alphanumeric
            index = len(raw_tokens) - 1
            while index >= 0:
                if not raw_tokens[index][0].isalnum() or not raw_tokens[index][-1].isalnum():
                    raw_tokens.pop(index)
                index -= 1

            # stemming
            stemmer = SnowballStemmer("english")
            tokens = [stemmer.stem(token) for token in raw_tokens]

            # calculating frequencies
            frequencies = dict()
            for token in tokens:
                if token in frequencies:
                    frequencies[token] += 1
                else:
                    frequencies[token] = 1

            # adding to inverted index
            for token, freq in frequencies.items():
                # expandable to include fields (tags), positions
                posting = {
                    'docID': docID,
                    'freq': freq
                }

                if token in partialInvertedIndex:
                    partialInvertedIndex[token].append(posting)

                    # checks if partialInvertedIndex is > 100,000
                    # after saving file, we need to find the file size.
                    if postingCounter > 100000:
                        fileName = os.path.join(PARTIAL_INDEX_FOLDER, f'partial_index_{partialIndexCounter}.txt')
                        savePartialIndex(partialInvertedIndex, fileName)
                        partialInvertedIndex = dict()
                        partialIndexCounter += 1
                        postingCounter = 0
                        
                else:
                    partialInvertedIndex[token] = [posting]
                postingCounter += 1

    # save docLookup
    with open('docLookup.json', 'w') as dl:
        json.dump(docLookup, dl)


if __name__ == '__main__':
    # constant, file path for DEV folder
    DEV_DIRECTORY = 'DEV'
    # constant, size of partial index
    BATCH_SIZE = 10000

    # uncomment if never used nltk - it's necessary download, else nltk can't tokenize
    #nltk.download('punkt')

    main()