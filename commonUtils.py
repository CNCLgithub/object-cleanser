import os, re, pickle
from glob import iglob
from pathlib import Path

def numericalSort(value):
    numbers = re.compile(r'(\d+)')
    # Only use this function for reading list of rendering files
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

def getFilesList(path, fileType='', subDirs=False, lookupStr = '', onlyDir=False, forceSort=False):
    # Example of an acceptable fileType: png, zip etc -- So not put a dot '.' at the beginning
    # onlyDir=True returns directory names only
    filesList = sorted(subDirs and iglob(path + (fileType == '' and '/**' or '/**/*.' + fileType), recursive=True) or iglob(path + (fileType == '' and '/*' or '/*.' + fileType)), key=subDirs and numericalSort or None)
    if isinstance(lookupStr, list):
        filesList = [filePath for filePath in filesList if all([luStr in filePath for luStr in lookupStr])]
    elif lookupStr != '':
        filesList = [filePath for filePath in filesList if lookupStr in filePath]
    if onlyDir:
        dirs = []
        for f in filesList:
            if os.path.isdir(f):
                dirs.append(f)
        filesList = dirs
    if forceSort:
        filesList.sort(key=lambda f: int(re.sub('\D+', '', f)))
    return filesList

def fileExist(path):
    if path != '/':
        if os.path.isdir(path):
            return True
        else:
            temp = Path(path)
            return temp.is_file()
    else:
        return False

def mkdirs(paths):
    try:
        if isinstance(paths, list) and not isinstance(paths, str):
            for path in paths:
                mkdir(path)
        else:
            mkdir(paths)
    except:
        time.sleep(random.random()/5)
        if isinstance(paths, list) and not isinstance(paths, str):
            for path in paths:
                mkdir(path)
        else:
            mkdir(paths)

def mkdir(path):
    if not fileExist(path):
        os.makedirs(path)

def savePickle(filePath, data, protocol=pickle.HIGHEST_PROTOCOL):
    with open(filePath, 'wb') as f:
        pickle.dump(data, f, protocol=protocol)