# ScatterPlot.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from cadence.analysis.shared.PositionValue2D import PositionValue2D

from cadence.analysis.shared.plotting.SinglePlotBase import SinglePlotBase

#*************************************************************************************************** ScatterPlot
class ScatterPlot(SinglePlotBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of ScatterPlot."""
        super(ScatterPlot, self).__init__(**kwargs)
        self.color      = kwargs.get('color', 'b')
        self.format     = kwargs.get('format', 'o')
        self.data       = kwargs.get('data', [])

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ shaveDataToXLimits
    def shaveDataToXLimits(self):
        """shaveData doc..."""

        if not self.xLimits or not len(self.xLimits) == 2:
            return self.data

        out  = []
        for item in self.data:
            if self.xLimits[0] <= item <= self.xLimits[1]:
                out.append(item)
        self.data = out
        return out

#===================================================================================================
#                                                                               P R O T E C T E D


#___________________________________________________________________________________________________ _dataItemToValue
    @classmethod
    def _dataItemToValue(cls, value):
        """_dataItemToValue doc..."""
        if isinstance(value, dict):
            return dict(
                x=value['x'], y=value['y'],
                xUnc=value.get('xUnc', 0.0), yUnc=value.get('yUnc', 0.0) )

        if isinstance(value, (list, tuple)):
            return dict(
                x=value[0], y=value[1],
                xUnc=0.0 if len(value) < 4 else value[2],
                yUnc=0.0 if len(value) < 3 else (value[2] if len(value) < 4 else value[3]))

        if isinstance(value, PositionValue2D):
            return value.toDict()

#___________________________________________________________________________________________________ _plot
    def _plot(self):
        """_plot doc..."""

        x = []
        y = []
        xUnc = []
        yUnc = []

        for value in self.data:
            item = self._dataItemToValue(value)
            x.append(item['x'])
            y.append(item['y'])
            xUnc.append(item['xUnc'])
            yUnc.append(item['yUnc'])

        pl = self.pl
        pl.errorbar(x, y, xerr=xUnc, yerr=yUnc, fmt=self.format, color=self.color)
        pl.title(self.title)
        pl.xlabel(self.xLabel)
        pl.ylabel(self.yLabel)
        if self.xLimits:
            pl.xlim(*self.xLimits)
        if self.yLimits:
            pl.ylim(*self.yLimits)
        pl.grid(True)

