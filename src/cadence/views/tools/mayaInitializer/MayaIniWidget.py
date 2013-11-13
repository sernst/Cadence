# MayaIniWidget.py
# (C)2013
# Scott Ernst

import re
import os

import pyaid
from pyaid.OsUtils import OsUtils
from pyaid.file.FileUtils import FileUtils

import nimble

from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.util.maya.MayaUtils import MayaUtils

#___________________________________________________________________________________________________ MayaIniWidget
class MayaIniWidget(PyGlassWidget):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    RESOURCE_FOLDER_PREFIX = ['tools']

    _PYTHON_PATH_PATTERN = re.compile('PYTHONPATH=(?P<paths>[^\n\r]+)')

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        """Creates a new instance of MayaIniWidget."""
        super(MayaIniWidget, self).__init__(parent, **kwargs)

        self.runBtn.clicked.connect(self._handleExecute)
        self.reportTextEdit.setReadOnly(True)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _modifyEnvFile
    def _modifyEnvFile(self, target):
        """Doc..."""
        text = self.reportTextEdit

        pathSep = OsUtils.getPerOsValue(u';', u':')

        nimblePath = FileUtils.createPath(
            FileUtils.getDirectoryOf(nimble.__file__),
            '..', isDir=True, noTail=True)

        pyaidPath = FileUtils.createPath(
            FileUtils.getDirectoryOf(pyaid.__file__),
            '..', isDir=True, noTail=True)

        removals  = []
        additions = [nimblePath]
        if nimblePath != pyaidPath:
            additions.append(pyaidPath)

        with open(target, 'r') as f:
            contents = f.read()

        result = self._PYTHON_PATH_PATTERN.search(contents)
        if not result:
            contents += (u'\n' if contents else u'') + u'PYTHONPATH=' + pathSep.join(additions)
        else:
            paths = result.groupdict()['paths'].split(pathSep)
            index = 0
            while index < len(paths):
                if not additions:
                    break

                p = paths[index]

                # If path already exists don't add it again
                if p in additions:
                    additions.remove(p)
                    index += 1
                    continue

                # Remove unrecognized paths that import nimble or pyaid
                testPaths = [
                    FileUtils.createPath(p, u'nimble', isDir=True),
                    FileUtils.createPath(p, u'pyaid', isDir=True) ]
                for test in testPaths:
                    if os.path.exists(test):
                        paths.remove(p)
                        continue

                index += 1

            paths += additions
            contents = contents[:result.start()] + u'PYTHONPATH=' + pathSep.join(paths) \
                + u'\n' + contents[result.end():]

        for item in removals:
            text.append(u'<p REMOVED:> %s</p>' % item)

        for item in additions:
            text.append(u'<p>ADDED: %s</p>' % item)

        with open(target, 'w') as f:
            f.write(contents)

        return True

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleExecute
    def _handleExecute(self):
        self.mainWindow.setEnabled(False)
        text = self.reportTextEdit
        text.clear()
        text.append(u'<h1>Running Initializer...</h1>')
        self.refreshGui()

        envFiles = MayaUtils.locateMayaEnvFiles()
        if not envFiles:
            text.append(u"""\
            <p style="color:#FF6666;">Operation failed. Unable to locate a maya installation.\
            Make sure you have opened Maya at least once after installing it before running this
            initializer. For more details see help instructions located to the right of
            this window.</p>""")
            self.mainWindow.setEnabled(True)
            self.refreshGui()
            return

        for envFile in envFiles:
            text.append(u"""<p><span style="font-weight:bold;">Initializing:</span> %s""" % envFile)
            self.refreshGui()

            if not self._modifyEnvFile(envFile):
                text.append(
                    u"""<p style="color:#FF6666;">ERROR: Initialization attempt failed.</p>""")
            else:
                text.append(
                    u"""<p style="color:#33CC33;">SUCCESS: Initialization complete.</p>""")
            self.refreshGui()

        text.append(
            u"""<h2>Operation Complete</h2>""")
        self.mainWindow.setEnabled(True)
        self.refreshGui()
