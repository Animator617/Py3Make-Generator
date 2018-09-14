#!/usr/bin/python3

# * class to parse a json file - done
# * expand BuildJson class - done
# * class to generate a Makefile - in progress
# * add documentation - not started
# * possibility to skip catalog or file while scan workspace - not started

import sys
import os
import platform
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

    def getWindowsIncludeDir(self):
        return self.getIncludeDir()['win32']

    def getLinuxIncludeDir(self):
        return self.getIncludeDir()['linux']

    def getLibs(self):
        return self.getCodeInfo()['libs']

    def getWindowsLibs(self):
        return self.getLibs()['win32']

    def getLinuxLibs(self):
        return self.getLibs()['linux']

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
        self.fileList = []
        self.dirsList = []
        self.destFileList = self.settingsCatalog + '/filedb'

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
        for path, subdirs, files in os.walk('.'): # subdirs is not used because os.walk() return
            for name in files:                    # list of sub-folder in folders
                for i in self.patternSources:
                    pp = '*' + i
                    if fnmatch(name, pp):
                        self.fileList.append(os.path.join(path, name))
                        self.dirsList.append(path)
        self.fileList.sort()
        self.dirsList.sort()
        if platform.system() == 'Windows':
            for i in range(0, len(self.fileList)):
                self.fileList[i] = self.fileList[i][2:] # remove '.\\'
            #for i in range(0, len(self.dirsList)):
            #    self.dirsList[i] = self.dirsList[i][2:] # remove '.\\'
            # print(self.fileList)

    def getDirs(self):
        return self.dirsList

    def getFileList(self):
        return self.fileList

class MakeConstValues:
    Includes = 'INCLUDES'
    CXXFlags = 'CXXFLAGS'
    DCXXFlags = 'DCXXFLAGS'
    LDFlags = 'LDFLAGS'
    Libs = 'LIBS'
    GCC = 'CXX'
    DefineDebug = 'DDEFINE'
    DefineRelease = 'DEFINE'

class MakeOutputsCatalogs:
    BuildMode = ['Debug', 'Release']
    App = 'bin'
    DebugApp = App + '/' + BuildMode[0]
    ReleaseApp = App + '/' + BuildMode[1]
    ObjectFiles = 'obj'
    DebugObjectFile = ObjectFiles + '/' + BuildMode[0]
    ReleaseObjectFile = ObjectFiles + '/' + BuildMode[1]

