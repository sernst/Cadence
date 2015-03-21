# PathGeneratorStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.StrideLine import StrideLine
from cadence.util.math2D.Vector2D import Vector2D

#*************************************************************************************************** PathGeneratorStage
class PathGeneratorStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of PathGeneratorStage."""
        super(PathGeneratorStage, self).__init__(
            key, owner,
            label='Track Direction',
            **kwargs)
        self._paths  = []

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackway(self, trackway, sitemap):
        super(PathGeneratorStage, self)._analyzeTrackway(trackway, sitemap)

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        """_analyzeTrackSeries doc..."""

        absoluteAxis = Vector2D(1, 0)
        absoluteAxis.normalize()

        angles = []
        for track in series.tracks:
            strideLine = StrideLine(track, series)
            angles.append(strideLine.angle.degrees)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        pass

