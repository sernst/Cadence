# TrackSeries.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.config.ConfigsDict import ConfigsDict
from pyaid.number.NumericUtils import NumericUtils

from cadence.models.tracks.Tracks_Track import Tracks_Track

#*************************************************************************************************** TrackSeries
class TrackSeries(object):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, trackway, firstTrackUid, **kwargs):
        """Creates a new instance of TrackSeries."""
        self.analysisHierarchy = []

        self._bundle        = kwargs.get('bundle')
        self._left          = kwargs.get('left')
        self._pes           = kwargs.get('pes')
        self._trackway      = trackway
        self._firstTrackUid = firstTrackUid
        self._tracks        = []
        self._incomplete    = []
        self._isValid       = True
        self._cache         = ConfigsDict()

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def averageTrackWidth(self):
        values = []
        for t in self.tracks:
            values.append(t.widthValue)

        return NumericUtils.weightedAverage(values)

#_______________________________________________________________________________
    @property
    def averageTrackLength(self):
        values = []
        for t in self.tracks:
            values.append(t.lengthValue)

        return NumericUtils.weightedAverage(values)

#_______________________________________________________________________________
    @property
    def bundle(self):
        return self._bundle

#_______________________________________________________________________________
    @property
    def firstTrackUid(self):
        if not self.tracks:
            return None
        return self.tracks[0].uid

#_______________________________________________________________________________
    @property
    def isReady(self):
        """ Specifies whether or not this track series is ready for analysis """
        return self.isComplete and self.isValid

#_______________________________________________________________________________
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

#_______________________________________________________________________________
    @property
    def isValid(self):
        return self._isValid

#_______________________________________________________________________________
    @property
    def cache(self):
        return self._cache

#_______________________________________________________________________________
    @property
    def left(self):
        try:
            return self.tracks[0].left
        except Exception:
            return bool(self._left)

#_______________________________________________________________________________
    @property
    def pes(self):
        try:
            return self.tracks[0].pes
        except Exception:
            return bool(self._pes)

#_______________________________________________________________________________
    @property
    def count(self):
        return len(self.tracks) if self.tracks else 0

#_______________________________________________________________________________
    @property
    def fingerprint(self):
        if not self.tracks:
            return '-'.join([
            self.trackway.name,
            'L' if self.left else 'R',
            'P' if self.pes else 'M' ])

        track = self.tracks[0]
        if track:
            return track.trackSeriesFingerprint
        return None

#_______________________________________________________________________________
    @property
    def isComplete(self):
        return not self.incompleteTracks

#_______________________________________________________________________________
    @property
    def sitemap(self):
        return self.trackway.sitemap

#_______________________________________________________________________________
    @property
    def trackway(self):
        return self._trackway
    @trackway.setter
    def trackway(self, value):
        self._trackway = value

#_______________________________________________________________________________
    @property
    def tracks(self):
        if self._tracks is None:
            self._tracks = []
        return self._tracks
    @tracks.setter
    def tracks(self, value):
        self._tracks = value

#_______________________________________________________________________________
    @property
    def incompleteTracks(self):
        if self._incomplete is None:
            self._incomplete = []
        return self._incomplete
    @incompleteTracks.setter
    def incompleteTracks(self, value):
        self._incomplete = value

#_______________________________________________________________________________
    @property
    def key(self):
        return '%s%s' % (
            'left' if self.left else 'right',
            'Pes' if self.pes else 'Manus')

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
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

#===============================================================================
#                                                                               I N T R I N S I C

#_______________________________________________________________________________
    def __repr__(self):
        return self.__str__()

#_______________________________________________________________________________
    def __str__(self):
        return '<%s>' % self.__class__.__name__

