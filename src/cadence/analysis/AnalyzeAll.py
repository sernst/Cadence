# AnalyzeAll.py
# (C)2015
# Scott Ernst

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyaid.time.TimeUtils import TimeUtils

from cadence.analysis.comparison.ComparisonAnalyzer import ComparisonAnalyzer
from cadence.analysis.curvature.CurvatureAnalyzer import CurvatureAnalyzer
from cadence.analysis.direction.DirectionAnalyzer import DirectionAnalyzer
from cadence.analysis.gauge.GaugeAnalyzer import GaugeAnalyzer
from cadence.analysis.stats.StatisticsAnalyzer import StatisticsAnalyzer
from cadence.analysis.status.StatusAnalyzer import StatusAnalyzer
from cadence.analysis.validation.ValidationAnalyzer import ValidationAnalyzer

class AnalyzeAll(object):
    """A class for..."""

    ANALYZERS = [
        StatusAnalyzer,
        ComparisonAnalyzer,
        CurvatureAnalyzer,
        ValidationAnalyzer,
        DirectionAnalyzer,
        GaugeAnalyzer,
        StatisticsAnalyzer
    ]

    def __init__(self):
        """Creates a new instance of AnalyzeAll."""
        self.analyzers = []

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

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '<%s>' % self.__class__.__name__

################################################################################
################################################################################

if __name__ == '__main__':
    r = AnalyzeAll()
    r.run()
