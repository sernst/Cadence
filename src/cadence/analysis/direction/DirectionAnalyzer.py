# DirectionAnalyzer.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.direction.TrackwayDeflectionStage import TrackwayDeflectionStage
from cadence.analysis.direction.TrackwayDirectionStage import TrackwayDirectionStage
from cadence.analysis.AnalyzerBase import AnalyzerBase
from cadence.analysis.direction.TrackHeadingStage import TrackHeadingStage

#_______________________________________________________________________________
class DirectionAnalyzer(AnalyzerBase):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of DirectionAnalyzer."""
        super(DirectionAnalyzer, self).__init__(**kwargs)
        self.addStage(TrackHeadingStage('heading', self))
        self.addStage(TrackwayDirectionStage('direction', self))
        self.addStage(TrackwayDeflectionStage('deflection', self))

####################################################################################################
####################################################################################################

#_______________________________________________________________________________
if __name__ == '__main__':
    DirectionAnalyzer().run()
