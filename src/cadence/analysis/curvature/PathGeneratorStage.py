# PathGeneratorStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.AnalysisStage import AnalysisStage

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
            label='Path Generation',
            **kwargs)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackway(self, trackway, sitemap):
        self._minStrideLength = 1.0e8
        self._points = []
        super(PathGeneratorStage, self)._analyzeTrackway(trackway, sitemap)

        points = []
        for p in self._points:
            points.append([p[0].value, p[1].value])

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        """_analyzeTrackSeries doc..."""
        super(PathGeneratorStage, self)._analyzeTrackSeries(series, trackway, sitemap)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        x = track.zValue
        y = track.xValue
        self._points.append((x, y))

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        self.mergePdfs(self._paths, self.getPath('Voronois.pdf'))
