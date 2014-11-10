# CadenceMainWindow.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from PySide import QtCore

from pyaid.OsUtils import OsUtils

from pyglass.windows.PyGlassWindow import PyGlassWindow

# AS NEEDED: from cadence.models import tracks
from cadence.views.home.CadenceHomeWidget import CadenceHomeWidget
from cadence.views.loading.LoadingWidget import LoadingWidget
from cadence.views.status.StatusWidget import StatusWidget
from cadence.views.tools.CadenceToolViewerWidget import CadenceToolViewerWidget

#___________________________________________________________________________________________________ CadenceMainWindow
class CadenceMainWindow(PyGlassWindow):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
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

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ showLoading
    def showLoading(self, target, header = u'Loading', info = u'(Please Stand By)', **kwargs):
        super(CadenceMainWindow, self).showLoading(target=target, header=header, info=info, **kwargs)

#___________________________________________________________________________________________________ showStatus
    def showStatus(self, target, header, info, clear =True):
        self.showApplicationLevelWidget('status', target=target, header=header, info=info, clear=clear)

#___________________________________________________________________________________________________ appendStatus
    def appendStatus(self, target, message, formatAsHtml =True):
        w = self.getApplicationLevelWidget('status')
        if not w.isShowing or w.target != target:
            return

        message = message.replace(u'\r', u'')
        if formatAsHtml:
            parts = []
            for p in message.strip().split(u'\n'):
                parts.append(p.replace(u'\t', u'&nbsp;&nbsp;&nbsp;&nbsp;'))
            message = u'<br/>'.join(parts)
        else:
            message = u'<div>' + message + u'</div>'

        w.append(message)
        self.refreshGui()

#___________________________________________________________________________________________________ clearStatus
    def clearStatus(self, target):
        w = self.getApplicationLevelWidget('status')
        if not w.isShowing or w.target != target:
            return

        w.clear()
        self.refreshGui()

#___________________________________________________________________________________________________ showStatusDone
    def showStatusDone(self, target):
        w = self.getApplicationLevelWidget('status')
        if not w.isShowing or w.target != target:
            return

        w.showStatusDone()
        self.refreshGui()

#___________________________________________________________________________________________________ hideStatus
    def hideStatus(self, target):
        self.hideApplicationLevelWidget('status')

#___________________________________________________________________________________________________ toggleInteractivity
    def toggleInteractivity(self, value):
        if self._currentWidget.widgetID == 'home':
            self.setEnabled(value)
        else:
            if value and not self.isEnabled():
                self.setEnabled(value)
            self._currentWidget.toggleInteractivity(value)
        self.refreshGui()

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _initializeImpl
    def _initializeImpl(self, *args, **kwargs):
        # Initialize databases
        import cadence.models.tracks as tracks
        print(tracks.DATABASE_URL)
        super(CadenceMainWindow, self)._initializeImpl()

#___________________________________________________________________________________________________ _firstShowImpl
    def _firstShowImpl(self):
        self.hideLoading(self)
        self.setActiveWidget('home')

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleKeyboardCallback
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

