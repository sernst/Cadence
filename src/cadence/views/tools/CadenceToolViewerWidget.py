# CadenceToolViewerWidget.py
# (C)2013
# Scott Ernst

import os
import markdown

from PySide import QtGui

from pyaid.ClassUtils import ClassUtils

from pyglass.gui.scrollArea.SimpleScrollArea import SimpleScrollArea
from pyglass.gui.web.PyGlassWebView import PyGlassWebView
from pyglass.widgets.PyGlassWidget import PyGlassWidget
from pyglass.widgets.LineSeparatorWidget import LineSeparatorWidget

#___________________________________________________________________________________________________ CadenceToolViewerWidget
class CadenceToolViewerWidget(PyGlassWidget):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _HTML_WRAPPER = """\
        <!doctype html>
        <head></head>
        <body style="font-size:70%;color:#333;">##CONTENT##</body>
        </html>
    """

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        """Creates a new instance of CadenceToolViewerWidget."""
        super(CadenceToolViewerWidget, self).__init__(parent, widgetFile=False, **kwargs)

        self._definition = None

        mainLayout = self._getLayout(self, QtGui.QVBoxLayout)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(6)

        header, headerLayout = self._createWidget(self, QtGui.QHBoxLayout, True)
        headerLayout.setContentsMargins(6, 6, 6, 0)
        label = QtGui.QLabel(header)
        label.setText(u' ')
        label.setStyleSheet("QLabel { font-size:18px; color:#333; }")
        self._headerLabel = label
        headerLayout.addWidget(label)
        headerLayout.addStretch()

        btn = QtGui.QPushButton(header)
        btn.setText('Close')
        btn.clicked.connect(self._handleCloseTool)
        headerLayout.addWidget(btn)

        focalBox, focalLayout = self._createElementWidget(self, QtGui.QHBoxLayout, True)

        self._toolScroller = SimpleScrollArea(focalBox)
        focalLayout.addWidget(self._toolScroller)
        self._toolBox = self._toolScroller.containerWidget
        self._getLayout(self._toolBox, QtGui.QVBoxLayout)
        self._containerWidget = self._toolBox

        w, l = self._createWidget(focalBox, QtGui.QHBoxLayout, True)
        self._helpBox = w

        sep = LineSeparatorWidget(w, False)
        l.addWidget(sep)
        self._helpWebView = PyGlassWebView(w)
        self._helpWebView.setFixedWidth(360)
        l.addWidget(self._helpWebView)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _activateWidgetDisplayImpl
    def _activateWidgetDisplayImpl(self, **kwargs):
        d = kwargs.get('definition', None)
        self._definition = d

        self._headerLabel.setText(d['name'])
        if d['id'] not in self._widgetClasses:
            widgetClass = ClassUtils.dynamicImport(d['module'])
            self.addWidgetChild(d['id'], widgetClass, True)
        self.setActiveWidget(d['id'])

        widget   = self._currentWidget
        helpPath = widget.getResourcePath('help.markdown', isFile=True)
        if os.path.exists(helpPath):
            f = open(helpPath, 'r+')
            md = f.read().encode('utf-8', 'ignore')
            f.close()
            result = self._HTML_WRAPPER.replace('##CONTENT##', markdown.markdown(md))
            self._helpWebView.setHtml(result)
            self._helpBox.setVisible(True)
        else:
            self._helpBox.setVisible(False)

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleCloseTool
    def _handleCloseTool(self):
        self.mainWindow.setActiveWidget('home')

