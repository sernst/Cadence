# initializeStatsEnv.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os

from pyaid.file.FileUtils import FileUtils
from pyaid.string.StringUtils import StringUtils
from pyaid.system.SystemUtils import SystemUtils

rootPath = FileUtils.getDirectoryOf(__file__)

#---------------------------------------------------------------------------------------------------
# INPUTS

inputPath = FileUtils.createPath('input', isDir=True)
if os.path.exists(inputPath):
    SystemUtils.remove(inputPath)
os.makedirs(inputPath)

localDatabasePath = FileUtils.createPath(
    rootPath, '..', 'resources', 'local', 'apps', 'Cadence', 'data', isDir=True)

if not os.path.exists(localDatabasePath):
    print('[ERROR]: No local database resource folder exists')
    sys.exit(1)

for filename in os.listdir(localDatabasePath):
    if StringUtils.begins(filename, '.'):
        # Skip '.' hidden files
        continue

    source = FileUtils.createPath(localDatabasePath, filename)
    target = FileUtils.createPath(inputPath, filename)

    if not SystemUtils.copy(source, target):
        print('[ERROR]: Failed to copy "%s" database file from local app resources' % filename)
        sys.exit(2)
    print('[COPIED]: %s -> %s' % (
        filename,
        target.replace(FileUtils.getDirectoryOf(rootPath), '') ))

#---------------------------------------------------------------------------------------------------
# OUTPUTS

outputPath = FileUtils.createPath(rootPath, 'output', isDir=True)
if os.path.exists(outputPath):
    SystemUtils.remove(outputPath)
os.makedirs(outputPath)

