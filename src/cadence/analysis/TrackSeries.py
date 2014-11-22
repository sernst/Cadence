# TrackSeries.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#*************************************************************************************************** TrackSeries
from pyaid.list.ListUtils import ListUtils


class TrackSeries(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of TrackSeries."""
        self._tracks    = kwargs.get('tracks', [])
        self._sitemap   = kwargs.get('sitemap')
        self._trackway  = kwargs.get('trackway')

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: isComplete
    @property
    def isComplete(self):
        if not self.tracks:
            return False
        for track in self.tracks:
            if not track.isComplete:
                return False
        return True

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

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ sort
    def sort(self):
        """sort doc..."""
        ListUtils.sortObjectList(self.tracks, 'number', inPlace=True)

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

