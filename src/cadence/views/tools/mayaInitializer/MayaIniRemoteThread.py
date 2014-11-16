# MayaIniRemoteThread.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from nimble.utils.MayaEnvEntry import MayaEnvEntry
from nimble.utils.MayaEnvUtils import MayaEnvUtils
from pyaid.file.FileUtils import FileUtils
from pyglass.threading.RemoteExecutionThread import RemoteExecutionThread
import elixir

import cadence

#___________________________________________________________________________________________________ MayaIniRemoteThread
class MayaIniRemoteThread(RemoteExecutionThread):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, test =True, install =True, check =False, verbose =True, **kwargs):
        """Creates a new instance of MayaIniRemoteThread."""
        super(MayaIniRemoteThread, self).__init__(parent, **kwargs)
        self._test      = test
        self._verbose   = True
        self._install   = install
        self._check     = check
        self._output    = {}

        self._cadenceEntry = MayaEnvEntry.fromRootPath(FileUtils.createPath(
            FileUtils.getDirectoryOf(cadence.__file__), noTail=True))

        self._elixirEntry = MayaEnvEntry.fromRootPath(FileUtils.createPath(
            FileUtils.getDirectoryOf(elixir.__file__), noTail=True))

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _verboseLog
    def _verboseLog(self, message):
        """_verboseLog doc..."""
        if self._verbose:
            self.log.write(message)

#___________________________________________________________________________________________________ _runImpl
    def _runImpl(self):
        """Doc..."""
        if self._check:
            return self._runCheck()

        testStr  = u'Test' if self._test else u''
        typeStr  = u'Installer' if self._install else u'Uninstaller'
        labelStr = u' '.join([testStr, typeStr]).strip()

        self._verboseLog(u'<h1>Running %s...</h1>' % labelStr)

        envFiles = MayaEnvUtils.locateMayaEnvFiles()
        if not envFiles:
            self._verboseLog(u"""\
            <p style="color:#FF6666;">Operation failed. Unable to locate a maya installation.\
            Make sure you have opened Maya at least once after installing it.</p>""")
            return 0

        for envFile in envFiles:
            self._verboseLog(
                u'<p><span style="font-weight:bold;">%s:</span> %s' % (labelStr, envFile))

            result = MayaEnvUtils.modifyEnvFile(
                envFile,
                test=self._test,
                install=self._install,
                otherPaths=[self._cadenceEntry, self._elixirEntry])

            if result is None:
                self._verboseLog(
                    u'<p style="color:#FF6666;">ERROR: %s attempt failed.</p>' % labelStr)
            else:
                for item in result.removed:
                    self._verboseLog(
                        u'<p><span style="font-weight:bold;">REMOVED:</span> %s</p>' % item.rootName)

                for item in result.added:
                    self._verboseLog(
                        u'<p><span style="font-weight:bold;">ADDED:</span> %s</p>' % item.rootName)

                self._verboseLog(
                    u'<p style="color:#33CC33;">SUCCESS: %s complete.</p>' % labelStr)

        self._verboseLog(u'<h2>Operation Complete</h2>')
        return 0

#___________________________________________________________________________________________________ _runCheck
    def _runCheck(self):
        self._verboseLog(u'<h1>Running Check...</h1>')
        envFiles = MayaEnvUtils.locateMayaEnvFiles()

        if not envFiles:
            self._verboseLog(u"""\
            <p style="color:#FF6666;">Operation failed. Unable to locate a maya installation.\
            Make sure you have opened Maya at least once after installing it.</p>""")
            self._output['success'] = False
            return 0

        for env in envFiles:
            if MayaEnvUtils.checkEnvFile(env, otherPaths=[self._cadenceEntry, self._elixirEntry]):
                self._output['success'] = True
                return 0

        self._output['success'] = False
        return 0
