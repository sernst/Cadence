# TrackwayManagerWidget.py
# (C)2012-2013
# Scott Ernst

from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.mayan.trackway.TrackwayManager import TrackwayManager

#___________________________________________________________________________________________________ TrackwayManagerWidget
class TrackwayManagerWidget(PyGlassWidget):

#===================================================================================================
#                                                                                       C L A S S

    RESOURCE_FOLDER_PREFIX = ['tools']

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)

        self.addBtn.clicked.connect(self._addToTrackway)
        self.removeBtn.clicked.connect(self._removeFromTrackway)
        self.startBtn.clicked.connect(self._goToStart)
        self.endBtn.clicked.connect(self._goToEnd)
        self.prevBtn.clicked.connect(self._goToPrevious)
        self.nextBtn.clicked.connect(self._goToNext)
        self.updateBtn.clicked.connect(self._updateInfo)
        self.newBtn.clicked.connect(self._newTrack)

        self.adjustSize()
        self._updateInfo()

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

        self.previousLabel.setText(prev)
        self.currentLabel.setText(target)
        self.nextLabel.setText(next)

#___________________________________________________________________________________________________ _addTrack
    def _newTrack(self):
        TrackwayManager.addTrack()



