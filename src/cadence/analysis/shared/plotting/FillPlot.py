# FillPlot.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.ArgsUtils import ArgsUtils

from cadence.analysis.shared.PositionValue2D import PositionValue2D
from cadence.analysis.shared.plotting.SinglePlotBase import SinglePlotBase

#*************************************************************************************************** FillPlot
class FillPlot(SinglePlotBase):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of FillPlot."""
        ArgsUtils.addIfMissing('yLabel', 'Frequency', kwargs)
        super(FillPlot, self).__init__(**kwargs)
        self.color      = kwargs.get('color', 'b')
        self.lineColor  = kwargs.get('lineColor', 'none')
        self.data       = kwargs.get('data', [])
        self.isLog      = kwargs.get('isLog', False)

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
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

#===============================================================================
#                                                                               P R O T E C T E D


#_______________________________________________________________________________
    def _plot(self):
        """_plot doc..."""

        x = []
        y = []

        for value in self.data:
            entry = self._dataItemToValue(value)
            y.append(entry['y'])
            x.append(entry.get('x', len(x)))

        pl = self.pl
        pl.fill(x, y, facecolor=self.color, edgecolor=self.lineColor)
        pl.title(self.title)
        pl.xlabel(self.xLabel)
        pl.ylabel(self.yLabel)
        if self.xLimits:
            pl.xlim(*self.xLimits)
        if self.yLimits:
            pl.ylim(*self.yLimits)
        pl.grid(True)

#_______________________________________________________________________________
    @classmethod
    def _dataItemToValue(cls, value):
        """_dataItemToValue doc..."""
        if isinstance(value, dict):
            return dict(x=value['x'], y=value['y'])

        if isinstance(value, (list, tuple)):
            return dict(x=value[0], y=value[1])

        if isinstance(value, PositionValue2D):
            return dict(x=value.x, y=value.y)

        return dict(y=value, yUnc=0.0)

