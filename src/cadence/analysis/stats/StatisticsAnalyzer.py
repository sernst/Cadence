# StatisticsAnalyzer.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.stats.TrackwayStatsStage import TrackwayStatsStage
from cadence.analysis.AnalyzerBase import AnalyzerBase

#___________________________________________________________________________________________________ StatisticsAnalyzer
class StatisticsAnalyzer(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of StatisticsAnalyzer."""
        super(StatisticsAnalyzer, self).__init__(**kwargs)
        self.addStage(TrackwayStatsStage('trackwayStats', self))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    StatisticsAnalyzer().run()


