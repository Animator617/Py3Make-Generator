#!/usr/bin/python3

# TODO:
# * class to parse a json file - done
# * class to generate a Makefile
# * implemente a logic
# * more descriton what i going on
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

    def save(self):
        currentFileList = open(self.destFileList, 'w')
        currentFileList.seek(0) # probably is set in the upper line, but I want to be sure
        for i in self.fileList:
            currentFileList.write(i + '\n')
        currentFileList.close()

    def isChanged(self):
        if not os.path.exists(self.destFileList):
            self.save()
        pervList = open(self.destFileList, 'r')
        d1 = pervList.readlines()
        pervList.close()
        self.scan()
        if len(self.fileList) != len(d1):
            return True
        else:
            return False

    def update(self):
        if self.isChanged():
            self.fileList.clear() # clear old file list
            self.scan() # get new file list
            self.save() # save to filedb file list

    # method get all path to .cpp/.c/.cc.cxx files
    # and save in fileList array
    def scan(self):
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
    workspace = Workspace('.builddb') # test workspace
    workspace.update()

    makefile = MakefileGenerator('.builddb') # test makefile
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
              "> init - initialize project\n" \
              "> update - update a project (generate a new Makefile)\n" \
              "Example: python3 build.py init"
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