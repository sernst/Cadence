# MultiScatterPlot.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

from cadence.analysis.shared.plotting.ScatterPlot import ScatterPlot

#*******************************************************************************
class MultiScatterPlot(ScatterPlot):
    """A class for..."""

#===============================================================================
#                                                                     C L A S S

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
        plotHandles = []
        for item in self._plotData:
            if 'label' not in item:
                item['label'] = 'Series %s' % (len(plotHandles) + 1)
            plotHandles.append(self._plotScatterSeries(**item))

        if len(plotHandles) < 2:
            return

        handles = []
        for ph in plotHandles:
            handles.append(ph[-1])
            self.pl.legend(handles)
