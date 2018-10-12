#!/usr/bin/python3

import sys
import os
import platform
import shutil
import json
from fnmatch import fnmatch
from optparse import OptionParser

def isWindows():
    if platform.system() == 'Linux':
        return False
    else:
        return True

def arrayToString(value):
    i = ' '
    return i.join(value)

class Consts:
    JsonFileName = 'build.json'

class BuildJson:
    def __init__(self, filename):
        json_file = open(filename, 'r')
        self.data = json.load(json_file)
        json_file.close()

    def getData(self):
        return self.data

    def getVersion(self):
        return self.data['version']

    def getCompiler(self):
        return self.data['compiler']

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

    def getMsvcLibs(self):
        return self.getLibs()['msvc-lib']

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
        self.fileListWithoutExt = []
        self.fileListOnlyName = []
        self.fileListWithObject = []
        self.objectTargets = []
        self.destFileList = self.settingsCatalog + '/filedb'

    def clean(self):
        self.fileList.clear()
        self.dirsList.clear()
        self.fileListWithoutExt.clear()
        self.fileListOnlyName.clear()
        self.fileListWithObject.clear()
        self.objectTargets.clear()

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
        self.clean()
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
        if isWindows():
            for i in range(0, len(self.fileList)):
                self.fileList[i] = self.fileList[i][2:] # remove '.\\'
            #for i in range(0, len(self.dirsList)):
            #    self.dirsList[i] = self.dirsList[i][2:] # remove '.\\'
            # print(self.fileList)
        self.fileListWithoutExt.clear()
        for i in self.fileList:
            self.fileListWithoutExt.append(os.path.splitext(i)[0])

        for i in self.fileListWithoutExt:
            self.fileListOnlyName.append(os.path.basename(i))
            
        self.fileListWithObject.clear()
        for i in self.fileListOnlyName:
            self.fileListWithObject.append(i + '.o')
        # print('fileListWithoutExt: ' + arrayToString(self.fileListWithoutExt))
        # print('dirList: ' + arrayToString(self.dirsList))
        for i in self.fileListWithoutExt:
            self.objectTargets.append(i + '.o')

    def getDirs(self):
        # print('dirsList(): ' + arrayToString(self.dirsList))
        return self.dirsList

    def getFileList(self):
        # print('getFileList(): ' + arrayToString(self.fileList))
        return self.fileList

    def getFileListOnlyName(self):
        # print('getFileListOnlyName(): ' + arrayToString(self.fileListOnlyName))
        return self.fileListOnlyName

    def getFileListWithObject(self):
        # print('getFileListWithObject(): ' + arrayToString(self.fileListWithObject))
        return self.fileListWithObject

    def getObjectTargets(self):
        # print('getObjectTargets(): ' + arrayToString(self.objectTargets))
        return self.objectTargets

    def numberOfFiles(self):
        # v = len(self.fileList)
        # print ('\nfileList: ' , v)
        # v = len(self.dirsList)
        # print ('dirsList: ' , v)
        # v = len(self.fileListOnlyName)
        # print ('fileListOnlyName: ' , v)
        # v = len(self.fileListWithObject)
        # print('getFileListWithObject(): ' + arrayToString(self.fileListWithObject))
        # print ('fileListWithObject: ', v)
        # v = len(self.objectTargets)
        # print ('objectTargets: ' , v , '\n')
        return len(self.fileList)

class MakeConstValues:
    Includes = 'INCLUDES'
    CXXFlags = 'CXXFLAGS'
    DCXXFlags = 'DCXXFLAGS'
    LDFlags = 'LDFLAGS'
    Libs = 'LIBS'
    MSVCLibs = 'MSVCLIBS'
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

class PlatformDeps:
    def includes(self):
        return ''
    
    def msvcLibs(self):
        return ''

    def libs(self):
        return ''

