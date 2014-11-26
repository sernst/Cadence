# TrackwayPlotStrideStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.AnalysisStage import AnalysisStage


#*************************************************************************************************** TrackwayPlotStrideStage
class TrackwayPlotStrideStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayPlotStrideStage."""
        super(TrackwayPlotStrideStage, self).__init__(key, owner, **kwargs)
        self._paths = []

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        pl = self.plot

        self.owner.createFigure(trackway.fingerprint)
        pl.xlabel('Track Index')
        pl.ylabel('Stride Length (m)')
        pl.title(trackway.fingerprint)
        pl.grid(True)

        super(TrackwayPlotStrideStage, self)._analyzeTrackway(trackway, sitemap)

        if trackway.cache.get('doStridePlot', False):
            self._paths.append(self.owner.saveFigure(trackway.fingerprint))
            self.logger.write('[PLOTTED]: Strides for %s' % trackway.fingerprint)
        self.owner.closeFigure(trackway.fingerprint)

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        """_analyzeTrackSeries doc..."""

        if not series.tracks:
            return

        pl    = self.plot
        x     = []
        y     = []
        cols  = []
        lw    = []
        sizes = []

        self.owner.getFigure(trackway.fingerprint)
        for track in series.tracks:
            entry = track.cache.get('strideData')
            if not entry:
                continue

            x.append(track.number)
            y.append(entry['distance'])
            cols.append((0 if entry['sigmaDev'] < 2.0 else 1.0, 0, 0))
            lw.append(2.0)
            sizes.append(30.0)

        if len(x) < 2:
            return

        trackway.cache.set('doStridePlot', True)

        # sizes = 20.0 + 100.0*np.array(sizes)/min(1.0, max(*sizes))
        pl.scatter(x, y, s=sizes, c=cols, marker='|' if series.pes else '_', linewidths=lw, alpha=0.5)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        self.mergePdfs(self._paths)
