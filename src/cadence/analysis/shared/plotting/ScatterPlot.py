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
        self.size       = kwargs.get('size', 6)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ shaveDataToXLimits
    def shaveDataToXLimits(self):
        """shaveData doc..."""

        if not self.xLimits or not len(self.xLimits) == 2:
            return self.data

        self.data = self._shaveDataToLimits(self.data, *self.xLimits)
        return self.data

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _plot
    def _plot(self):
        """_plot doc..."""
        pl = self.pl
        self._plotImpl()
        pl.title(self.title)
        pl.xlabel(self.xLabel)
        pl.ylabel(self.yLabel)
        if self.xLimits:
            pl.xlim(*self.xLimits)
        if self.yLimits:
            pl.ylim(*self.yLimits)
        pl.grid(True)

#___________________________________________________________________________________________________ _plotImpl
    def _plotImpl(self):
        """_plotImpl doc..."""
        self._plotScatterSeries(data=self.data, format=self.format, color=self.color)

#___________________________________________________________________________________________________ _plotScatterSeries
    def _plotScatterSeries(self, data, **kwargs):
        """_plotScatterSeries doc..."""
        x = []
        y = []
        xUnc = []
        yUnc = []

        color = kwargs.get('color', 'black')

        for value in data:
            item = self._dataItemToValue(value)
            x.append(item['x'])
            y.append(item['y'])
            xUnc.append(item['xUnc'])
            yUnc.append(item['yUnc'])
        self.pl.errorbar(
            x=x, y=y, xerr=xUnc, yerr=yUnc,
            fmt=kwargs.get('format', 'o'), markersize=kwargs.get('size', 6), color=color)

        if kwargs.get('line'):
            self.pl.plot(x, y, '-', color=color)

#___________________________________________________________________________________________________ _shaveDataToLimits
    @classmethod
    def _shaveDataToLimits(cls, data, xMin, xMax):
        """_shaveDataToLimits doc..."""
        out  = []
        for value in data:
            item = cls._dataItemToValue(value)
            if xMin <= item[0] <= xMax:
                out.append(value)
        return out

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
