# CadenceHomeWidget.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from PySide import QtCore
from PySide import QtGui
from pyaid.ArgsUtils import ArgsUtils
from pyaid.json.JSON import JSON
from pyglass.gui.scrollArea.SimpleScrollArea import SimpleScrollArea
from pyglass.widgets.PyGlassWidget import PyGlassWidget
from pyglass.widgets.LineSeparatorWidget import LineSeparatorWidget

from cadence.enums.UserConfigEnum import UserConfigEnum
from cadence.views.home.CadenceMayaStatusElement import CadenceMayaStatusElement
from cadence.views.home.CadenceNimbleStatusElement import CadenceNimbleStatusElement


#_______________________________________________________________________________
class CadenceHomeWidget(PyGlassWidget):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, parent, **kwargs):
        """Creates a new instance of CadenceHomeWidget."""
        super(CadenceHomeWidget, self).__init__(parent, widgetFile=False, **kwargs)
        self._firstView = True

        mainLayout = self._getLayout(self, QtGui.QHBoxLayout)
        mainLayout.setContentsMargins(6, 6, 6, 6)
        mainLayout.setSpacing(6)

        self._toolScroller = SimpleScrollArea(self)
        mainLayout.addWidget(self._toolScroller)
        self._toolBox = self._toolScroller.containerWidget
        self._getLayout(self._toolBox, QtGui.QVBoxLayout)

        self._statusBox, statusLayout = self._createElementWidget(self, QtGui.QVBoxLayout, True)
        statusLayout.setSpacing(10)
        statusLayout.addStretch()

        self._mayaStatus = CadenceMayaStatusElement(self._statusBox)
        statusLayout.addWidget(self._mayaStatus)

        self._nimbleStatus = CadenceNimbleStatusElement(
            self._statusBox,
            disabled=self.mainWindow.appConfig.get(UserConfigEnum.NIMBLE_TEST_STATUS, True) )
        statusLayout.addWidget(self._nimbleStatus)

        self._populateTools()

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def refreshMayaStatus(self):
        self._mayaStatus.refresh()

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _activateWidgetDisplayImpl(self, **kwargs):
        if self._firstView:
            self.refreshMayaStatus()
            self._nimbleStatus.refresh()
            self._firstView = False

#_______________________________________________________________________________
    def _addTool(self, definition):
        widget, layout = self._createElementWidget(self._toolBox, QtGui.QVBoxLayout, True)
        layout.setContentsMargins(0, 0, 0, 6)
        layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        widget.id = 'toolItem'
        data = dict()

        layout.addWidget(LineSeparatorWidget(widget))
        layout.addSpacing(6)

        w, l = self._createWidget(widget, QtGui.QHBoxLayout, True)
        l.setAlignment(QtCore.Qt.AlignBottom)

        name = QtGui.QLabel(w)
        name.setText(definition['name'])
        name.setStyleSheet("QLabel { font-size:16px; color:#333; }")
        l.addWidget(name)
        l.addStretch()
        data['label'] = name

        btn = QtGui.QPushButton(w)
        btn.setText('Open')
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self._handleOpenTool)
        l.addWidget(btn)
        data['btn'] = btn

        desc = QtGui.QLabel(widget)
        desc.setText(definition['description'])
        desc.setStyleSheet("QLabel { font-size:11px; color:#666; }")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        data['desc'] = desc

        data['definition'] = definition
        widget.userData    = data
        return widget

#_______________________________________________________________________________
    def _populateTools(self):
        """Doc..."""

        path = self.getAppResourcePath('ToolsManifest.json', isFile=True)

        try:
            f = open(path)
            definition = JSON.fromString(f.read())
            f.close()
        except Exception as err:
            self.log.writeError('ERROR: Unable to read tools manifest file.', err)
            return

        for tool in ArgsUtils.getAsList('tools', definition):
            self._addTool(tool)

        self._toolBox.layout().addStretch()

#===============================================================================
#                                                                                 H A N D L E R S

#_______________________________________________________________________________
    def _handleOpenTool(self):
        # From the pushbutton get the element
        element = self.sender().parent().parent()

        w = self.mainWindow.getWidgetFromID('toolViewer')
        print(w)
        self.mainWindow.showLoading(w, u'Opening Tool')
        self.refreshGui()
        self.mainWindow.setActiveWidget('toolViewer', args=element.userData)
