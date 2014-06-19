# CadenceMainWindow.py
# (C)2013-2014
# Scott Ernst

from PySide import QtCore
from PySide import QtGui

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

        widget = self._createCentralWidget()
        layout = QtGui.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)
        self._containerWidget = widget

        self._contentWidget = QtGui.QWidget(parent=widget)
        contentLayout = QtGui.QVBoxLayout(self._contentWidget)
        contentLayout.setContentsMargins(0, 0, 0, 0)
        contentLayout.setSpacing(0)
        self._contentWidget.setLayout(layout)
        layout.addWidget(self._contentWidget)

        self._centerWidget = self._contentWidget

        self._loadingWidget = LoadingWidget(self._widgetParent)
        layout.addWidget(self._loadingWidget)
        self._loadingWidget.setVisible(False)

        self._statusWidget = StatusWidget(self._widgetParent)
        layout.addWidget(self._statusWidget)
        self._statusWidget.setVisible(False)

        self.showLoading(self)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ showLoading
    def showLoading(self, target, header = u'Loading', info = u'(Please Stand By)'):
        self._loadingWidget.header = header
        self._loadingWidget.info   = info
        self._loadingWidget.target = target

        self._contentWidget.setVisible(False)
        self._statusWidget.setVisible(False)
        self._loadingWidget.setVisible(True)
        self._loadingWidget.activateWidgetDisplay()
        self.refreshGui()

#___________________________________________________________________________________________________ hideLoading
    def hideLoading(self, target):
        if not self._loadingWidget.isShowing or self._loadingWidget.target != target:
            return

        self._loadingWidget.deactivateWidgetDisplay()
        self._loadingWidget.setVisible(False)
        self._statusWidget.setVisible(False)
        self._contentWidget.setVisible(True)
        self.refreshGui()

#___________________________________________________________________________________________________ showStatus
    def showStatus(self, target, header, info, clear =True):
        self._statusWidget.header = header
        self._statusWidget.info   = info
        self._statusWidget.target = target

        if clear:
            self._statusWidget.clear()

        self._loadingWidget.setVisible(False)
        self._contentWidget.setVisible(False)
        self._statusWidget.setVisible(True)
        self._statusWidget.activateWidgetDisplay()
        self.refreshGui()

#___________________________________________________________________________________________________ updateStatus
    def appendStatus(self, target, message, formatAsHtml =True):
        if not self._statusWidget.isShowing or self._statusWidget.target != target:
            return

        message = message.replace(u'\r', u'')
        if formatAsHtml:
            parts = []
            for p in message.strip().split(u'\n'):
                parts.append(p.replace(u'\t', u'&nbsp;&nbsp;&nbsp;&nbsp;'))
            message = u'<br/>'.join(parts)
        else:
            message = u'<div>' + message + u'</div>'

        self._statusWidget.append(message)
        self.refreshGui()

#___________________________________________________________________________________________________ clearStatus
    def clearStatus(self, target):
        if not self._statusWidget.isShowing or self._statusWidget.target != target:
            return

        self._statusWidget.clear()
        self.refreshGui()

#___________________________________________________________________________________________________ showStatusDone
    def showStatusDone(self, target):
        if not self._statusWidget.isShowing or self._statusWidget.target != target:
            return

        self._statusWidget.showStatusDone()
        self.refreshGui()

#___________________________________________________________________________________________________ hideStatus
    def hideStatus(self, target):
        if not self._statusWidget.isShowing or self._statusWidget.target != target:
            return

        self._statusWidget.deactivateWidgetDisplay()
        self._statusWidget.setVisible(False)
        self._loadingWidget.setVisible(False)
        self._contentWidget.setVisible(True)
        self.refreshGui()

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
        from cadence.models import tracks
        super(CadenceMainWindow, self)._initializeImpl()

#___________________________________________________________________________________________________ _firstShowImpl
    def _firstShowImpl(self):
        self.loadWidgets()
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

