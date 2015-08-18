# CadenceMainWindow.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from PySide import QtCore

from pyaid.OsUtils import OsUtils
from pyaid.string.StringUtils import StringUtils
from pyglass.alembic.AlembicUtils import AlembicUtils

from pyglass.windows.PyGlassWindow import PyGlassWindow

# AS NEEDED: from cadence.models import tracks
from cadence.views.home.CadenceHomeWidget import CadenceHomeWidget
from cadence.views.loading.LoadingWidget import LoadingWidget
from cadence.views.status.StatusWidget import StatusWidget
from cadence.views.tools.CadenceToolViewerWidget import CadenceToolViewerWidget

#_______________________________________________________________________________
class CadenceMainWindow(PyGlassWindow):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        PyGlassWindow.__init__(
            self,
            widgets={
                'home':CadenceHomeWidget,
                'toolViewer':CadenceToolViewerWidget },
            title='Cadence Toolset',
            keyboardCallback=self._handleKeyboardCallback,
            **kwargs )
        self.setMinimumSize(1024,480)
        self.setContentsMargins(0, 0, 0, 0)

        self.addApplicationLevelWidget('loading', LoadingWidget)
        self.addApplicationLevelWidget('status', StatusWidget)

        self.showLoading(self)

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def showLoading(self, target, header = 'Loading', info = '(Please Stand By)', **kwargs):
        super(CadenceMainWindow, self).showLoading(target=target, header=header, info=info, **kwargs)

#_______________________________________________________________________________
    def showStatus(self, target, header, info, clear =True):
        self.showApplicationLevelWidget('status', target=target, header=header, info=info, clear=clear)

#_______________________________________________________________________________
    def appendStatus(self, target, message, formatAsHtml =True):
        w = self.getApplicationLevelWidget('status')
        if not w.isShowing or w.target != target:
            return

        message = StringUtils.toText(message).replace('\r', '')
        if formatAsHtml:
            parts = []
            for p in message.strip().split('\n'):
                parts.append(p.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;'))
            message = '<br/>'.join(parts)
        else:
            message = '<div>%s</div>' % message

        w.append(message)
        self.refreshGui()

#_______________________________________________________________________________
    def clearStatus(self, target):
        w = self.getApplicationLevelWidget('status')
        if not w.isShowing or w.target != target:
            return

        w.clear()
        self.refreshGui()

#_______________________________________________________________________________
    def showStatusDone(self, target):
        w = self.getApplicationLevelWidget('status')
        if not w.isShowing or w.target != target:
            return

        w.showStatusDone()
        self.refreshGui()

#_______________________________________________________________________________
    def hideStatus(self, target):
        self.hideApplicationLevelWidget('status')

#_______________________________________________________________________________
    def toggleInteractivity(self, value):
        if self._currentWidget.widgetID == 'home':
            self.setEnabled(value)
        else:
            if value and not self.isEnabled():
                self.setEnabled(value)
            self._currentWidget.toggleInteractivity(value)
        self.refreshGui()

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _initializeImpl(self, *args, **kwargs):
        # Initialize databases
        import cadence.models.tracks as tracks
        headRevision = AlembicUtils.getHeadDatabaseRevision(databaseUrl=tracks.DATABASE_URL)
        myRevision = AlembicUtils.getCurrentDatabaseRevision(databaseUrl=tracks.DATABASE_URL)
        print('[TRACKS]: %s [HEAD %s]' % (myRevision, headRevision))

        import cadence.models.analysis as analysis
        headRevision = AlembicUtils.getHeadDatabaseRevision(databaseUrl=analysis.DATABASE_URL)
        myRevision = AlembicUtils.getCurrentDatabaseRevision(databaseUrl=analysis.DATABASE_URL)
        print('[ANALYSIS]: %s [HEAD %s]' % (myRevision, headRevision))

        super(CadenceMainWindow, self)._initializeImpl()

#_______________________________________________________________________________
    def _firstShowImpl(self):
        self.hideLoading(self)
        self.setActiveWidget('home')

#===============================================================================
#                                                                                 H A N D L E R S

#_______________________________________________________________________________
    def _handleKeyboardCallback(self, event):
        mod  = event.modifiers()
        mods = QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier
        if mod != mods:
            if OsUtils.isMac():
                mods = QtCore.Qt.ShiftModifier | QtCore.Qt.MetaModifier
                if mod != mods:
                    return False
            else:
                return False

        op = self.windowOpacity()

        if event.key() in [QtCore.Qt.Key_Plus, QtCore.Qt.Key_Equal]:
            op = min(1.0, op + 0.2)
        elif event.key() in [QtCore.Qt.Key_Minus, QtCore.Qt.Key_Underscore]:
            op = max(0.2, op - 0.2)
        else:
            return False

        self.setWindowOpacity(op)
        return True

