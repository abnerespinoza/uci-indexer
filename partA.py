import sys
import os
import re

def tokenize(file_path):
    '''
    O(N) complexity: Goes through each line of the input file and adds each token.
    '''
    results = []
    with open(file_path, 'r') as input_file:
        line = ' '
        try:
            line = input_file.readline()
        except:
            pass
        while line:
            # tokens are alphanumeric
            results += tokenize_string(line)
            try:
                line = input_file.readline()
            except:
                pass
        return results

def tokenize_string(s):
    tokens = re.split('[^a-zA-Z0-9]', s)
    tokens = list(filter(None, tokens))
    return tokens

def compute_word_frequencies(tokens, results={}):
    '''
    O(N) complexity: Iterates through each token in the input file.
    '''
    for token in tokens:
        key = token.lower()
        if key not in results:
            results[key] = 0
        results[key] += 1
    return results

def my_print(frequencies):
    '''
    O(N log N) complexity: Relational Sorting.
    '''
    for word in sorted(frequencies, key=(lambda x: -1 * frequencies[x])):
        print(f'{word}\t{frequencies[word]}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please provide an input file!')
        exit(1)
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print('File provided does not exist!')
        exit(1)

    tokens = tokenize(file_path)
    frequencies = compute_word_frequencies(tokens)
    my_print(frequencies)