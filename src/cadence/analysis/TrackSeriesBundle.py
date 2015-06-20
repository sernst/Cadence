# TrackSeriesBundle.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from collections import OrderedDict
from pyaid.string.StringUtils import StringUtils

from cadence.analysis.TrackSeries import TrackSeries

#*************************************************************************************************** TrackSeriesBundle
class TrackSeriesBundle(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, trackway):
        """Creates a new instance of TrackSeriesBundle."""
        self._trackway = trackway

        tw = trackway
        self._leftPes = TrackSeries(
            tw, bundle=self, firstTrackUid=tw.firstLeftPes, left=True, pes=True)
        self._rightPes = TrackSeries(
            tw, bundle=self, firstTrackUid=tw.firstRightPes, pes=True, )
        self._leftManus = TrackSeries(
            tw, bundle=self, firstTrackUid=tw.firstLeftManus, left=True)
        self._rightManus = TrackSeries(
            tw, bundle=self, firstTrackUid=tw.firstRightManus)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: count
    @property
    def count(self):
        """ The number of tracks in the trackway """
        out = 0
        for series in self.asList():
            out += series.count
        return out

#___________________________________________________________________________________________________ GS: trackway
    @property
    def trackway(self):
        return self._trackway

#___________________________________________________________________________________________________ GS: leftPes
    @property
    def leftPes(self):
        return self._leftPes

#___________________________________________________________________________________________________ GS: rightPes
    @property
    def rightPes(self):
        return self._rightPes

#___________________________________________________________________________________________________ GS: leftManus
    @property
    def leftManus(self):
        return self._leftManus

#___________________________________________________________________________________________________ GS: rightManus
    @property
    def rightManus(self):
        return self._rightManus

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getOpposingSeries
    def getOpposingSeries(self, series):
        """getOpposingSeries doc..."""
        if series == self.leftPes:
            return self.rightPes
        elif series == self.rightPes:
            return self.leftPes
        elif series == self.leftManus:
            return self.rightManus
        elif series == self.rightManus:
            return self.leftManus

        print('SERIES:', series)
        raise ValueError('Specified series "%s" not part of this bundle' % series)

#___________________________________________________________________________________________________ echoStatus
    def echoStatus(self, asPercent =False):
        if not self._leftPes:
            return '(NOT-LOADED)'

        seriesList = self.asList()
        zFill = StringUtils.zeroFill
        out = [float(s.count if s.isReady else 0) for s in seriesList]

        if asPercent:
            out = [math.ceil(100.0*item/max(out)) for item in out]
            out = ['%s%%' % int(item) for item in out]
        else:
            out = [zFill(item, 3) if item > 0 else '---' for item in out]

        return 'P:(%s, %s) M:(%s, %s)' % tuple(out)

#___________________________________________________________________________________________________ echoStartUids
    def echoStartUids(self):
        """echoStarts doc..."""
        if not self._leftPes:
            return '(NOT-LOADED)'

        return 'P:("%s" | "%s") M:("%s" | "%s")'  % (
            self._leftPes.firstTrackUid if self._leftPes.firstTrackUid else '---',
            self._rightPes.firstTrackUid if self._rightPes.firstTrackUid else '---',
            self._leftManus.firstTrackUid if self._leftManus.firstTrackUid else '---',
            self._rightManus.firstTrackUid if self._rightManus.firstTrackUid else '---')

#___________________________________________________________________________________________________ asList
    def asList(self):
        return [self._leftPes, self._rightPes, self._leftManus, self._rightManus]

#___________________________________________________________________________________________________ asDict
    def asDict(self):
        out = OrderedDict()
        for item in self.asList():
            item.load()
            out[item.key] = item
        return out

#___________________________________________________________________________________________________ items
    def items(self):
        out = []
        for item in self.asList():
            out.append((item.key, item))
        return out

#___________________________________________________________________________________________________ load
    def load(self):
        """load doc..."""

        for series in self.asList():
            series.load()

        return True

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __len__
    def __len__(self):
        """__len__ doc..."""
        return 4

#___________________________________________________________________________________________________ __iter__
    def __iter__(self):
        """__iter__ doc..."""
        return self.asList()

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

