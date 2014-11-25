# TrackSeries.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.config.ConfigsDict import ConfigsDict

from pyaid.list.ListUtils import ListUtils

#*************************************************************************************************** TrackSeries
class TrackSeries(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of TrackSeries."""
        self._fingerprint   = kwargs.get('fingerprint')
        self._tracks        = kwargs.get('tracks', [])
        self._incomplete    = kwargs.get('incomplete', [])
        self._hiddenTracks  = kwargs.get('hiddenTracks', [])
        self._sitemap       = kwargs.get('sitemap')
        self._trackway      = kwargs.get('trackway')
        self._cache         = ConfigsDict()

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: cache
    @property
    def cache(self):
        return self._cache

#___________________________________________________________________________________________________ GS: left
    @property
    def left(self):
        try:
            return self._getFirstTrack().left
        except Exception:
            return True

#___________________________________________________________________________________________________ GS: pes
    @property
    def pes(self):
        try:
            return self._getFirstTrack().pes
        except Exception:
            return True

#___________________________________________________________________________________________________ GS: count
    @property
    def count(self):
        return len(self.tracks) if self.tracks else 0


#___________________________________________________________________________________________________ GS: totalCount
    @property
    def totalCount(self):
        return self.count + \
            (len(self.hiddenTracks) if self.hiddenTracks else 0) + \
            (len(self.incompleteTracks) if self.incompleteTracks else 0)

#___________________________________________________________________________________________________ GS: fingerprint
    @property
    def fingerprint(self):
        if self._fingerprint:
            return self._fingerprint
        track = self._getFirstTrack()
        if track:
            return track.trackSeriesFingerprint
        return None
    @fingerprint.setter
    def fingerprint(self, value):
        self._fingerprint = value

#___________________________________________________________________________________________________ GS: trackwayFingerprint
    @property
    def trackwayFingerprint(self):
        track = self._getFirstTrack()
        if track:
            return track.trackwayFingerprint
        return None

#___________________________________________________________________________________________________ GS: isComplete
    @property
    def isComplete(self):
        return not self.incompleteTracks

#___________________________________________________________________________________________________ GS: sitemap
    @property
    def sitemap(self):
        if self._sitemap:
            return self._sitemap
        try:
            return self.trackway.sitemap
        except Exception:
            return None
    @sitemap.setter
    def sitemap(self, value):
        self._sitemap = value

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

#___________________________________________________________________________________________________ GS: hiddenTracks
    @property
    def hiddenTracks(self):
        if self._hiddenTracks is None:
            self._hiddenTracks = []
        return self._hiddenTracks
    @hiddenTracks.setter
    def hiddenTracks(self, value):
        self._hiddenTracks = value

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

#___________________________________________________________________________________________________ addTrack
    def addTrack(self, track):
        """addTrack doc..."""
        if not track.isComplete:
            self.incompleteTracks.append(track)
        elif track.hidden:
            self.hiddenTracks.append(track)
        else:
            self.tracks.append(track)

#___________________________________________________________________________________________________ sort
    def sort(self):
        """sort doc..."""
        ListUtils.sortObjectList(self.tracks,           'number', inPlace=True)
        ListUtils.sortObjectList(self.incompleteTracks, 'number', inPlace=True)
        ListUtils.sortObjectList(self.hiddenTracks,     'number', inPlace=True)

#___________________________________________________________________________________________________ _getFirstTrack
    def _getFirstTrack(self, allowHidden =True, allowIncomplete =True):
        """_getFirstTrack doc..."""
        if self.tracks:
            return self.tracks[0]
        if allowHidden and self.hiddenTracks:
            return self.hiddenTracks[0]
        if allowIncomplete and self.incompleteTracks:
            return self.incompleteTracks[0]

        return None

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

