# buildIndex.py


import re
import os
import math
import nltk
import ujson

from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer


def listdir_nohidden(path: str):
    f_names = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            f_names.append(f)
    return f_names


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
    urlLookup = dict()

    document = dict()   # ujson document
    contains = set()    # set of words contains in each ujson document
    invertedIndex = dict()  # index in ujson document
    
    # extracting folders from DEV
    folders = listdir_nohidden(DEV_DIRECTORY)

    # extracting ujson files from folders
    ujson_files = [] 
    for folder_name in folders:
        files = listdir_nohidden('{}/{}'.format(DEV_DIRECTORY, folder_name))  # ujson files

        for index, file_path in enumerate(files):
            files[index] = '{}/{}/{}'.format(DEV_DIRECTORY, folder_name, file_path)

        ujson_files.extend(files)

    # creating lookup for documents, building inverted index
    ii_guid = 0     # guid for each ujson file
    ii_items = 0    # number of items in inverted index
    for url_ID, file_path in enumerate(ujson_files):
        with open(file_path, 'r') as f:
            page = ujson.load(f)

            url = page['url']
            urlLookup[url_ID] = url

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

            # adding to inverted index
            contains.update(frequencies.keys())

            # searching for import text
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

            for token, freq in frequencies.items():
                posting = {
                    'ur': url_ID,           # url_ID
                    'fr': freq,             # frequency
                    'fi': fields[token]     # fields
                }

                if token in invertedIndex:
                    invertedIndex[token].append(posting)
                else:
                    invertedIndex[token] = [posting]

                ii_items += 1
                if ii_items >= NUM_ITEMS:
                    document['guid'] = ii_guid   # unique ID of ujson file
                    document['contains'] = list(contains)  # words contains within ujson file
                    document['index'] = invertedIndex

                    file_name = '{}/ii_{}.ujson'.format(RAW_INDICES_DIRECTORY, ii_guid)
                    with open(file_name, 'w+') as ii:
                        ujson.dump(document, ii)

                    document = dict()
                    contains = set()
                    invertedIndex = dict()

                    ii_guid += 1
                    ii_items = 0

        ii_items += 1
        if url_ID == (len(ujson_files) - 1):
            document['guid'] = ii_guid   # unique ID of ujson file
            document['contains'] = list(contains)  # words contains within ujson file
            document['index'] = invertedIndex

            file_name = '{}/ii_{}.ujson'.format(RAW_INDICES_DIRECTORY, ii_guid)
            with open(file_name, 'w+') as ii:
                ujson.dump(document, ii)

            document = dict()
            contains = set()
            invertedIndex = dict()

            ii_guid += 1
            ii_items = 0

    # save urlLookup
    with open('url_Lookup.ujson', 'w') as dl:
        ujson.dump(urlLookup, dl)


if __name__ == '__main__':
    # constant, file path for DEV folder
    DEV_DIRECTORY = 'DEV'

    # constant, file path for RAW INDICES folder
    RAW_INDICES_DIRECTORY = 'raw_indices'

    # contant, tolerance for number of items per dictionary
    NUM_ITEMS = 35_000

    # constant, STEMMER object
    STEMMER = SnowballStemmer('english')

    # constant, replacement pairs for regex
    REP = {"'": '', ".": '', ",": ' ', "/": ' '}
    REP = dict((re.escape(k), v) for k, v in REP.items()) 
    PATTERN = re.compile("|".join(REP.keys()))

    # uncomment if never used nltk - it's necessary download, else nltk can't tokenize
    # nltk.download('punkt')

    main()