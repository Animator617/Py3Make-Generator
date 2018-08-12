#!/usr/bin/python3

# TODO:
# * class to parse a json file - done
# * class to generate a Makefile
# * implemente a logic
# * add documentation

import sys
import os
import json
from fnmatch import fnmatch

class BuildJson:
    def __init__(self, filename):
        json_file = open(filename, 'r')
        self.data = json.load(json_file)
        json_file.close()
    
    def get(self, what):
        return self.data[what]


class Workspace:
    def __init__(self):
        self.pattern = ['.cpp', '.c', '.cc', '.cxx']
        self.settingsCatalog = ".builddb"
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
        currentFileList.seek(0)
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
            print("is diffrent")
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
    def __init__(self):
        print("makefile")
    
    def getWorkspace(workspace):
        return 0



def testFunction():
    test = BuildJson('build.json')
    workspce = Workspace()
    workspce.scanWorkspace()
    workspce.saveToFile()
   # workspce.diffFileList()
    #print(test.get('code')['libs']['linux'][0])
    print(workspce.getFileList())

def initializeProject():
    print("init project")

def updateProject(workspace):
    workspace.diffWorkspace()

def usage():
    message = "python3 build.py [args]\n" \
              "args:\n" \
              "> init - initialize project\n" \
              "> update - update a project (generate a new Makefile)\n" \
              "Example: python3 build.py init"
    print(message)

def actions(action):
    w = Workspace()
    if action == "init": initializeProject()
    elif action == "update": updateProject(w)
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