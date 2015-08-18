# LoadingWidget.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from PySide import QtGui

from pyaid.ArgsUtils import ArgsUtils

from pyglass.widgets.ApplicationLevelWidget import ApplicationLevelWidget

#_______________________________________________________________________________
class LoadingWidget(ApplicationLevelWidget):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, parent, **kwargs):
        """Creates a new instance of LoadingWidget."""
        super(LoadingWidget, self).__init__(parent, **kwargs)

        self._animatedIcon = QtGui.QMovie(self.getResourcePath('loader.gif'))
        self.loadImageLabel.setMovie(self._animatedIcon)

        self.target    = None
        self.isShowing = False
        self.setVisible(False)

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def header(self):
        return self.headerLabel.text()
    @header.setter
    def header(self, value):
        self.headerLabel.setText(value)

#_______________________________________________________________________________
    @property
    def info(self):
        return self.infoLabel.text()
    @info.setter
    def info(self, value):
        if value is None:
            self.infoLabel.setVisible(False)
            return

        self.infoLabel.setVisible(True)
        self.infoLabel.setText(value)

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _activateWidgetDisplayImpl(self, **kwargs):
        super(LoadingWidget, self)._activateWidgetDisplayImpl(**kwargs)
        self.target     = ArgsUtils.get('target', None, kwargs)
        self.header     = ArgsUtils.get('header', None, kwargs)
        self.info       = ArgsUtils.get('info', None, kwargs)
        self.isShowing  = True
        self._animatedIcon.start()

#_______________________________________________________________________________
    def _deactivateWidgetDisplayImpl(self, **kwargs):
        super(LoadingWidget, self)._deactivateWidgetDisplayImpl(**kwargs)
        self.isShowing = False
        self._animatedIcon.stop()

