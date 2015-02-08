# TrackSeries.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.config.ConfigsDict import ConfigsDict

from cadence.models.tracks.Tracks_Track import Tracks_Track

#*************************************************************************************************** TrackSeries
class TrackSeries(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, trackway, firstTrackUid):
        """Creates a new instance of TrackSeries."""
        self.analysisHierarchy = []

        self._trackway      = trackway
        self._firstTrackUid = firstTrackUid
        self._tracks        = []
        self._incomplete    = []
        self._isValid       = True
        self._cache         = ConfigsDict()

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: isReady
    @property
    def isReady(self):
        """ Specifies whether or not this track series is ready for analysis """
        return self.isComplete and self.isValid

#___________________________________________________________________________________________________ GS: trackwayKey
    @property
    def trackwayKey(self):
        if self.pes and self.left:
            return 'leftPes'
        elif self.pes:
            return 'rightPes'
        elif self.left:
            return 'leftManus'
        else:
            return 'rightManus'

#___________________________________________________________________________________________________ GS: isValid
    @property
    def isValid(self):
        return self._isValid

#___________________________________________________________________________________________________ GS: cache
    @property
    def cache(self):
        return self._cache

#___________________________________________________________________________________________________ GS: left
    @property
    def left(self):
        try:
            return self.tracks[0].left
        except Exception:
            return True

#___________________________________________________________________________________________________ GS: pes
    @property
    def pes(self):
        try:
            return self.tracks[0].pes
        except Exception:
            return True

#___________________________________________________________________________________________________ GS: count
    @property
    def count(self):
        return len(self.tracks) if self.tracks else 0

#___________________________________________________________________________________________________ GS: fingerprint
    @property
    def fingerprint(self):
        track = self.tracks[0]
        if track:
            return track.trackSeriesFingerprint
        return None

#___________________________________________________________________________________________________ GS: isComplete
    @property
    def isComplete(self):
        return not self.incompleteTracks

#___________________________________________________________________________________________________ GS: sitemap
    @property
    def sitemap(self):
        return self.trackway.sitemap

#___________________________________________________________________________________________________ GS: trackway
    @property
    def trackway(self):
        return self._trackway
    @trackway.setter
    def trackway(self, value):
        self._trackway = value

#___________________________________________________________________________________________________ GS: tracks
    @property
    def tracks(self):
        if self._tracks is None:
            self._tracks = []
        return self._tracks
    @tracks.setter
    def tracks(self, value):
        self._tracks = value

#___________________________________________________________________________________________________ GS: incompleteTracks
    @property
    def incompleteTracks(self):
        if self._incomplete is None:
            self._incomplete = []
        return self._incomplete
    @incompleteTracks.setter
    def incompleteTracks(self, value):
        self._incomplete = value

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ load
    def load(self):
        """load doc..."""
        if not self._firstTrackUid:
            return True

        model   = Tracks_Track.MASTER
        session = self.trackway.mySession

        nextTrackUid = self._firstTrackUid
        while nextTrackUid:
            track = session.query(model).filter(model.uid == nextTrackUid).first()
            track.trackSeries = self
            self.tracks.append(track)
            if not track.isComplete:
                self.incompleteTracks.append(track)
            nextTrackUid = track.next
        return True

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

