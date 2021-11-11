import os


DEV_DIRECTORY = 'DEV'


# for loop below (for folder_name in folders) raised an error when hidden files' names
#   were appended to DEV_DIRECTORY. Eg .DS_STORE
#
# solution: https://stackoverflow.com/questions/7099290/how-to-ignore-hidden-files-using-os-listdir
def listdir_nohidden(path):
    f_names = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            f_names.append(f)
    return f_names


docLookup = {}
def main():
    # extracting folders from DEV
    folders = listdir_nohidden(DEV_DIRECTORY)

    # extracting json files from folders
    json_files = []
    for folder_name in folders:
        js = os.listdir(DEV_DIRECTORY + '/' + folder_name) 
        json_files.extend(js)

    # creating lookup for documents
    for docID, page in enumerate(json_files):
        docLookup[docID] = page
    
    print(docLookup)

if __name__ == '__main__':
    main()