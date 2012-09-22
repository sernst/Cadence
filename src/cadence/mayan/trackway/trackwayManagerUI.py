# gaitGeneratorUI.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import sys

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import QUiLoader

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.mayan.trackway.TrackwayManager import TrackwayManager

#___________________________________________________________________________________________________ Viewer
class Viewer(QWidget):

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        QWidget.__init__(self)
        l = QUiLoader()
        file = QFile(CadenceEnvironment.getResourcePath('gui', 'TrackwayManagerUI.ui'))
        file.open(QFile.ReadOnly)
        myWidget = l.load(file, self)
        file.close()

        layout = QVBoxLayout()
        layout.addWidget(myWidget)
        self.setLayout(layout)

        self.widgets = []
        for item in dir(myWidget):
            item = getattr(myWidget, item)
            if isinstance(item, QWidget):
                self.widgets.append(item)

        w             = myWidget
        self.myWidget = myWidget

        w.addBtn.clicked.connect(self._addToTrackway)
        w.removeBtn.clicked.connect(self._removeFromTrackway)
        w.startBtn.clicked.connect(self._goToStart)
        w.endBtn.clicked.connect(self._goToEnd)
        w.prevBtn.clicked.connect(self._goToPrevious)
        w.nextBtn.clicked.connect(self._goToNext)
        w.updateBtn.clicked.connect(self._updateInfo)

        self.adjustSize()
        self._updateInfo()

#___________________________________________________________________________________________________ sizeHint
    def sizeHint(self, *args, **kwargs):
        size = QWidget.sizeHint(self)
        size.setWidth(self.myWidget.baseSize().width())
        size.setHeight(self.myWidget.baseSize().height())
        return size

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _addToTrackway
    def _addToTrackway(self):
        TrackwayManager.build()
        self._updateInfo()

#___________________________________________________________________________________________________ _removeFromTrackway
    def _removeFromTrackway(self):
        TrackwayManager.remove()
        self._updateInfo()

#___________________________________________________________________________________________________ _goToStart
    def _goToStart(self):
        TrackwayManager.findPrevious(start=True)
        self._updateInfo()

#___________________________________________________________________________________________________ _goToEnd
    def _goToEnd(self):
        TrackwayManager.findNext(end=True)
        self._updateInfo()

#___________________________________________________________________________________________________ _goToStart
    def _goToPrevious(self):
        TrackwayManager.findPrevious()
        self._updateInfo()

#___________________________________________________________________________________________________ _goToNext
    def _goToNext(self):
        TrackwayManager.findNext()
        self._updateInfo()

#___________________________________________________________________________________________________ _updateInfo
    def _updateInfo(self):
        w      = self.myWidget
        target = TrackwayManager.getTargets()
        if target:
            target = target[0]
            if not TrackwayManager.isFootprint(target):
                prev   = 'Not Applicable'
                target = 'Invalid Selection'
                next   = 'Not Applicable'
            else:
                prevs  = TrackwayManager.getPrevious(target)
                prev   = prevs[0] if prevs else 'None'
                nexts  = TrackwayManager.getNext(target)
                next   = nexts[0] if nexts else 'None'
        else:
            prev   = 'Unknown'
            next   = 'Unknown'
            target = 'None Found'

        w.previousLabel.setText(prev)
        w.currentLabel.setText(target)
        w.nextLabel.setText(next)

#===================================================================================================
#                                                                                     M O D U L E

app = QApplication(sys.argv)
win = Viewer()
win.show()

app.exec_()
sys.exit()