class WindowsDeps(PlatformDeps):
    def __init__(self, buildJsonFile):
        self.buildJson = buildJsonFile

    def includes(self):
        result = []
        for i in self.buildJson.getWindowsIncludeDir():
            result.append(' -I' + i)
        return result
    
    def msvcLibs(self):
        result = []
        for i in self.buildJson.getMsvcLibs():
            result.append(' ' + i)
        return result

    def libs(self):
        result = []
        for i in self.buildJson.getWindowsLibs():
            result.append(' -l' + i)
        return result

class LinuxDeps(PlatformDeps):
    def __init__(self, buildJsonFile):
        self.buildJson = buildJsonFile

    def includes(self):
        result = []
        for i in self.buildJson.getLinuxIncludeDir():
            result.append(' -I' + i)
        return result

    # not applicable
    def msvcLibs(self):
        return ''

    def libs(self):
        result = []
        for i in self.buildJson.getLinuxLibs():
            result.append(' -l' + i)
        return result

class MakefileGenerator:
    def __init__(self, settingsCat, jsonFile):
        self.settingsCatalog = settingsCat
        copyFileDir = settingsCat + '/' + Consts.JsonFileName
        if not os.path.exists(copyFileDir):
            shutil.copy('./' + Consts.JsonFileName, copyFileDir)
        # compare two json file (old and new)
        # if are diffrent copy build.json to .builddb/build.json
        # and generate new makefile
        builddbFile = BuildJson(copyFileDir)
        if builddbFile.getData() != jsonFile.getData():
            # print('Makefile - build.json are different')
            shutil.copy('./' + Consts.JsonFileName, copyFileDir)
        self.buildJson = jsonFile
        self.Makefile = open('Makefile', 'w')
        self.fileSourceList = []

    def __del__(self):
        self.Makefile.close()

    def writeLine(self, line):
        self.Makefile.write(line + '\n')

    def createCatalogs(self, workspace):
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
            dirDebug = MakeOutputsCatalogs.DebugObjectFile + '/' + i
            dirRelease = MakeOutputsCatalogs.ReleaseObjectFile + '/' + i
            if not os.path.exists(dirDebug):
                os.makedirs(dirDebug)
            if not os.path.exists(dirRelease):
                os.makedirs(dirRelease)

    def defineValues(self):
    # set values like CXX, CXXFLAGS, etc.
        self.writeLine(MakeConstValues.GCC + '=' + self.buildJson.getCompiler())
        self.writeLine(MakeConstValues.CXXFlags + '=' +
                       arrayToString(self.buildJson.getFlagsReleaseMode()))

        self.writeLine(MakeConstValues.DCXXFlags + '=' +
                       arrayToString(self.buildJson.getFlagsDebugMode()))
        tmpArray = []
        for i in self.buildJson.getDefineDebugMode():
            tmpArray.append(' -D' + i)
        self.writeLine(MakeConstValues.DefineDebug + '=' + arrayToString(tmpArray))

        tmpArray.clear()
        for i in self.buildJson.getDefineReleaseMode():
            tmpArray.append(' -D' + i)
        self.writeLine(MakeConstValues.DefineRelease + '=' + arrayToString(tmpArray))

    def generateMakefile(self, workspace):
        print('Generates a Makefile ..', end='')
        appName = self.buildJson.getAppName()
        if isWindows():
            appName += '.exe'

        self.createCatalogs(workspace)
        # start write to Makefile
        self.defineValues()

        platform = PlatformDeps()
        if isWindows():
            platform = WindowsDeps(self.buildJson)
        else:
            platform = LinuxDeps(self.buildJson)

        self.writeLine(MakeConstValues.Libs + '=' + arrayToString(platform.libs()))
        self.writeLine(MakeConstValues.MSVCLibs + '=' + arrayToString(platform.msvcLibs()))
        self.writeLine(MakeConstValues.Includes + '=' + arrayToString(platform.includes()))

        targetsToRemoveDebug = []
        targetsToRemoveRelease = []

        for i in workspace.getObjectTargets():
            oDirDebug = MakeOutputsCatalogs.DebugObjectFile + '/' + i
            oDirRelease = MakeOutputsCatalogs.ReleaseObjectFile + '/' + i
            targetsToRemoveDebug.append(oDirDebug)
            targetsToRemoveRelease.append(oDirRelease)

        # main target
        self.writeLine('\n.PHONY: all')
        self.writeLine('\nall: debug release\n')
        self.writeLine("debug" + ': debug-target')
        self.writeLine('\t$(' + MakeConstValues.GCC + ') ' + arrayToString(targetsToRemoveDebug)
                       + ' $(' + MakeConstValues.Libs + ') $(' + MakeConstValues.MSVCLibs + ') -o ' +
                       MakeOutputsCatalogs.DebugApp + '/' + appName)
        self.writeLine("\nrelease" + ': release-target')
        self.writeLine('\t$(' + MakeConstValues.GCC + ') ' + arrayToString(targetsToRemoveRelease)
                       + ' $('+ MakeConstValues.Libs + ') $(' + MakeConstValues.MSVCLibs + ') -o ' +
                       MakeOutputsCatalogs.ReleaseApp + '/' + appName)

        # sub-targets
        self.writeLine('\ndebug-target:')
        for i in range(0, workspace.numberOfFiles()):
            oDir = MakeOutputsCatalogs.DebugObjectFile + '/' + workspace.getObjectTargets()[i]
            self.writeLine('\t$(' + MakeConstValues.GCC + ') $(' + MakeConstValues.DefineDebug +
                            ') $(' + MakeConstValues.DCXXFlags + ') -c ' + workspace.getFileList()[i] + ' $(' +
                            MakeConstValues.Includes + ') -o ' + oDir)

        self.writeLine('\nrelease-target:')
        for i in range(0, workspace.numberOfFiles()):
            oDir = MakeOutputsCatalogs.ReleaseObjectFile + '/' + workspace.getObjectTargets()[i]
            self.writeLine('\t$(' + MakeConstValues.GCC + ') $(' + MakeConstValues.DefineRelease +
                           ') $(' + MakeConstValues.CXXFlags + ') -c ' + workspace.getFileList()[i] + ' $(' +
                           MakeConstValues.Includes + ') -o ' + oDir)

        self.writeLine("\nclean: debug-clean release-clean")

        self.writeLine('\ndebug-clean:')
        self.writeLine('\trm ' + MakeOutputsCatalogs.DebugApp + '/' + appName + ' ' +
                       arrayToString(targetsToRemoveDebug))

        self.writeLine('\nrelease-clean:')
        self.writeLine('\trm ' + MakeOutputsCatalogs.ReleaseApp + '/' + appName + ' ' +
                       arrayToString(targetsToRemoveRelease))

        print('.. Done')

def generateProject(buildCatalog, parameters):
    workspace = Workspace(buildCatalog)
    buildJsonFile = BuildJson(parameters)
    if workspace.isChanged() == True:
        workspace.update()
        makefile = MakefileGenerator(buildCatalog, buildJsonFile)
        makefile.generateMakefile(workspace)
    else:
        print('No changes')

def usage(): # improvement this description
    message = "python3 build.py [args]\n" \
              "\t[args]:\n" \
              "\t  python3 build.py generate - generate a Makefile base on build.json file"
    return message

def actions(action, parameters):
    settingsCatalog = '.builddb'
    if action == 'generate': generateProject(settingsCatalog, parameters)
    else: usage()

def main():
    global buildJsonFileDir
    args = sys.argv[1:]
    parser = OptionParser(usage=usage())
    parser.add_option('-s', '--settings',dest='buildJsonFileDir', default='build.json')
    (option, arg) = parser.parse_args()
    buildJsonFileDir = option.buildJsonFileDir
    if not args:
        usage()
    else:
        for i in args:
            actions(i, buildJsonFileDir)
    
if __name__ == "__main__":
    main()
