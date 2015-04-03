# CurvatureAnalyzer.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.curvature import DirectionStage
from cadence.analysis.curvature.DirectionStage import DirectionStage
from cadence.analysis.curvature.TrackwayCurveStatsStage import TrackwayCurveStatsStage

from cadence.analysis.curvature.PathGeneratorStage import PathGeneratorStage
from cadence.analysis.curvature.SeriesCurvatureStage import SeriesCurvatureStage
from cadence.analysis.AnalyzerBase import AnalyzerBase

#___________________________________________________________________________________________________ CurvatureAnalyzer
class CurvatureAnalyzer(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of CurvatureAnalyzer."""
        super(CurvatureAnalyzer, self).__init__(**kwargs)
        # self.addStage(SeriesCurvatureStage('seriesCurves', self))
        self.addStage(TrackwayCurveStatsStage('curveStats', self))
        # self.addStage(DirectionStage('direction', self))
        # self.addStage(PathGeneratorStage('pathGenerator', self))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    CurvatureAnalyzer().run()
