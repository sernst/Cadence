# MultiScatterPlot.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.shared.plotting.ScatterPlot import ScatterPlot

#*************************************************************************************************** MultiScatterPlot
class MultiScatterPlot(ScatterPlot):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, *args, **kwargs):
        """Creates a new instance of MultiScatterPlot."""
        super(MultiScatterPlot, self).__init__(**kwargs)
        self._plotData = []

        for item in args:
            self.addPlotSeries(**item)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ shaveDataToXLimits
    def shaveDataToXLimits(self):
        """shaveData doc..."""

        if not self.xLimits or not len(self.xLimits) == 2:
            return self.data

        for entry in self._plotData:
            self._shaveDataToLimits(entry, *self.xLimits)
        return self._plotData

#___________________________________________________________________________________________________ addPlotSeries
    def addPlotSeries(self, data, **kwargs):
        """addPlotSeries doc..."""

        self._plotData.append(dict(
            color=kwargs.get('color', 'blue'),
            format=kwargs.get('format', 'o'),
            data=data))

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _plotImpl
    def _plotImpl(self):
        """_plotImpl doc..."""
        for item in self._plotData:
            self._plotScatterSeries(item['data'], item['format'], item['color'])
