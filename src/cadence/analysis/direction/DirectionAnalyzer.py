# DirectionAnalyzer.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.AnalyzerBase import AnalyzerBase
from cadence.analysis.direction.DirectionStage import DirectionStage

#___________________________________________________________________________________________________ DirectionAnalyzer
class DirectionAnalyzer(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of DirectionAnalyzer."""
        super(DirectionAnalyzer, self).__init__(**kwargs)
        self.addStage(DirectionStage('direction', self))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    DirectionAnalyzer().run()
