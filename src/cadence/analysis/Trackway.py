# Trackway.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#*************************************************************************************************** Trackway
from cadence.analysis.TrackSeries import TrackSeries


class Trackway(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, sitemap =None, fingerprint =None):
        """Creates a new instance of Trackway."""
        self._fingerprint   = fingerprint
        self._sitemap       = sitemap
        self._leftPes       = None
        self._rightPes      = None
        self._leftManus     = None
        self._rightManus    = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: sitemap
    @property
    def sitemap(self):
        return self._sitemap

#___________________________________________________________________________________________________ GS: fingerprint
    @property
    def fingerprint(self):
        if self._fingerprint:
            return self._fingerprint
        for series in [self.leftPes, self.rightPes, self.leftManus, self.rightManus]:
            if series and series[0]:
                return series[0].trackwayFingerprint

#___________________________________________________________________________________________________ GS: sitemap
    @property
    def sitemap(self):
        return self._sitemap

#___________________________________________________________________________________________________ GS: leftPes
    @property
    def leftPes(self):
        return self._leftPes
    @leftPes.setter
    def leftPes(self, value):
        self._leftPes = value

#___________________________________________________________________________________________________ GS: rightPes
    @property
    def rightPes(self):
        return self._rightPes
    @rightPes.setter
    def rightPes(self, value):
        self._rightPes = value

#___________________________________________________________________________________________________ GS: leftManus
    @property
    def leftManus(self):
        return self._leftManus
    @leftManus.setter
    def leftManus(self, value):
        self._leftManus = value

#___________________________________________________________________________________________________ GS: rightManus
    @property
    def rightManus(self):
        return self._rightManus
    @rightManus.setter
    def rightManus(self, value):
        self._rightManus = value

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ addSeries
    def addSeries(self, series, allowReplace =True):
        """addSeries doc..."""
        if not isinstance(series, TrackSeries):
            series = TrackSeries(tracks=series, trackway=self)

        attr = '%s%s' % (
            'left' if series.tracks[0].left else 'right',
            'Pes' if series.tracks[0].pes else 'Manus')

        if not allowReplace and getattr(self, attr):
            return False

        setattr(self, attr, series)
        return True

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s "%s" | %s.%s %s.%s>' % (
            self.__class__.__name__,
            self.fingerprint,
            self.leftPes.count if self.leftPes else '-',
            self.rightPes.count if self.leftPes else '-',
            self.leftManus.count if self.leftPes else '-',
            self.rightManus.count if self.leftPes else '-')
