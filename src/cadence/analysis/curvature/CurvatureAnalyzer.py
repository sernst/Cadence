# CurvatureAnalyzer.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.AnalyzerBase import AnalyzerBase
from cadence.analysis.curvature.CurveCorrelationStage import CurveCorrelationStage
from cadence.analysis.curvature.CurveProjectionLinkStage import CurveProjectionLinkStage
from cadence.analysis.curvature.CurveProjectionStage import CurveProjectionStage
from cadence.analysis.curvature.CurveSparsenessStage import CurveSparsenessStage

#_______________________________________________________________________________
class CurvatureAnalyzer(AnalyzerBase):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of CurvatureAnalyzer."""
        super(CurvatureAnalyzer, self).__init__(**kwargs)
        self.addStage(CurveSparsenessStage('sparseness', self))
        self.addStage(CurveProjectionStage('projection', self))
        self.addStage(CurveProjectionLinkStage('projection-linking', self))
        self.addStage(CurveCorrelationStage('correlation', self))

####################################################################################################
####################################################################################################

#_______________________________________________________________________________
if __name__ == '__main__':
    CurvatureAnalyzer().run()
