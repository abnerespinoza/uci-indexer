import os
DEVDIRECTORY = 'DEV'

docIdLookup = {}
if __name__ == '__main__':
    #creating documentID lookup
    folders = os.listdir(DEVDIRECTORY)
    allFiles = []
    for folder in folders:
        files = os.listdir(DEVDIRECTORY + '/' + folder)
        allFiles.extend(files)

    docId = 1
    for page in allFiles:
        docIdLookup[page] = docId  
        docId += 1
    
    print(docIdLookup)