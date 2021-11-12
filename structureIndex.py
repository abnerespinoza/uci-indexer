# structureIndex.py


import os
import ujson


def listdir_nohidden(path):
    f_names = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            f_names.append(f)
    return f_names


def structure_index():
    new_index = dict()
    new_index_guid = 0
    new_index_count = 0

    cur_tokens = []

    ujson_files = listdir_nohidden(RAW_INDICES_DIRECTORY) 

    print(len(ujson_files)) # sanity check

    for iter, file_path in enumerate(ujson_files):
        print(iter) # sanity check
        
        file_path = '{}/{}'.format(RAW_INDICES_DIRECTORY, file_path)
        with open(file_path, 'r') as f:
            document = ujson.load(f)
            index = document['index']

            for token in index:
                data = index[token]

                lookup = None
                if token[0].isnumeric():
                    lookup = index_nu
                elif token[0] < 'm':
                    lookup = index_al
                else:
                    lookup = index_mz
                
                if token in lookup:
                    file_path = '{}/index_{}.ujson'.format(INDICES_DIRECTORY, lookup[token])
                    structured_index = None
                    with open(file_path, 'r') as f:
                        structured_index = ujson.load(f)
                        for posting in data:
                            structured_index[token].append(posting)
                    with open(file_path, 'w+') as f:
                        ujson.dump(structured_index, f)
                else:
                    new_index[token] = data
                    new_index_count += 1

                    cur_tokens.append(token)
                
                if (new_index_count >= NUM_TOKENS) or iter == (len(gen_index) - 1):
                    file_name = '{}/index_{}.ujson'.format(INDICES_DIRECTORY, new_index_guid)
                    with open(file_name, 'w+') as f:
                        ujson.dump(new_index, f)

                        for t in cur_tokens:
                            if t[0].isnumeric():
                                index_nu[t] = new_index_guid
                            elif t[0] < 'm':
                                index_al[t] = new_index_guid
                            else:
                                index_mz[t] = new_index_guid

                        new_index = dict()
                        new_index_guid += 1
                        new_index_count = 0

                        cur_tokens = []

    with open('nu_Lookup.ujson', 'w+') as nu_f, open('al_Lookup.ujson', 'w+') as al_f, open('mz_Lookup.ujson', 'w+') as mz_f:
        ujson.dump(index_nu, nu_f)
        ujson.dump(index_al, al_f)
        ujson.dump(index_mz, mz_f)


def first_pass():
    ii_files = listdir_nohidden('{}'.format(RAW_INDICES_DIRECTORY))  # ujson files

    for index_path in ii_files:
        index_path = '{}/{}'.format(RAW_INDICES_DIRECTORY, index_path)
        with open(index_path, 'r') as f:
            document = ujson.load(f)

            tokens = document['contains']
            guid = document['GUID']

            for token in tokens:
                if token in gen_index:
                    gen_index[token].append(guid) 
                else:
                    gen_index[token] = [guid]


def second_pass():
    new_index = dict()
    new_index_guid = 0
    new_index_count = 0

    print(len(gen_index.keys()))  # sanity check
    for iter, (token, val) in enumerate(gen_index.items()):
        print(iter) # sanity check

        new_index[token] = []
        for guid in val:
            file_path = '{}/ii_{}.ujson'.format(RAW_INDICES_DIRECTORY, guid)
            with open(file_path, 'r') as f:
                document = ujson.load(f)
                token_index = document['index'][token]

                new_index_count += len(token_index)
                for posting in token_index:
                    new_index[token].append(posting)

        if (new_index_count >= NUM_ITEMS) or iter == (len(gen_index) - 1):
            file_name = '{}/index_{}.ujson'.format(INDICES_DIRECTORY, new_index_guid)
            with open(file_name, 'w+') as f:
                ujson.dump(new_index, f)

            if token[0].isnumeric():
                index_nu[token] = new_index_guid
            elif token[0] < 'm':
                index_al[token] = new_index_guid
            else:
                index_mz[token] = new_index_guid

            new_index = dict()
            new_index_guid += 1
            new_index_count = 0

    with open('nu_Lookup.ujson', 'w+') as nu_f, open('al_Lookup.ujson', 'w+') as al_f, open('mz_Lookup.ujson', 'w+') as mz_f:
        ujson.dump(index_nu, nu_f)
        ujson.dump(index_al, al_f)
        ujson.dump(index_mz, mz_f)


def memory_index():
    ii_files = listdir_nohidden('{}'.format(RAW_INDICES_DIRECTORY))  # ujson files
    for index_path in ii_files:
        index_path = '{}/{}'.format(RAW_INDICES_DIRECTORY, index_path)
        with open(index_path, 'r') as f:
            document = ujson.load(f)
            index = document['index']

            for token in index:
                lookup = None
                if token[0].isnumeric():
                    lookup = index_nu
                elif token[0] < 'm':
                    lookup = index_al
                else:
                    lookup = index_mz
                
                data = index[token]
                if token in lookup:
                    for posting in data:
                        lookup[token].append(posting) 
                else:
                    lookup[token] = data

    with open('mem_nu.ujson', 'w+') as nu, open('mem_al.ujson', 'w+') as al, open('mem_mz.ujson', 'w+') as mz:
        ujson.dump(index_nu, nu)
        ujson.dump(index_al, al)
        ujson.dump(index_mz, mz)

    report()


# only functional with memory_index function. Won't make sense otherwise.
def report():
    with open('url_Lookup.ujson', 'r') as f:
        urlLookup = ujson.load(f)
        print('Number of indexed documents: {}'.format(len(urlLookup)))

    token_count = 0
    token_count += len(index_nu)
    token_count += len(index_al)
    token_count += len(index_mz)
    print('Number of unique tokens: {}'.format(token_count))

    # check total size manually

    # emphasize that it is an in-memory index


if __name__ == '__main__':
    # constant, file path for RAW INDICES folder
    RAW_INDICES_DIRECTORY = 'raw_indices'

    # constant, file path for INDICES folder
    INDICES_DIRECTORY = 'indices'

    # contant, tolerance for number of tokens per dictionary
    NUM_TOKENS = 6_500

    # contant, tolerance for number of items per dictionary
    NUM_ITEMS = 22_500

    # indexing for the inverted index
    gen_index = dict()  # general index

    index_nu = dict()   # index for tokens that start with a number
    index_al = dict()   # index for tokens that start with a-l
    index_mz = dict()   # index for tokens that start with m-z

    # first_pass()
    # second_pass()
    # structure_index()

    memory_index()