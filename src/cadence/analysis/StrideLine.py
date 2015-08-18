# TrackLine.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from cadence.analysis.shared.LineSegment2D import LineSegment2D

from cadence.util.math2D.Vector2D import Vector2D

#*************************************************************************************************** StrideLine
class StrideLine(object):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, track, series):
        """Creates a new instance of StrideLine."""
        pairTrack = series.tracks[-2] \
            if track == series.tracks[-1] else \
            series.tracks[series.tracks.index(track) + 1]

        self._track = track
        self._pairTrack = pairTrack

        tPos = track.positionValue
        pPos = pairTrack.positionValue

        # Z and X are swapped here for a 2D projection into a Right-Handed Coordinate system
        if self.isNext:
            self._line = LineSegment2D(tPos, pPos)
            self._vector = Vector2D(pairTrack.z - track.z, pairTrack.x - track.x)
        else:
            self._line = LineSegment2D(pPos, tPos)
            self._vector = Vector2D(track.z - pairTrack.z, track.x - pairTrack.x)

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def line(self):
        return self._line

#_______________________________________________________________________________
    @property
    def angle(self):
        return Vector2D(1.0, 0.0).angleBetween(self.vector)

#_______________________________________________________________________________
    @property
    def isNext(self):
        return self.track.next == self.pairTrack.uid

#_______________________________________________________________________________
    @property
    def vector(self):
        return self._vector

#_______________________________________________________________________________
    @property
    def track(self):
        return self._track

#_______________________________________________________________________________
    @property
    def pairTrack(self):
        return self._pairTrack

#===============================================================================
#                                                                               I N T R I N S I C

#_______________________________________________________________________________
    def __repr__(self):
        return self.__str__()

#_______________________________________________________________________________
    def __str__(self):
        return '<%s>' % self.__class__.__name__

