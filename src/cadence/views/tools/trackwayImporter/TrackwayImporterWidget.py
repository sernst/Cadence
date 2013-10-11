# TrackwayImporterWidget.py
# (C)2013 http://cadence.ThreeAddOne.com
# Scott Ernst

from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ Viewer
class TrackwayImporterWidget(PyGlassWidget):

#===================================================================================================
#                                                                                       C L A S S

    RESOURCE_FOLDER_PREFIX = ['tools']

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayImporterWidget, self).__init__(parent, **kwargs)

        self.loadAllBtn.clicked.connect(self._handleLoadAllTracks)

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleLoadAllTracks
    def _handleLoadAllTracks(self):
        self.setEnabled(False)
        model   = Tracks_Track.MASTER
        session = model.createSession()
        entries = session.query(model).all()
        for entry in entries:
            track = entry.createTrack()
            track.generateNode()
        session.close()
        self.setEnabled(True)

