# MultiScatterPlot.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.shared.plotting.ScatterPlot import ScatterPlot

#*************************************************************************************************** MultiScatterPlot
class MultiScatterPlot(ScatterPlot):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, *args, **kwargs):
        """Creates a new instance of MultiScatterPlot."""
        super(MultiScatterPlot, self).__init__(**kwargs)
        self._plotData = []

        for item in args:
            self.addPlotSeries(**item)

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def shaveDataToXLimits(self):
        """shaveData doc..."""

        if not self.xLimits or not len(self.xLimits) == 2:
            return self.data

        for entry in self._plotData:
            self._shaveDataToLimits(entry, *self.xLimits)
        return self._plotData

#_______________________________________________________________________________
    def addPlotSeries(self, data, **kwargs):
        """addPlotSeries doc..."""

        kwargs['data'] = data
        self._plotData.append(kwargs)

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _plotImpl(self):
        """_plotImpl doc..."""
        for item in self._plotData:
            self._plotScatterSeries(**item)
