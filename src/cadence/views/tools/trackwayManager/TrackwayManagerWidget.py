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

        self.addBtn.clicked.connect(self._addToSeries)
        self.removeBtn.clicked.connect(self._removeFromSeries)
        self.startBtn.clicked.connect(self._goToStart)
        self.endBtn.clicked.connect(self._goToEnd)
        self.prevBtn.clicked.connect(self._goToPrevious)
        self.nextBtn.clicked.connect(self._goToNext)
        self.updateBtn.clicked.connect(self._updateInfo)
        self.initialBtn.clicked.connect(self._initializeSeries)
        self.newBtn.clicked.connect(self._newTrack)

        self.adjustSize()
        self._updateInfo()

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _addToSeries
    def _addToSeries(self):
        TrackwayManager.addToSeries()
        self._updateInfo()

#___________________________________________________________________________________________________ _removeFromSeries
    def _removeFromSeries(self):
        TrackwayManager.removeFromSeries()
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
            if not TrackwayManager.isTrack(target):
                prevTrack   = 'Not Applicable'
                target      = 'Invalid Selection'
                nextTrack   = 'Not Applicable'
            else:
                prevTracks  = TrackwayManager.getPreviousTracks(target)
                prevTrack   = prevTracks[0] if prevTracks else 'None'
                nextTracks  = TrackwayManager.getNextTracks(target)
                nextTrack   = nextTracks[0] if nextTracks else 'None'
        else:
            prevTrack = 'Unknown'
            nextTrack = 'Unknown'
            target    = 'None Found'

        self.previousLabel.setText(prevTrack)
        self.currentLabel.setText(target)
        self.nextLabel.setText(nextTrack)
#___________________________________________________________________________________________________ _initialize Track
    def _initializeSeries(self):
        TrackwayManager.initializeTrackway()

#___________________________________________________________________________________________________ _addTrack
    def _newTrack(self):
        TrackwayManager.newTrack()



