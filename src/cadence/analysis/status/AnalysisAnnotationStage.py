# AnalysisAnnotationStage.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

from cadence.analysis.AnalysisStage import AnalysisStage

#*******************************************************************************
class AnalysisAnnotationStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                   C L A S S

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of OriginCheckStage."""
        super(AnalysisAnnotationStage, self).__init__(
            key, owner,
            label='Analysis Annotation',
            **kwargs)

#===============================================================================
#                                                           P R O T E C T E D

#_______________________________________________________________________________
    def _analyzeTrack(self, track, series, trackway, sitemap):
        analysisTrack = track.getAnalysisPair(self.analysisSession)
        analysisTrack.trackwayIndex = trackway.index
        analysisTrack.trackwayName = trackway.name

