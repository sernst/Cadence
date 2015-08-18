# ValidationAnalyzer.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.validation.PaceLengthStage import PaceLengthStage
from cadence.analysis.validation.TrackwayPlotPaceStage import TrackwayPlotPaceStage
from cadence.analysis.validation.TrackwayPlotStrideStage import TrackwayPlotStrideStage
from cadence.analysis.validation.StrideLengthStage import StrideLengthStage
from cadence.analysis.AnalyzerBase import AnalyzerBase

#_______________________________________________________________________________
class ValidationAnalyzer(AnalyzerBase):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of ValidationAnalyzer."""
        super(ValidationAnalyzer, self).__init__(**kwargs)
        self.addStage(StrideLengthStage('strideLength', self))
        self.addStage(TrackwayPlotStrideStage('stridePlots', self))
        self.addStage(PaceLengthStage('paceLength', self))
        self.addStage(TrackwayPlotPaceStage('pacePlots', self))

####################################################################################################
####################################################################################################

#_______________________________________________________________________________
if __name__ == '__main__':
    ValidationAnalyzer().run()

