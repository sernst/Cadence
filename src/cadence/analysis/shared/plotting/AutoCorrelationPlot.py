# AutoCorrelationPlot.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import numpy as np
import pandas as pd
from pandas.tools import plotting as pdPlot

from cadence.analysis.shared.plotting.SinglePlotBase import SinglePlotBase


#*************************************************************************************************** AutoCorrelationPlot
class AutoCorrelationPlot(SinglePlotBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of AutoCorrelationPlot."""
        super(AutoCorrelationPlot, self).__init__(**kwargs)
        self.lineColor  = kwargs.get('lineColor', 'none')
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


#___________________________________________________________________________________________________ _plot
    def _plot(self):
        """_plot doc..."""

        data = pd.Series(np.asarray(self.data))

        pl = self.pl
        ax = pl.gca()
        pdPlot.autocorrelation_plot(data, ax=ax)
        pl.title(self.title)
        pl.xlabel(self.xLabel)
        pl.ylabel(self.yLabel)
        if self.xLimits:
            pl.xlim(*self.xLimits)
        if self.yLimits:
            pl.ylim(*self.yLimits)
        pl.grid(True)
