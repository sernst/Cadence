# SinglePlotBase.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division


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

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ setLabels
    def setLabels(self, title =None, xLabel =None, yLabel =None):
        if title:
            self.title = title
        if xLabel:
            self.xLabel = xLabel
        if yLabel:
            self.yLabel = yLabel
