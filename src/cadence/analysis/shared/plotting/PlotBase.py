# PlotBase.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

#*************************************************************************************************** PlotBase
class PlotBase(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        """Creates a new instance of PlotBase."""
        self._figure       = None
        self._figureIndex  = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: pl
    @property
    def pl(self):
        return plt

#___________________________________________________________________________________________________ GS: figureIndex
    @property
    def figureIndex(self):
        return self._figureIndex

#___________________________________________________________________________________________________ GS: figure
    @property
    def figure(self):
        return self._figure

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ create
    def create(self):
        """create doc..."""
        if self._figure:
            return

        self._createFigure()
        self._plot()

#___________________________________________________________________________________________________ close
    def close(self):
        """closeFigure doc..."""
        if not self._figure:
            return

        plt.close(self._figure)
        self._figure = None

#___________________________________________________________________________________________________ save
    def save(self, path, close =True, **kwargs):
        """savePlotFile doc..."""
        if not self._figure:
            self.create()

        if 'orientation' not in kwargs:
            kwargs['orientation'] = 'landscape'

        self._figure.savefig(path, **kwargs)
        if close:
            self.close()
        return path

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _createFigure
    def _createFigure(self, subplotX =1, subPlotY =1, **kwargs):
        """createFigure doc..."""
        result = plt.subplots(subplotX, subPlotY, **kwargs)
        self._figure = plt.gcf()
        self._figureIndex = result[0]

#___________________________________________________________________________________________________ _plot
    def _plot(self):
        """_plot doc..."""
        pass

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__


