# LoadingWidget.py
# (C)2014
# Scott Ernst

from PySide import QtGui

from pyglass.widgets.PyGlassWidget import PyGlassWidget

#___________________________________________________________________________________________________ LoadingWidget
class LoadingWidget(PyGlassWidget):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        """Creates a new instance of LoadingWidget."""
        super(LoadingWidget, self).__init__(parent, **kwargs)

        self._animatedIcon = QtGui.QMovie(self.getResourcePath('loader.gif'))
        self.loadImageLabel.setMovie(self._animatedIcon)

        self.target    = None
        self.isShowing = False

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: header
    @property
    def header(self):
        return self.headerLabel.text()
    @header.setter
    def header(self, value):
        self.headerLabel.setText(value)

#___________________________________________________________________________________________________ GS: info
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

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _activateWidgetDisplayImpl
    def _activateWidgetDisplayImpl(self, **kwargs):
        self.isShowing = True
        self._animatedIcon.start()

#___________________________________________________________________________________________________ _deactivateWidgetDisplayImpl
    def _deactivateWidgetDisplayImpl(self, **kwargs):
        self.isShowing = False
        self._animatedIcon.stop()

