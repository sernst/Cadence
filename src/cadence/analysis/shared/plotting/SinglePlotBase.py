# SinglePlotBase.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from matplotlib.ticker import FuncFormatter

from cadence.analysis.shared.plotting.PlotBase import PlotBase

#*************************************************************************************************** SinglePlotBase
class SinglePlotBase(PlotBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of SinglePlotBase."""
        super(SinglePlotBase, self).__init__()
        self.xLimits = kwargs.get('xLimits')
        self.yLimits = kwargs.get('yLimits')
        self.title   = kwargs.get('title')
        self.xLabel  = kwargs.get('xLabel')
        self.yLabel  = kwargs.get('yLabel')
        self.yTickFunc = kwargs.get('yTickFunc')
        self.xTickFunc = kwargs.get('xTickFunc')

        self._lineMarkers = []

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ create
    def create(self):
        """create doc..."""
        if self._figure:
            return

        super(SinglePlotBase, self).create()
        if not self._lineMarkers:
            return

        for marker in self._lineMarkers:
            self._plotLineMarker(marker['value'], **marker['kwargs'])

        ax = self.pl.gca()
        if self.xTickFunc is not None:
            formatter = FuncFormatter(self.xTickFunc)
            ax.get_xaxis().set_major_formatter(formatter)
        if self.yTickFunc is not None:
            formatter = FuncFormatter(self.yTickFunc)
            ax.get_yaxis().set_major_formatter(formatter)

#___________________________________________________________________________________________________ addLineMarker
    def addLineMarker(self, yValue, vertical =False, **kwargs):
        """addLineMarker doc..."""
        self._lineMarkers.append({'value':yValue, 'vertical':vertical, 'kwargs':kwargs})

#___________________________________________________________________________________________________ setLabels
    def setLabels(self, title =None, xLabel =None, yLabel =None):
        if title:
            self.title = title
        if xLabel:
            self.xLabel = xLabel
        if yLabel:
            self.yLabel = yLabel

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _plotLineMarker
    def _plotLineMarker(self, value, vertical, **kwargs):
        """_plotLineMarker doc..."""

        if vertical:
            self.pl.axvline(x=value, hold=True, **kwargs)
        else:
            self.pl.axhline(y=value, hold=True, **kwargs)