class MakefileGenerator:
    def __init__(self, settingsCat, jsonFile):
        self.settingsCatalog = settingsCat
        copyFileDir = settingsCat + '/build.json'
        if not os.path.exists(copyFileDir):
            shutil.copy('./build.json', copyFileDir)
        # compare two json file (old and new)
        # if are diffrent copy build.json to .builddb/build.json
        # and generate new makefile
        builddbFile = BuildJson(copyFileDir)
        if builddbFile.getData() != jsonFile.getData():
            # print('Makefile - build.json are different')
            shutil.copy('./build.json', copyFileDir)
        self.buildJson = jsonFile
        self.Makefile = open('Makefile', 'w')
        self.fileSourceList = []

    def __del__(self):
        self.Makefile.close()

    def writeLine(self, line):
        self.Makefile.write(line + '\n')

    def arrayToStr(self, array):
        i = ' '
        return i.join(array)

    def arrayToStrReg(self, array, reg):
        i = reg + ' '
        return i.join(array)

    def generateValues(self):
        consts = MakeConstValues()
        # INCLUDES
    def isWindows(self):
        if platform.system() == 'Linux':
            return False
        else:
            return True

    def generateMakefile(self, workspace):
        print('Start generate Makefile')
        appName = self.buildJson.getAppName()
        if self.isWindows():
            appName += '.exe'
        # get file list (.cpp)
        fileList = workspace.getFileList()
        fileListWithoutExt = []
        for i in fileList:
            fileListWithoutExt.append(os.path.splitext(i)[0])

        # targets
        fileListOnlyName = []
        for i in fileListWithoutExt:
            fileListOnlyName.append(os.path.basename(i))

        # object files
        fileListWithO = []
        for i in fileListOnlyName:
            fileListWithO.append(i + '.o')

        # create a bin catalog for executable app
        if not os.path.exists(MakeOutputsCatalogs.DebugApp):
            os.makedirs(MakeOutputsCatalogs.DebugApp)

        if not os.path.exists(MakeOutputsCatalogs.ReleaseApp):
            os.makedirs(MakeOutputsCatalogs.ReleaseApp)

        # craete a obj catalog for .o files
        if not os.path.exists(MakeOutputsCatalogs.DebugObjectFile):
            os.makedirs(MakeOutputsCatalogs.DebugObjectFile)

        if not os.path.exists(MakeOutputsCatalogs.ReleaseObjectFile):
            os.makedirs(MakeOutputsCatalogs.ReleaseObjectFile)

        # create sub-catalogs (deps from [.cpp, .c, .cxx, .cc] files)
        for i in workspace.getDirs():
            dirDebug = MakeOutputsCatalogs.DebugObjectFile  + i
            dirRelease = MakeOutputsCatalogs.ReleaseObjectFile + i
            if not os.path.exists(dirDebug):
                os.makedirs(dirDebug)
            if not os.path.exists(dirRelease):
                os.makedirs(dirRelease)

        # start write to Makefile

        # set values like CXX, CXXFLAGS, etc.
        self.writeLine(MakeConstValues.GCC + '=g++')
        self.writeLine(MakeConstValues.CXXFlags + '=' +
                       self.arrayToStr(self.buildJson.getFlagsReleaseMode()))

        self.writeLine(MakeConstValues.DCXXFlags + '=' +
                       self.arrayToStr(self.buildJson.getFlagsDebugMode()))
        tmpArray = []
        for i in self.buildJson.getDefineDebugMode():
            tmpArray.append(' -D' + i)
        self.writeLine(MakeConstValues.DefineDebug + '=' + self.arrayToStr(tmpArray))
        tmpArray.clear()
        for i in self.buildJson.getDefineReleaseMode():
            tmpArray.append(' -D' + i)
        self.writeLine(MakeConstValues.DefineRelease + '=' + self.arrayToStr(tmpArray))
        tmpArray.clear()

        if self.isWindows(): # windows
            for i in self.buildJson.getWindowsLibs():
                tmpArray.append(' -l' + i)
        else:
            for i in self.buildJson.getLinuxLibs():
                tmpArray.append(' -l' + i)

        self.writeLine(MakeConstValues.Libs + '=' + self.arrayToStr(tmpArray))
        tmpArray.clear()
        if self.isWindows():
            for i in self.buildJson.getWindowsIncludeDir():
                tmpArray.append(' -I' + i)
        else:
            for i in self.buildJson.getLinuxIncludeDir():
                tmpArray.append(' -I' + i)

        self.writeLine(MakeConstValues.Includes+'=' + self.arrayToStr(tmpArray))
        fullPathOFile = []
        for i in fileListWithoutExt:
            fullPathOFile.append(i + '.o')

        oTargets = []
        for i in fileListWithoutExt:
            oTargets.append(i + '.o')


        targetsToRemoveDebug = []
        for i in range(0, len(fileListWithO)):
            oDir = MakeOutputsCatalogs.DebugObjectFile + '/' + oTargets[i]
            targetsToRemoveDebug.append(oDir)

        targetsToRemoveRelease = []
        for i in range(0, len(fileListWithO)):
            oDir = MakeOutputsCatalogs.ReleaseObjectFile + '/' + oTargets[i]
            targetsToRemoveRelease.append(oDir)

        # main target
        self.writeLine('\n.PHONY: all')
        self.writeLine('\nall: debug release\n')
        self.Makefile.write("debug" + ': debug-target\n')
        self.writeLine('\t$(' + MakeConstValues.GCC + ') ' + self.arrayToStr(targetsToRemoveDebug)
                       + ' $(' + MakeConstValues.Libs + ') -o ' +
                       MakeOutputsCatalogs.DebugApp + '/' + appName)
        self.Makefile.write("release" + ': release-target\n')
        self.writeLine('\t$(' + MakeConstValues.GCC + ') ' + self.arrayToStr(targetsToRemoveRelease)
                       + ' $('+ MakeConstValues.Libs + ') -o ' +
                       MakeOutputsCatalogs.ReleaseApp + '/' + appName)

        # sub-targets
        self.Makefile.write('\ndebug-target:\n')
        for i in range(0, len(fileListWithO)):
            oDir = MakeOutputsCatalogs.DebugObjectFile + '/' + oTargets[i]
            self.writeLine('\t$(' + MakeConstValues.GCC + ') $(' + MakeConstValues.DefineDebug +
                           ') $(' + MakeConstValues.DCXXFlags + ') -c ' + fileList[i] + ' $(' +
                           MakeConstValues.Includes + ') -o ' + oDir)

        self.Makefile.write('\nrelease-target:\n')
        for i in range(0, len(fileListWithO)):
            oDir = MakeOutputsCatalogs.ReleaseObjectFile + '/' + oTargets[i]
            self.writeLine('\t$(' + MakeConstValues.GCC + ') $(' + MakeConstValues.DefineRelease +
                           ') $(' + MakeConstValues.CXXFlags + ') -c ' + fileList[i] + ' $(' +
                           MakeConstValues.Includes + ') -o ' + oDir)

        self.writeLine("\nclean: debug-clean release-clean")

        self.writeLine('\ndebug-clean:')
        self.writeLine('\trm ' + MakeOutputsCatalogs.DebugApp + '/' + appName + ' ' +
                       self.arrayToStr(targetsToRemoveDebug))

        self.writeLine('\nrelease-clean:')
        self.writeLine('\trm ' + MakeOutputsCatalogs.ReleaseApp + '/' + appName + ' ' +
                       self.arrayToStr(targetsToRemoveRelease))

        print('End generate Makefile')


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
   # print("includeDirExternal: " + i.join(bj.getIncludeDir()))
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
    if action == 'init': initializeProject(settingsCat)
    elif action == 'update': updateProject(settingsCat)
    elif action == 'makefile-test': testMakefile()
    elif action == 'json-test': testBuildJson()
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
