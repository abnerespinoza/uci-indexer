import os
import hashlib
from re import I
import nltk
import gzip
import json
from bs4 import BeautifulSoup
from buildIndex import process_text, listDirNoHidden

DEV_DIRECTORY = 'DEV_no_dups'

THRESHOLD = 0.95
N = 3
old_hash_arrays = []
all_content = [] 

def get_hash_from_page(path): #returns hash_array (for text similarity)
    # load json from file
    with open(path, 'r',  encoding="utf-8") as f:
        content = json.load(f)
        all_content.append(content)
        print(content['url'])
        # parse into tree
        soup = BeautifulSoup(content['content'], 'lxml')
        
        # gathering text
        text = soup.get_text()

        #split text words into array.
        word_array = process_text(text) 

        hash_array = text_similarity(word_array, N)

        return content['url'], hash_array

def text_similarity(word_array, n): #returns a hash array 
    hash_array = []
    selected_hash_array = []
    n_grams = nltk.ngrams(word_array, n)

    for gram in n_grams:
        #gram[0], gram[1], ... gram[n - 1]
        phrase = ''
        for i in range(n):
            phrase += gram[i]

        # hash_entry = abs(hash(phrase))
        hash_entry = int(hashlib.sha256(phrase.encode('utf-8')).hexdigest(), 16)
        hash_array.append(hash_entry)

    #choose selected hashes
    for hash_entry in hash_array:
        if hash_entry % 4 == 0:
            selected_hash_array.append(hash_entry)

    return selected_hash_array

def similarity_of_pages(hash_array1, hash_array2):
    set_hash_array1 = set(hash_array1)
    set_hash_array2 = set(hash_array2)
    union = set_hash_array1 | set_hash_array2
    intersect = set_hash_array1 & set_hash_array2

    return len(intersect) / len(union)

def is_above_threshold(threshold, hash_array1, hash_array2):
    if not hash_array1 and not hash_array2:
        print("hash arrays are empty")
        return True #edge case???
    similarity = similarity_of_pages(hash_array1, hash_array2)
    if similarity >= threshold:
        return True
    else:
        return False

if __name__ == '__main__':
    dups = 0

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
    if not os.path.exists('no_dups'):
        os.makedirs('no_dups')

    f = open("no_dups/duplicate_pages.txt", "w")
    for filepath in jsonFiles:
        (url, hash_array) = get_hash_from_page(filepath)

        duplicate_found = False
        for old_hash_array in old_hash_arrays:
            if(is_above_threshold(THRESHOLD, old_hash_array['hash_array'], hash_array)):
                #note duplicate pages name current filename from pages.
                f.write("This page: " + all_content[-1]['url'] + '\nis a duplicate of: ' + old_hash_array['url'] + "\n\n")
                dups += 1
                print("Found duplicate!!!")
                duplicate_found = True
                os.remove(filepath)
                break

        if not duplicate_found:
            old_hash_arrays.append({
                'url': url,
                'hash_array': hash_array
            })
         
    print(dups)
    f.close()

    # f = open("duplicate_pages.txt", "w")
    # for filename in os.listdir(PAGES_DIRECTORY):
    #     path_to_file = os.path.join(PAGES_DIRECTORY, filename)
        
    #     (url, hash_array) = get_hash_from_page(path_to_file)

    #     duplicate_found = False
    #     for old_hash_array in old_hash_arrays:
    #         if(is_above_threshold(THRESHOLD, old_hash_array['hash_array'], hash_array)):
    #             #note duplicate pages name current filename from pages.
    #             f.write("This page: " + all_content[-1]['url'] + '\nis a duplicate of: ' + old_hash_array['url'] + "\n\n")
    #             dups += 1
    #             print("Found duplicate!!!")
    #             duplicate_found = True

    #     if not duplicate_found:
    #         old_hash_arrays.append({
    #             'url': url,
    #             'hash_array': hash_array
    #         })

    # print(dups)
    # f.close()