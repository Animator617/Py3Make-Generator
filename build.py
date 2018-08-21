#!/usr/bin/python3

# TODO:
# * class to parse a json file - done
# * class to generate a Makefile
# * add documentation

import sys
import os
import shutil
import json
from fnmatch import fnmatch

class BuildJson:
    def __init__(self, filename):
        json_file = open(filename, 'r')
        self.data = json.load(json_file)
        json_file.close()
    
    def getData(self):
        return self.data

    def getValue(self, what):
        return self.data[what]


class Workspace:
    def __init__(self, settingsCat):
        self.pattern = ['.cpp', '.c', '.cc', '.cxx']
        self.settingsCatalog = settingsCat
        if not os.path.exists(self.settingsCatalog):
            try:
                os.makedirs(self.settingsCatalog)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        self.fileList = [ ]
        self.destFileList = self.settingsCatalog + "/filedb"

    def saveToFile(self):
        currentFileList = open(self.destFileList, 'w')
        currentFileList.seek(0) # probably is set in the upper line, but I want to be sure
        for i in self.fileList:
            currentFileList.write(i + '\n')
        currentFileList.close()

    def diffWorkspace(self): # add try to open file
        pervList = open(self.destFileList, 'r')
        d1 = pervList.readlines()
        self.scanWorkspace()
        print(len(self.fileList))
        print(len(d1))
        if len(self.fileList) != len(d1):
            print("is different")
            self.fileList.clear() # clear old file list
            self.scanWorkspace() # get new file list
            self.saveToFile() # save to filedb file list
        else:
            print("is the same")
        pervList.close()

    # method get all path to .cpp/.c/.cc.cxx files
    # and save in fileList array
    def scanWorkspace(self):
        for path, subdirs, files in os.walk('.'):
            for name in files:
                for i in self.pattern:
                    pp = "*"+i
                    if fnmatch(name, pp):
                        self.fileList.append(os.path.join(path, name))
        self.fileList.sort()

    def getFileList(self):
        return self.fileList


class MakefileGenerator:
    def __init__(self, settingsCat):
        self.settingsCatalog = settingsCat
        copyFileDir = settingsCat + "/build.json"
        if not os.path.exists(copyFileDir):
            shutil.copy("./build.json", copyFileDir)
        # compare two json file (old and new)
        # if are diffrent copy build.json to .builddb/build.json
        # and generate new makefile
        builddbFile = BuildJson(copyFileDir)
        currentFile = BuildJson('./build.json')
        if builddbFile.getData() != currentFile.getData(): # remove white characters
            print("Makefile - build.json are different")
            shutil.copy("./build.json", copyFileDir)
            self.generateMakefile(currentFile) # generate new makefile
        else:
            print("Makefile - build.json are the same")

    def generateMakefile(self, jsonFile):
        print("Start generate Makefile")
        makefile = open('Makefile', 'w')
        makefile.write("CC=g++\n")
        makefile.write("CFLAGS=\n")
        makefile.close()
        print("End generate Makefile")


def testFunction():
    #buildFile = "build.json"
    #ws = '.builddb'
    #make = MakefileGenerator(ws)
    #test = BuildJson(buildFile)
    #workspce = Workspace(ws)
    #workspce.scanWorkspace()
    #workspce.saveToFile()
   # workspce.diffFileList()
    #print(test.get('code')['libs']['linux'][0])
    #print(workspce.getFileList())
    workspace = Workspace('.builddb')
    workspace.scanWorkspace()
    workspace.saveToFile()
    makefile = MakefileGenerator('.builddb')
    buildJson = BuildJson('build.json')
    makefile.generateMakefile(buildJson)

# only prepare to build.py update
def initializeProject(buildCat):
    workspace = Workspace(buildCat)
    workspace.scanWorkspace()
    workspace.saveToFile()
    makefile = MakefileGenerator(buildCat)
    makefile.generateMakefile()
    # print("init project")

def updateProject(buildCat):
    workspace = Workspace(buildCat)
    workspace.diffWorkspace()
    makefile = MakefileGenerator(buildCat)
    makefile.generateMakefile(BuildJson('build.json'))

def usage(): # improvement this description
    message = "python3 build.py [args]\n" \
              "args:\n" \
              "python3 build.py init - initialize project\n" \
              "python3 build.py update - update a project (generate a new Makefile)" 
    print(message)

def actions(action):
    settingsCat = '.builddb'
    if action == "init": initializeProject(settingsCat)
    elif action == "update": updateProject(settingsCat)
    elif action == "test": testFunction()
    else: usage()

def main():
    args = sys.argv[1:]
    if not args:
        usage()
    else:
        for i in args:
            actions(i)
    
if __name__ == "__main__":
    main()
