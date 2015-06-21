# deployResults.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import sys

from pyaid.file.FileUtils import FileUtils
from pyaid.json.JSON import JSON
from pyaid.system.SystemUtils import SystemUtils

FOLDER_NAME = 'Statistical-Results'

#---------------------------------------------------------------------------------------------------

rootPath = FileUtils.getDirectoryOf(__file__)
localAnalysisPath = FileUtils.makeFolderPath(rootPath, '..', 'resources', 'local', 'analysis')
analysisConfigPath = FileUtils.makeFilePath(localAnalysisPath, 'analysis.json')

config = JSON.fromFile(analysisConfigPath)

if 'OUTPUT_PATH' not in config:
    rootTargetPath = localAnalysisPath
else:
    rootTargetPath = FileUtils.cleanupPath(config['OUTPUT_PATH'], isDir=True)

targetPath = FileUtils.makeFolderPath(rootTargetPath, FOLDER_NAME)

if os.path.exists(targetPath):
    SystemUtils.remove(targetPath)

outputPath = FileUtils.makeFolderPath(rootPath, 'output')

if not SystemUtils.copy(outputPath, targetPath, echo=True):
    print('[FAILED]: Deployment')
    sys.exit(1)

print('Deployment Complete')
