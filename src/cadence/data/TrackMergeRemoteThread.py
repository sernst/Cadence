# TrackMergeRemoteThread.py
# (C)2014
# Scott Ernst

from pyaid.IterationCounter import IterationCounter

from pyglass.threading.RemoteExecutionThread import RemoteExecutionThread

from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ TrackMergeRemoteThread
class TrackMergeRemoteThread(RemoteExecutionThread):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, session, tracks =None, **kwargs):
        """Creates a new instance of TrackMergeRemoteThread."""
        self._session = session
        self._tracks = tracks
        super(TrackMergeRemoteThread, self).__init__(parent, **kwargs)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _runImpl
    def _runImpl(self):
        """Doc..."""

        model   = Tracks_Track.MASTER
        session = self._session if self._session else model.createSession()
        tracks  = self._tracks

        if not tracks:
            tracks = session.query(model).all()

        counter = IterationCounter(len(tracks), majorIntervalCount=10)
        for track in tracks:

            track.mergeToStorage(session)

            if counter.isMajorInterval:
                self._log.write(u'<div>Merging %s complete</div>' % counter.prettyPrintProgress)
            counter.increment()

        if not self._session:
            session.commit()
            session.close()


