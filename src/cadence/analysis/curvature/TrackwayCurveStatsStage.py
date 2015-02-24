# TrackwayCurveStatsStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.dict.DictUtils import DictUtils
from pyaid.list.ListUtils import ListUtils
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.LineSegment2D import LineSegment2D

#*************************************************************************************************** TrackwayCurveStatsStage
class TrackwayCurveStatsStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayCurveStatsStage."""
        super(TrackwayCurveStatsStage, self).__init__(
            key, owner,
            label='Trackway Curve Stats',
            **kwargs)

        self._trackRatings = dict()

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._trackRatings = dict()

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        super(TrackwayCurveStatsStage, self)._analyzeTrackway(trackway, sitemap)

        trackSeries = self.owner.getTrackwaySeries(trackway)
        tests       = []
        denseValue  = None

        for key, series in trackSeries.items():
            # For each series in the trackway, calculate the average length between tracks in the
            # series and store that number in the tests dictionary.

            if not series.isReady:
                # Skip trackways with invalid series
                return

            tracks = series.tracks
            if not tracks or len(tracks) < 2:
                # Ignore series with less than two tracks
                continue

            length = 0.0
            unc    = 0.0
            for i in ListUtils.range(len(tracks) - 1):
                line = LineSegment2D(
                    start=tracks[i].positionValue,
                    end=tracks[i + 1].positionValue)
                spacing = line.length
                length += spacing.value
                unc    += spacing.uncertainty

            value = NumericUtils.toValueUncertainty(
                length/float(len(tracks)), unc/float(len(tracks)))
            tests.append(value)

            if not denseValue or value.value < denseValue.value:
                denseValue  = value

        out = []
        for value in tests:
            # For each entry in the tests, normalize that value to the densest series
            out.append(NumericUtils.toValueUncertainty(
                value=value.value/denseValue.value,
                uncertainty=value.uncertainty/denseValue.uncertainty))

        out.sort()
        self._trackRatings[trackway.uid] = out

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""

        pl      = self.plot
        x       = []
        y       = []
        error   = []
        paths   = []
        index   = 0

        for uid, data in DictUtils.iter(self._trackRatings):
            # For each test list in track ratings

            if len(data) < 2:
                continue

            index += 1
            for v in data[1:]:
                x.append(index)
                y.append(v.value)
                error.append(v.uncertainty)

        self.owner.createFigure('items')
        pl.xlabel('Index')
        pl.ylabel('Relative Sparseness')
        pl.title('Trackway Sparseness')
        pl.ylim(0, 5)
        pl.grid(True)
        pl.errorbar(x, y, yerr=error, fmt='o', ms=4)
        paths.append(self.owner.saveFigure('items'))

        self.mergePdfs(paths, 'Trackway-Curve-Stats.pdf')
