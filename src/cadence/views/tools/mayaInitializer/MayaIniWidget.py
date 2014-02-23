# MayaIniWidget.py
# (C)2013
# Scott Ernst

from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.views.tools.mayaInitializer.MayaIniRemoteThread import MayaIniRemoteThread

#___________________________________________________________________________________________________ MayaIniWidget
class MayaIniWidget(PyGlassWidget):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    RESOURCE_FOLDER_PREFIX = ['tools']

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        """Creates a new instance of MayaIniWidget."""
        super(MayaIniWidget, self).__init__(parent, **kwargs)

        self.runBtn.clicked.connect(self._handleExecute)
        self.removeBtn.clicked.connect(self._handleRemove)

        self._thread = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _runInitializer
    def _runInitializer(self, install =True, test =False):
        self.mainWindow.showStatus(self, u'Initializing Maya', u'Running Maya Initialization')

        self._thread = MayaIniRemoteThread(self, test=test, install=install)
        self._thread.execute(self._handleInitializerComplete, self._handleThreadLog)

#___________________________________________________________________________________________________ _deactivateWidgetDisplayImpl
    def _deactivateWidgetDisplayImpl(self, **kwargs):
        self.mainWindow.getWidgetFromID('home').refreshMayaStatus()

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleExecute
    def _handleExecute(self):
        self._runInitializer(install=True, test=self.testChk.isChecked())

#___________________________________________________________________________________________________ _handleRemove
    def _handleRemove(self):
        self._runInitializer(install=False, test=self.testChk.isChecked())

#___________________________________________________________________________________________________ _handleInitializerComplete
    def _handleInitializerComplete(self, response):
        self.mainWindow.showStatusDone(self)
        self.refreshGui()
        self._thread = None

#___________________________________________________________________________________________________ _handleThreadLog
    def _handleThreadLog(self, value):
        self.mainWindow.appendStatus(self, value)
