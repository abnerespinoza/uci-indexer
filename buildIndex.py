# buildIndex.py


import os
import json
import nltk

from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer


# for loop below (for folder_name in folders) raised an error when hidden files' names
#   were appended to DEV_DIRECTORY. Eg .DS_STORE
def listdir_nohidden(path):
    f_names = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            f_names.append(f)
    return f_names

def create_partial_index(invertedIndex, indexNumber):
    pass

def merge_partial_indexes(indexNumbers):
    pass

def main():
    docLookup = dict()
    invertedIndex = dict()
    
    # extracting folders from DEV
    folders = listdir_nohidden(DEV_DIRECTORY)

    # extracting json files from folders
    json_files = [] 
    for folder_name in folders:
        files = os.listdir('{}/{}'.format(DEV_DIRECTORY, folder_name))  # json files

        for index, file_path in enumerate(files):
            files[index] = '{}/{}/{}'.format(DEV_DIRECTORY, folder_name, file_path)

        json_files.extend(files)

    # creating lookup for documents, building inverted index
    for docID, file_path in enumerate(json_files):
        with open(file_path, 'r') as f:
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
                        text += t + ' '

            # tokenizing
            raw_tokens = nltk.word_tokenize(text)  

            # removing all tokens that are wholly not alphanumeric
            index = len(raw_tokens) - 1
            while index >= 0:
                if not raw_tokens[index][0].isalnum():
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

                if token in invertedIndex:
                    invertedIndex[token].append(posting)
                else:
                    invertedIndex[token] = [posting]

    # save docLookup, invertedIndex
    with open('docLookup.json', 'w') as dl, open('invertedIndex.json', 'w') as ii:
        json.dump(docLookup, dl)
        json.dump(invertedIndex, ii)


if __name__ == '__main__':
    # constant, file path for DEV folder
    DEV_DIRECTORY = 'DEV'
    # constant, size of partial index
    BATCH_SIZE = 10000

    # uncomment if never used nltk - it's necessary download, else nltk can't tokenize
    nltk.download('punkt')

    main()