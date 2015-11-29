# StatisticsAnalyzer.py
# (C)2015
# Scott Ernst

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.stats.LocalRotationsStage import LocalRotationsStage
from cadence.analysis.stats.TrackPriorityStage import TrackPriorityStage
from cadence.analysis.stats.TrackwayStatsStage import TrackwayStatsStage
from cadence.analysis.AnalyzerBase import AnalyzerBase

class StatisticsAnalyzer(AnalyzerBase):
    """A class for..."""


    #___________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of StatisticsAnalyzer."""
        super(StatisticsAnalyzer, self).__init__(**kwargs)
        self.addStage(LocalRotationsStage('localRotations', self))
        self.addStage(TrackPriorityStage('priority', self))
        self.addStage(TrackwayStatsStage('trackwayStats', self))
        #self.addStage(KMeansClusterStage('kmeans', self))

####################################################################################################
####################################################################################################

#_______________________________________________________________________________
if __name__ == '__main__':
    StatisticsAnalyzer().run()


