# CurvatureAnalyzer.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.curvature.CurveProjectionStage import CurveProjectionStage
from cadence.analysis.curvature.CurveSparsenessStage import CurveSparsenessStage

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
        self.addStage(CurveSparsenessStage('sparseness', self))
        self.addStage(CurveProjectionStage('project', self))
        # self.addStage(DirectionStage('direction', self))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    CurvatureAnalyzer().run()
