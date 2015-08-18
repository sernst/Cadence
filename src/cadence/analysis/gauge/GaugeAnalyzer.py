# GaugeAnalyzer.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.gauge.SimpleGaugeStage import SimpleGaugeStage
from cadence.analysis.AnalyzerBase import AnalyzerBase

#_______________________________________________________________________________
class GaugeAnalyzer(AnalyzerBase):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of GaugeAnalyzer."""
        super(GaugeAnalyzer, self).__init__(**kwargs)
        self.addStage(SimpleGaugeStage('simpleGauge', self))

####################################################################################################
####################################################################################################

#_______________________________________________________________________________
if __name__ == '__main__':
    GaugeAnalyzer().run()

