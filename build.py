#!/usr/bin/python3

# TODO:
# * class to parse a json file
# * class to generate a Makefile
# * implemente a logic
import sys
import os
import json
from fnmatch import fnmatch



class BuildJson:
    def __init__(self, filename):
        json_file = open(filename, 'r')
        self.data = json.load(json_file)
    
    def get(self, what):
        return self.data[what]


class Workspace:
    def __init__(self):
        self.pattern = ['.cpp', '.c', '.cc', '.cxx', '.py']
        self.settingsCatalog = ".builddb"
        if not os.path.exists(self.settingsCatalog):
            try:
                os.makedirs(self.settingsCatalog)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        self.fileList = [ ]

    # method get all path to .cpp/.c/.cc.cxx files
    # and save in fileList array
    def scanWorkspace(self):
        for path, subdirs, files in os.walk('.'):
            for name in files:
                for i in self.pattern:
                    if fnmatch(name, "*"+i):
                        self.fileList.append(os.path.join(path, name))

    def getFileList(self):
        return self.fileList

    def print(self):
        for i in self.fileList:
            print(i)

class MakefileGenerator:
    def __init__(self):
        print("makefile")
    
    def getWorkspace(workspace):
        return 0



def testFunction():
    test = BuildJson('build.json')
    workspce = Workspace()
    workspce.scanWorkspace()
    print(workspce.getFileList())

def initializeProject():
    print("init project")

def updateProject():
    print("update project")

def usage():
    message = "python3 build.py [args]\n" \
              "args:\n" \
              "> init - initialize project\n" \
              "> update - update a project (generate a new Makefile)\n" \
              "Example: python3 build.py init"
    print(message)

def actions(action):
    if action == "init": initializeProject()
    elif action == "update": updateProject()
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