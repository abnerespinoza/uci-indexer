# query.py

import time
import nltk
import ujson

from nltk.stem.snowball import SnowballStemmer


def main():
    urlLookup = None

    indexNU = None
    indexAL = None
    indexMZ = None

    with open('url_Lookup.ujson', 'r') as url, open('mem_nu.ujson', 'r') as nu, open('mem_al.ujson', 'r') as al, open('mem_mz.ujson', 'r') as mz:
        urlLookup = ujson.load(url)
        indexNU = ujson.load(nu)
        indexAL = ujson.load(al)
        indexMZ = ujson.load(mz)

    while True:
        inp = input('> ')
        raw_tokens = nltk.word_tokenize(inp)  

        start = time.time()

        # will probably need to remove because token count can specify importance
        raw_tokens = list(set(raw_tokens))

        # removing all tokens that are wholly not alphanumeric
        index = len(raw_tokens) - 1
        while index >= 0:
            if not raw_tokens[index][0].isalnum() or not raw_tokens[index][-1].isalnum():
                raw_tokens.pop(index)
            index -= 1
            
        stemmer = SnowballStemmer("english")
        tokens = [stemmer.stem(token) for token in raw_tokens]

        # removing all tokens that are wholly not alphanumeric
        index = len(tokens) - 1
        while index >= 0:
            if not tokens[index][0].isalnum() or not tokens[index][-1].isalnum():
                tokens.pop(index)
            index -= 1

        # indices = dict()
        # for token in tokens:
        #     lookup = None
        #     if token[0].isnumeric():
        #         lookup = indexNU
        #     elif token[0] < 'm':
        #         lookup = indexAL
        #     else:
        #         lookup = indexMZ

        #     if token in lookup:
        #         indices[token] = lookup[token]

        docIDs = []
        for token in tokens:
            lookup = None
            if token[0].isnumeric():
                lookup = indexNU
            elif token[0] < 'm':
                lookup = indexAL
            else:
                lookup = indexMZ

            if token in lookup:
                s = set(t['ur'] for t in lookup[token])
                docIDs.append(s)

        # docIDs = []
        # for token, val in indices.items():
        #     s = set()
        #     for id in val:
        #         file_path = '{}/ii_{}.json'.format(RAW_INDICES_DIRECTORY, id)
        #         with open(file_path, 'r') as f:
        #             document = ujson.load(f)
        #             index = document['index']

        #             s.update([t['ur'] for t in index[token]])

        #     docIDs.append(s)
        
        interDocIDs = set()
        for s in docIDs:
            if not interDocIDs:
                interDocIDs = s
            else:
                interDocIDs = interDocIDs.intersection(s)

        urls = []
        for docID in interDocIDs:
            docID = str(docID)
            urls.append(urlLookup[docID])

        retrieval_time = time.time() - start

        for i, url in enumerate(urls):
            if i == 10:
                break
            print(url)

        print()
        print('retrieval time: {}'.format(retrieval_time))

if __name__ == '__main__':
    # constant, file path for RAW INDICES folder
    RAW_INDICES_DIRECTORY = 'raw_indices'

    main()