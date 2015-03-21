# TrackLine.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.util.math2D.Vector2D import Vector2D

#*************************************************************************************************** StrideLine
class StrideLine(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, track, series):
        """Creates a new instance of StrideLine."""
        pairTrack = series.tracks[-2] \
            if track == series.tracks[-1] else \
            series.tracks[series.tracks.index(track) + 1]

        self._track = track
        self._pairTrack = pairTrack

        # Z and X are swapped here for a 2D projection into a Right-Handed Coordinate system
        if self.isNext:
            self._vector = Vector2D(pairTrack.z - track.z, pairTrack.x - track.x)
        else:
            self._vector = Vector2D(track.z - pairTrack.z, track.x - pairTrack.x)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: angle
    @property
    def angle(self):
        return Vector2D(1, 0).angleBetween(self.vector)

#___________________________________________________________________________________________________ GS: isNext
    @property
    def isNext(self):
        return self.track.next == self.pairTrack.uid

#___________________________________________________________________________________________________ GS: vector
    @property
    def vector(self):
        return self._vector

#___________________________________________________________________________________________________ GS: track
    @property
    def track(self):
        return self._track

#___________________________________________________________________________________________________ GS: pairTrack
    @property
    def pairTrack(self):
        return self._pairTrack

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

