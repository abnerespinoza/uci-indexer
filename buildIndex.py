# buildIndex.py


import os
import nltk
import ujson

from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer


def listdir_nohidden(path):
    f_names = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            f_names.append(f)
    return f_names


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

            # criminal file: DEV/mondego_ics_uci_edu/95c3f9dc662f1fe7ed6982cf896e810756fda1098742bf09659f05a33d9c790a.ujson
            if url == 'http://mondego.ics.uci.edu/datasets/maven-contents.txt':
                continue

            urlLookup[url_ID] = url
            content = page['content']
            soup = BeautifulSoup(content, 'lxml')

            # gathering text
            text = ''
            tags = set(t.name for t in soup.find_all())
            for tag in tags:
                if tag == 'script' or tag == 'style':
                    continue

                for element in soup.find_all(tag):
                    if element.string:
                        t = element.string.strip()
                        t = t.replace(',', ' ')
                        text += t + ' '

            # tokenizing
            raw_tokens = nltk.word_tokenize(text)  

            # removing all tokens that are wholly not alphanumeric
            index = len(raw_tokens) - 1
            while index >= 0:
                if not raw_tokens[index][0].isalnum() or not raw_tokens[index][-1].isalnum():
                    raw_tokens.pop(index)
                index -= 1

            # can be useful in future if we need frequency % rather than token count
            # total_words = len(raw_tokens)   # can be used to calculate percent frequency within page

            # stemming
            stemmer = SnowballStemmer("english")
            tokens = [stemmer.stem(token) for token in raw_tokens]

            # removing all tokens that are wholly not alphanumeric
            index = len(tokens) - 1
            while index >= 0:
                if not tokens[index][0].isalnum() or not tokens[index][-1].isalnum():
                    tokens.pop(index)
                index -= 1

            # calculating frequencies
            frequencies = dict()
            for token in tokens:
                if token in frequencies:
                    frequencies[token] += 1
                else:
                    frequencies[token] = 1

            # adding to inverted index
            ii_items += len(frequencies)
            contains.update(frequencies.keys())

            for token, freq in frequencies.items():
                # expandable to include fields (tags), positions, etc
                posting = {
                    'url_ID': url_ID,
                    'freq': freq
                }

                if token in invertedIndex:
                    invertedIndex[token].append(posting)
                else:
                    invertedIndex[token] = [posting]

        if (ii_items >= NUM_ITEMS) or url_ID == (len(ujson_files) - 1):
            document['GUID'] = ii_guid   # unique ID of ujson file
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
    NUM_ITEMS = 22_500

    # uncomment if never used nltk - it's necessary download, else nltk can't tokenize
    # nltk.download('punkt')

    main()