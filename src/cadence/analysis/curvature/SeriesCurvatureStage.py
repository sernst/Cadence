# SeriesCurvatureStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.AnalysisStage import AnalysisStage

from cadence.analysis.shared.PositionValue2D import PositionValue2D

#*************************************************************************************************** SeriesCurvatureStage
class SeriesCurvatureStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of SeriesCurvatureStage."""
        super(SeriesCurvatureStage, self).__init__(
            key, owner,
            label='Series Processing',
            **kwargs)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        points = []
        for track in series.tracks:
            p = PositionValue2D()
            p.xFromUncertaintyValue(track.zValue)
            p.yFromUncertaintyValue(track.xValue)
            points.append(p)

        for i in range(5):
            xs = []
            ys = []

            for point in points:
                if i == 0:
                    p = (point.x, point.y)
                elif i == 1:
                    p = (point.x + point.xUnc, point.y + point.yUnc)
                elif i == 2:
                    p = (point.x + point.xUnc, point.y - point.yUnc)
                elif i == 3:
                    p = (point.x - point.xUnc, point.y - point.yUnc)
                else:
                    p = (point.x - point.xUnc, point.y + point.yUnc)

                xs.append(p[0])
                ys.append(p[1])






#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        pass

