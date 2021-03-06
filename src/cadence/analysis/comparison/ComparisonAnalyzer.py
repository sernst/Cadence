# ComparisonAnalyzer.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.comparison.DrawLengthWidthStage import DrawLengthWidthStage
from cadence.analysis.comparison.RotationStage import RotationStage
from cadence.analysis.comparison.LengthWidthStage import LengthWidthStage
from cadence.analysis.AnalyzerBase import AnalyzerBase

#_______________________________________________________________________________
class ComparisonAnalyzer(AnalyzerBase):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of ComparisonAnalyzer. Stages are added as needed. """
        super(ComparisonAnalyzer, self).__init__(**kwargs)
        self.addStage(LengthWidthStage('lengthWidth', self))
        self.addStage(DrawLengthWidthStage('drawLengthWidth', self))
        self.addStage(RotationStage('rotation', self))

####################################################################################################
####################################################################################################

#_______________________________________________________________________________
if __name__ == '__main__':
    ComparisonAnalyzer().run()
