# Trackway.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.config.ConfigsDict import ConfigsDict

from cadence.analysis.TrackSeries import TrackSeries

#*************************************************************************************************** Trackway
class Trackway(object):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, sitemap, trackway):
        """Creates a new instance of Trackway."""
        self._sitemap       = sitemap
        self._trackway      = trackway
        self._leftPes       = TrackSeries(self)
        self._rightPes      = TrackSeries(self)
        self._leftManus     = TrackSeries(self)
        self._rightManus    = TrackSeries(self)
        self._cache         = ConfigsDict()

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def trackway(self):
        return self._trackway

#_______________________________________________________________________________
    @property
    def isReady(self):
        """ Specifies whether or not this track series is ready for analysis """
        for s in self.seriesList:
            if not s.isReady:
                return False
        return True

#_______________________________________________________________________________
    @property
    def isValid(self):
        for s in self.seriesList:
            if not s.isValid:
                return False
        return True

#_______________________________________________________________________________
    @property
    def isComplete(self):
        for s in self.seriesList:
            if not s.isComplete:
                return False
        return True

#_______________________________________________________________________________
    @property
    def cache(self):
        return self._cache

#_______________________________________________________________________________
    @property
    def seriesList(self):
        return [self.leftPes, self.rightPes, self.leftManus, self.rightManus]

#_______________________________________________________________________________
    @property
    def count(self):
        count = 0
        for series in self.seriesList:
            if series:
                count += series.count
        return count

#_______________________________________________________________________________
    @property
    def totalCount(self):
        count = 0
        for series in self.seriesList:
            if series:
                count += series.totalCount
        return count

#_______________________________________________________________________________
    @property
    def hiddenCount(self):
        count = 0
        for series in self.seriesList:
            if series:
                count += len(series.hiddenTracks)
        return count

#_______________________________________________________________________________
    @property
    def incompleteCount(self):
        count = 0
        for series in self.seriesList:
            if series:
                count += len(series.incompleteTracks)
        return count

#_______________________________________________________________________________
    @property
    def sitemap(self):
        return self._sitemap

#_______________________________________________________________________________
    @property
    def fingerprint(self):
        if self._fingerprint:
            return self._fingerprint
        for series in self.seriesList:
            if series and series[0]:
                return series[0].trackwayFingerprint

#_______________________________________________________________________________
    @property
    def sitemap(self):
        return self._sitemap

#_______________________________________________________________________________
    @property
    def leftPes(self):
        return self._leftPes
    @leftPes.setter
    def leftPes(self, value):
        self._leftPes = value

#_______________________________________________________________________________
    @property
    def rightPes(self):
        return self._rightPes
    @rightPes.setter
    def rightPes(self, value):
        self._rightPes = value

#_______________________________________________________________________________
    @property
    def leftManus(self):
        return self._leftManus
    @leftManus.setter
    def leftManus(self, value):
        self._leftManus = value

#_______________________________________________________________________________
    @property
    def rightManus(self):
        return self._rightManus
    @rightManus.setter
    def rightManus(self, value):
        self._rightManus = value

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
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

#_______________________________________________________________________________
    def sortAll(self):
        """sortAll doc..."""
        for series in self.seriesList:
            series.sort()

#===============================================================================
#                                                                               I N T R I N S I C

#_______________________________________________________________________________
    def __repr__(self):
        return self.__str__()

#_______________________________________________________________________________
    def __str__(self):
        return '<%s "%s" | %s.%s %s.%s>' % (
            self.__class__.__name__,
            self.fingerprint,
            self.leftPes.count if self.leftPes else '*',
            self.rightPes.count if self.rightPes else '*',
            self.leftManus.count if self.leftManus else '*',
            self.rightManus.count if self.rightManus else '*')
