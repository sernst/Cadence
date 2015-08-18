# CurveOrderedAnalysisStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.AnalysisStage import AnalysisStage

#*************************************************************************************************** CurveOrderedAnalysisStage
class CurveOrderedAnalysisStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, key, owner, label =None, **kwargs):
        """Creates a new instance of CurveOrderedAnalysisStage."""
        super(CurveOrderedAnalysisStage, self).__init__(key, owner, label, **kwargs)

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _analyzeTrackway(self, trackway, sitemap):
        """_analyzeTrackway doc..."""

        bundle = self.owner.getSeriesBundle(trackway)
        track = self._getNextTrack(bundle)

        while track is not None:
            self._analyzeTrack(track, track.trackSeries, trackway, sitemap)
            track = self._getNextTrack(bundle, track)

        super(CurveOrderedAnalysisStage, self)._analyzeTrackway(trackway, sitemap)

#_______________________________________________________________________________
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        """ _analyzeTrackSeries """
        pass

#_______________________________________________________________________________
    def _getNextTrack(self, bundle, lastTrack =None):
        """_getNextTrack doc..."""

        if lastTrack:
            lastAnalysisTrack = lastTrack.getAnalysisPair(self.analysisSession)
            index = lastAnalysisTrack.curveIndex + 1
        else:
            index = 0

        for series in bundle.asList():
            for track in series.tracks:
                at = track.getAnalysisPair(self.analysisSession)
                if at.curveIndex == index:
                    return track
                if at.curveIndex > index:
                    break

        return None
