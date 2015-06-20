# AnalyzeAll.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.time.TimeUtils import TimeUtils

from cadence.analysis.comparison.ComparisonAnalyzer import ComparisonAnalyzer
from cadence.analysis.curvature.CurvatureAnalyzer import CurvatureAnalyzer
from cadence.analysis.direction.DirectionAnalyzer import DirectionAnalyzer
from cadence.analysis.gauge.GaugeAnalyzer import GaugeAnalyzer
from cadence.analysis.stats.StatisticsAnalyzer import StatisticsAnalyzer
from cadence.analysis.status.StatusAnalyzer import StatusAnalyzer
from cadence.analysis.validation.ValidationAnalyzer import ValidationAnalyzer

#*************************************************************************************************** AnalyzeAll
class AnalyzeAll(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    ANALYZERS = [
        StatusAnalyzer,
        ComparisonAnalyzer,
        CurvatureAnalyzer,
        ValidationAnalyzer,
        DirectionAnalyzer,
        GaugeAnalyzer,
        StatisticsAnalyzer]

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        """Creates a new instance of AnalyzeAll."""
        self.analyzers = []

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ run
    def run(self):
        """run doc..."""

        for AnalyzerClass in self.ANALYZERS:
            a = AnalyzerClass()
            a.run()
            self.analyzers.append([a.elapsedTime, a])

            print('\n\n%s\n%s\n\n' % (80*'#', 80*'#'))

        print('%s\nANALYSIS COMPLETE:' % (80*'-'))
        for a in self.analyzers:
            print('  [%s]: %s (%s)' % (
                'SUCCESS' if a[-1].success else 'FAILED',
                TimeUtils.toPrettyElapsedTime(a[0]),
                a[-1].__class__.__name__))

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    r = AnalyzeAll()
    r.run()
