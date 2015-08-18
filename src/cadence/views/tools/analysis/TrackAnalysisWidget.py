# TrackAnalysisWidget.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.threading.FunctionRemoteExecutionThread import FunctionRemoteExecutionThread

from pyglass.widgets.PyGlassWidget import PyGlassWidget

#_______________________________________________________________________________
class TrackAnalysisWidget(PyGlassWidget):
    """ User interface class for handling track data IO from any of the possible sources and
        saving them to, or loading them from the database. """

#===============================================================================
#                                                                                       C L A S S

    RESOURCE_FOLDER_PREFIX = ['tools']

#_______________________________________________________________________________
    def __init__(self, parent, **kwargs):
        super(TrackAnalysisWidget, self).__init__(parent, **kwargs)

        self.runIntegrityBtn.clicked.connect(self._handleRunIntegrityTests)

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _activateWidgetDisplayImpl(self, **kwargs):
        pass

#_______________________________________________________________________________
    @classmethod
    def _runIntegrityTests(cls):
        # tester = DataIntegrityTester()
        # return tester.run()
        pass

#===============================================================================
#                                                                                 H A N D L E R S

#_______________________________________________________________________________
    def _handleRunIntegrityTests(self):
        self.mainWindow.showStatus(
            self,
            u'Integrity Testing',
            u'Running integrity test suite')

        thread = FunctionRemoteExecutionThread(self, self._runIntegrityTests)
        thread.execute(
            callback=self._handleIntegrityTestsComplete,
            logCallback=self._handleThreadLog)

#_______________________________________________________________________________
    def _handleThreadLog(self, event):
        self.mainWindow.appendStatus(self, event.get('message'))

#_______________________________________________________________________________
    def _handleIntegrityTestsComplete(self, event):
        self.mainWindow.showStatusDone(self)


