# TrackwayPlotStrideStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re

from pyaid.color.ColorValue import ColorValue

from cadence.analysis.AnalysisStage import AnalysisStage



#*************************************************************************************************** TrackwayPlotStrideStage
class TrackwayPlotStrideStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayPlotStrideStage."""
        super(TrackwayPlotStrideStage, self).__init__(
            key, owner,
            label='Stride Length Plotting',
            **kwargs)
        self._paths = []

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        pl = self.plot

        self.owner.createFigure(trackway.uid)
        pl.xlabel('Track Index')
        pl.ylabel('Stride Length (m)')
        pl.title(trackway.name)
        pl.grid(True)

        super(TrackwayPlotStrideStage, self)._analyzeTrackway(trackway, sitemap)

        if trackway.cache.get('doStridePlot', False):
            self._paths.append(self.owner.saveFigure(trackway.uid))
        self.owner.closeFigure(trackway.uid)

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        """_analyzeTrackSeries doc..."""

        if not series.tracks:
            return

        pl    = self.plot
        x     = []
        y     = []
        error = []
        lw    = []

        self.owner.getFigure(trackway.uid)
        for track in series.tracks:
            entry = track.cache.get('strideData')
            if not entry:
                continue

            try:
                xv = int(track.number)
            except Exception:
                xv = int(re.sub(r'[^0-9]+', '', track.number))

            x.append(xv)
            y.append(entry['entered'].value)
            error.append(entry['entered'].uncertainty)
            lw.append(2.0)

        if len(x) < 2:
            return

        trackway.cache.set('doStridePlot', True)

        if series.left and series.pes:
            color = ColorValue('blue')
        elif series.pes:
            color = ColorValue('sky blue')
        elif series.left:
            color = ColorValue('green')
        else:
            color = ColorValue('light green')

        pl.errorbar(x, y, yerr=error, fmt='o', color=color.web)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        self.mergePdfs(self._paths)
