# ExporterAnalyzer.py
# (C)2015
# Scott Ernst

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from cadence.analysis.AnalyzerBase import AnalyzerBase
from cadence.analysis.exporter.SimulationCsvExporterStage import \
    SimulationCsvExporterStage


class ExporterAnalyzer(AnalyzerBase):
    """A class for..."""

    def __init__(self, **kwargs):
        """Creates a new instance of ExporterAnalyzer."""
        super(ExporterAnalyzer, self).__init__(**kwargs)
        self.addStage(SimulationCsvExporterStage('simulation_csv', self))

################################################################################
################################################################################

if __name__ == '__main__':
    ExporterAnalyzer().run()



