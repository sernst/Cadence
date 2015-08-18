# TrackwayPlotPaceStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.color.ColorValue import ColorValue

from cadence.analysis.AnalysisStage import AnalysisStage


#*************************************************************************************************** TrackwayPlotPaceStage
class TrackwayPlotPaceStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayPlotPaceStage."""
        super(TrackwayPlotPaceStage, self).__init__(
            key, owner,
            label='Pace Length Plotting',
            **kwargs)
        self._paths = []

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _analyzeTrackway(self, trackway, sitemap):
        pl = self.plot

        self.owner.createFigure(trackway.uid)
        pl.xlabel('Track Index')
        pl.ylabel('Pace Length (m)')
        pl.title(trackway.name)
        pl.grid(True)

        super(TrackwayPlotPaceStage, self)._analyzeTrackway(trackway, sitemap)

        if trackway.cache.get('doPacePlot', False):
            self._paths.append(self.owner.saveFigure(trackway.uid))
        self.owner.closeFigure(trackway.uid)

#_______________________________________________________________________________
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
            entry = track.cache.get('paceData')
            if not entry:
                continue

            aTrack = track.getAnalysisPair(self.analysisSession)
            x.append(aTrack.curvePosition)
            y.append(entry['entered'].value)
            error.append(entry['entered'].uncertainty)
            lw.append(2.0)

        if len(x) < 2:
            return

        trackway.cache.set('doPacePlot', True)

        if series.left and series.pes:
            color = ColorValue('blue')
        elif series.pes:
            color = ColorValue('sky blue')
        elif series.left:
            color = ColorValue('green')
        else:
            color = ColorValue('light green')

        pl.errorbar(x, y, yerr=error, fmt='o', color=color.web)

#_______________________________________________________________________________
    def _postAnalyze(self):
        self.mergePdfs(self._paths)
