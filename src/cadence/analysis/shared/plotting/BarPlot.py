# BarPlot.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.ArgsUtils import ArgsUtils
from pyaid.number.NumericUtils import NumericUtils
from cadence.analysis.shared.PositionValue2D import PositionValue2D

from cadence.analysis.shared.plotting.SinglePlotBase import SinglePlotBase

#*************************************************************************************************** BarPlot
class BarPlot(SinglePlotBase):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of BarPlot."""
        ArgsUtils.addIfMissing('yLabel', 'Frequency', kwargs)
        super(BarPlot, self).__init__(**kwargs)
        self.color      = kwargs.get('color', 'b')
        self.strokeColor = kwargs.get('strokeColor', 'none')
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
        yUnc = []

        for value in self.data:
            entry = self._dataItemToValue(value)
            y.append(entry['y'])
            x.append(entry.get('x', len(x)))
            yUnc.append(entry.get('yUnc', 0.0))

        if NumericUtils.equivalent(max(yUnc), 0.0):
            yUnc = None

        pl = self.pl
        pl.bar(x, y, yerr=yUnc, facecolor=self.color, edgecolor=self.strokeColor, log=self.isLog)
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
            return dict(x=value['x'], y=value['y'], yUnc=value.get('yUnc', 0.0) )

        if isinstance(value, (list, tuple)):
            return dict(x=value[0], y=value[1], yUnc=0.0 if len(value) < 3 else value[2])

        if isinstance(value, PositionValue2D):
            return value.toDict()

        return dict(y=value, yUnc=0.0)
