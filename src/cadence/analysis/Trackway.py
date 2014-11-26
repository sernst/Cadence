# Trackway.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.config.ConfigsDict import ConfigsDict

from cadence.analysis.TrackSeries import TrackSeries

#*************************************************************************************************** Trackway
class Trackway(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, sitemap =None, fingerprint =None):
        """Creates a new instance of Trackway."""
        self._fingerprint   = fingerprint
        self._sitemap       = sitemap
        self._leftPes       = TrackSeries(sitemap=sitemap, trackway=self)
        self._rightPes      = TrackSeries(sitemap=sitemap, trackway=self)
        self._leftManus     = TrackSeries(sitemap=sitemap, trackway=self)
        self._rightManus    = TrackSeries(sitemap=sitemap, trackway=self)
        self._cache         = ConfigsDict()

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: isReady
    @property
    def isReady(self):
        """ Specifies whether or not this track series is ready for analysis """
        for s in self.seriesList:
            if not s.isReady:
                return False
        return True

#___________________________________________________________________________________________________ GS: isValid
    @property
    def isValid(self):
        for s in self.seriesList:
            if not s.isValid:
                return False
        return True

#___________________________________________________________________________________________________ GS: isComplete
    @property
    def isComplete(self):
        for s in self.seriesList:
            if not s.isComplete:
                return False
        return True

#___________________________________________________________________________________________________ GS: cache
    @property
    def cache(self):
        return self._cache

#___________________________________________________________________________________________________ GS: seriesList
    @property
    def seriesList(self):
        return [self.leftPes, self.rightPes, self.leftManus, self.rightManus]

#___________________________________________________________________________________________________ GS: count
    @property
    def count(self):
        count = 0
        for series in self.seriesList:
            if series:
                count += series.count
        return count

#___________________________________________________________________________________________________ GS: totalCount
    @property
    def totalCount(self):
        count = 0
        for series in self.seriesList:
            if series:
                count += series.totalCount
        return count

#___________________________________________________________________________________________________ GS: hiddenCount
    @property
    def hiddenCount(self):
        count = 0
        for series in self.seriesList:
            if series:
                count += len(series.hiddenTracks)
        return count

#___________________________________________________________________________________________________ GS: incompleteCount
    @property
    def incompleteCount(self):
        count = 0
        for series in self.seriesList:
            if series:
                count += len(series.incompleteTracks)
        return count

#___________________________________________________________________________________________________ GS: sitemap
    @property
    def sitemap(self):
        return self._sitemap

#___________________________________________________________________________________________________ GS: fingerprint
    @property
    def fingerprint(self):
        if self._fingerprint:
            return self._fingerprint
        for series in self.seriesList:
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

#___________________________________________________________________________________________________ addTrack
    def addTrack(self, track):
        """addTrack doc..."""
        if track.left and track.pes:
            self.leftPes.addTrack(track)
        elif track.left:
            self.leftManus.addTrack(track)
        elif track.pes:
            self.rightPes.addTrack(track)
        else:
            self.rightManus.addTrack(track)

#___________________________________________________________________________________________________ sortAll
    def sortAll(self):
        """sortAll doc..."""
        for series in self.seriesList:
            series.sort()

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
            self.leftPes.count if self.leftPes else '*',
            self.rightPes.count if self.rightPes else '*',
            self.leftManus.count if self.leftManus else '*',
            self.rightManus.count if self.rightManus else '*')
