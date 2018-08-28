#!/usr/bin/python3

# TODO:
# * class to parse a json file - done
# * expand BuildJson class - done
# * class to generate a Makefile - in progress
# * add documentation - not started
# * possibility to skip catalog or file while scan workspace - not started

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

    def getVersion(self):
        return self.data['version']

    def getGeneral(self):
        return self.data['general']

    def getAppName(self):
        return self.getGeneral()['appName']

    def getProjectWorkspacePath(self):
        return self.getGeneral()['projectWorkspace']
    
    def getCodeInfo(self):
        return self.data['code']

    def getIncludeDir(self):
        return self.getCodeInfo()['includeDir']

    def getIncludeDirExternal(self):
        return self.getCodeInfo()['includeDirExternal']

    def getLibs(self):
        return self.getCodeInfo()['libs']

    def getWindowsLibs(self):
        return self.getLibs()['win32']
    
    def getLinuxLibs(self):
        return self.getLibs()['linux']

    def getLibsExternal(self):
        return self.getCodeInfo()['libsExternal']
    
    def getWindowsLibsExternal(self):
        return self.getLibsExternal()['win32']
    
    def getLinuxLibsExternal(self):
        return self.getLibsExternal()['linux']

    def getDebugMode(self):
        return self.data['debug']

    def getFlagsDebugMode(self):
        return self.getDebugMode()['flags']

    def getDefineDebugMode(self):
        return self.getDebugMode()['define']

    def getReleaseMode(self):
        return self.data['release']

    def getFlagsReleaseMode(self):
        return self.getReleaseMode()['flags']

    def getDefineReleaseMode(self):
        return self.getReleaseMode()['define']


class Workspace:
    def __init__(self, settingsCat):
        self.patternSources = ['.cpp', '.c', '.cc', '.cxx']
        self.patternHeaders = ['.hpp', '.h', '.hh', '.hxx']
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
                for i in self.patternSources:
                    pp = "*"+i
                    if fnmatch(name, pp):
                        self.fileList.append(os.path.join(path, name))
        self.fileList.sort()

    def getFileList(self):
        return self.fileList


class MakefileGenerator:
    def __init__(self, settingsCat, jsonFile):
        self.settingsCatalog = settingsCat
        copyFileDir = settingsCat + "/build.json"
        if not os.path.exists(copyFileDir):
            shutil.copy("./build.json", copyFileDir)
        # compare two json file (old and new)
        # if are diffrent copy build.json to .builddb/build.json
        # and generate new makefile
        builddbFile = BuildJson(copyFileDir)
        if builddbFile.getData() != jsonFile.getData():
            print("Makefile - build.json are different")
            shutil.copy("./build.json", copyFileDir)
        self.buildJson = jsonFile
        self.Makefile = open('Makefile', 'w')
        self.fileSourceList = []

    def __del__(self):
        self.Makefile.close()

    def writeLine(self, line):
        self.Makefile.write(line + os.linesep)

    def arrayToStr(self, array):
        i = ' '
        return i.join(array)

    def arrayToStrReg(self, array, reg):
        i = ' -I'
        return i.join(reg)

    def generateValues(self):
        # INCLUDES
        tmpArray = []
        for i in self.buildJson.getIncludeDirExternal():
            tmpArray.append('-I\"'+ i + '\"' )
        self.writeLine("INCLUDES=" + self.arrayToStr(tmpArray))

    def generateMakefile(self, workspace):
        print("Start generate Makefile")
        appName = self.buildJson.getAppName()
        fileList = workspace.getFileList()
        fileListWithoutExt = []
        for i in fileList:
            fileListWithoutExt.append(os.path.splitext(i)[0])
        print(fileListWithoutExt)
        fileListOnlyName = []
        for i in fileListWithoutExt:
            fileListOnlyName.append(os.path.basename(i))
        print(fileListOnlyName)
        fileListWithO = []
        for i in fileListOnlyName:
            fileListWithO.append(i+'.o')
        self.writeLine("CC=g++")
        self.writeLine("CXXFLAGS=" + self.arrayToStr(self.buildJson.getFlagsDebugMode()))
        self.writeLine("all: " + appName)
        self.Makefile.write(appName + ': ' + self.arrayToStr(fileListWithO) + '\n')
        self.writeLine("\t$(CC) " + self.arrayToStr(fileListWithO) + " -o " + appName)

        for i in range(0, len(fileListWithO)):
            self.Makefile.write(fileListWithO[i] + ' : ' + fileList[i]+'\n')
            self.writeLine("\t$(CC) $(CXXFLAGS) " + fileList[i])

        print("End generate Makefile")


def testMakefile():
    bj = BuildJson('build.json')
    wk = Workspace('.builddb')
    wk.update()
    mk = MakefileGenerator('.builddb', bj)
    mk.generateMakefile(wk)

def testBuildJson():
    bj = BuildJson('build.json')
    print("version: " + bj.getVersion())
    print("appName: " + bj.getAppName())
    print("projectWorkspace: " + bj.getProjectWorkspacePath())
    i = ', '
    print("includeDir: " + i.join(bj.getIncludeDir()))
    print("includeDirExternal: " + i.join(bj.getIncludeDirExternal()))
    print("libs:")
    print("    win32: " + i.join(bj.getWindowsLibs()))
    print("    linux: " + i.join(bj.getLinuxLibs()))
    print("libs external:")
    print("    win32: " + i.join(bj.getWindowsLibsExternal()))
    print("    linux: " + i.join(bj.getLinuxLibsExternal()))
    print("debug mode")
    print("    flags: " + i.join(bj.getFlagsDebugMode()))
    print("    define: " + i.join(bj.getDefineDebugMode()))
    print("release mode")
    print("    flags: " + i.join(bj.getFlagsReleaseMode()))
    print("    define: " + i.join(bj.getDefineReleaseMode()))

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
    elif action == "makefile-test": testMakefile()
    elif action == "json-test": testBuildJson()
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
