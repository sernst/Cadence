# TrackwayCurveStatsStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import numpy as np

from pyaid.dict.DictUtils import DictUtils
from pyaid.list.ListUtils import ListUtils
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.analysis.shared.plotting.Histogram import Histogram

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

        self._trackwaySparseness = dict()
        self._paths = []

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._trackwaySparseness = dict()
        self._paths = []

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        pesSpacings     = []
        manusSpacings   = []
        denseCount      = 0
        denseSpacing    = None

        for key, series in self.owner.getTrackwaySeries(trackway).items():
            # Iterate through each series in the trackway

            spacing = self._calculateAverageSpacing(series)
            if not spacing:
                continue

            if series.tracks[0].pes:
                pesSpacings.append(spacing)
            else:
                manusSpacings.append(spacing)

            # The highest track count series should be stored for reference
            if series.count > denseCount:
                denseSpacing = spacing

        pesSpacings     = self._calculateSparseness(pesSpacings, denseSpacing)
        manusSpacings   = self._calculateSparseness(manusSpacings, denseSpacing)

        self._trackwaySparseness[trackway.uid] = {'manus':manusSpacings, 'pes':pesSpacings}

#___________________________________________________________________________________________________ _calculateSparseness
    @classmethod
    def _calculateSparseness(cls, spacings, reference):
        """ Calculates the relative sparseness from the series spacings list and the reference
            spacing. """

        out = []
        for data in spacings:
            # For each entry in the tests, normalize that value to the most complete (highest
            # track count) series to create a relative sparseness rating

            diff    = data.value - reference.value
            absDiff = abs(diff)
            dVal    = reference.value
            sign    = 0.0 if absDiff == 0.0 else diff/absDiff
            unc     = abs(data.uncertainty/dVal) + abs(dVal*sign - absDiff)/(dVal*dVal)
            out.append(NumericUtils.toValueUncertainty(
                value=100.0*absDiff/dVal,
                uncertainty=100.0*unc))

        return ListUtils.sortObjectList(out, 'value')

#___________________________________________________________________________________________________ _calculateAverageSpacing
    @classmethod
    def _calculateAverageSpacing(cls, series):
        """ Determines the average spacing of the tracks in the track series for use as a
            comparative measure of sparseness to the other track series in the trackway. If the
            series is not ready or does not have a sufficient number of tracks, this method will
            return None.

            :param: series | TrackSeries
                The series on which to determine the average spacing.

            :return: VALUE_UNCERTAINTY
                A value uncertainty instance that represents the average spacing of the series,
                or None if it's the calculation is aborted. """

        if not series.isReady:
            # Skip trackways with invalid series
            return None

        tracks = series.tracks
        if not tracks or len(tracks) < 2:
            # Ignore series with less than two tracks
            return None

        length = 0.0
        uncs    = []

        for i in ListUtils.range(len(tracks) - 1):
            line = LineSegment2D(
                start=tracks[i].positionValue,
                end=tracks[i + 1].positionValue)
            spacing = line.length
            length += spacing.value
            uncs.append(spacing.uncertainty)

        unc = NumericUtils.sqrtSumOfSquares(*uncs)

        return NumericUtils.toValueUncertainty(
            value=length/float(len(tracks)),
            uncertainty=unc/float(len(tracks)) )

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""

        label = 'Both'
        lows, mids, highs, tsValues, twValues, totals = self._processSparsenessResults(None)
        self._paths.append(self._scatterSparseness(label, lows, mids, highs))
        self._paths.append(self._histogramSeriesSparseness(label, tsValues))
        self._paths.append(self._histogramTrackwaySparseness(label, twValues))

        totalAve = NumericUtils.weightedAverage(*totals)
        self.logger.write('Total Average Spareness: %s' % totalAve.label)

        label = 'Pes'
        lows, mids, highs, tsValues, twValues, totals = self._processSparsenessResults('pes')
        self._paths.append(self._scatterSparseness(label, lows, mids, highs))
        self._paths.append(self._histogramSeriesSparseness(label, tsValues))
        self._paths.append(self._histogramTrackwaySparseness(label, twValues))

        totalAve = NumericUtils.weightedAverage(*totals)
        self.logger.write('Total Average Pes Spareness: %s' % totalAve.label)

        label = 'Manus'
        lows, mids, highs, tsValues, twValues, totals = self._processSparsenessResults('manus')
        self._paths.append(self._scatterSparseness(label, lows, mids, highs))
        self._paths.append(self._histogramSeriesSparseness(label, tsValues))
        self._paths.append(self._histogramTrackwaySparseness(label, twValues))

        totalAve = NumericUtils.weightedAverage(*totals)
        self.logger.write('Total Average Manus Spareness: %s' % totalAve.label)

        self.mergePdfs(self._paths, 'Trackway-Curve-Stats.pdf')

#___________________________________________________________________________________________________ _processSparsenessResults
    def _processSparsenessResults(self, key):
        """_processSparsenessResults doc..."""

        index       = 0
        means       = []
        totals      = []
        twValues    = []
        tsValues    = []

        lows        = dict(x=[], y=[], error=[], color='#666666')
        mids        = dict(x=[], y=[], error=[], color='#33CC33')
        highs       = dict(x=[], y=[], error=[], color='#CC3333')

        for uid, entry in DictUtils.iter(self._trackwaySparseness):
            # For each test list in track ratings process the data and filter it into the correct
            # segments for plotting.

            if not key:
                data = entry['pes'] + entry['manus']
            else:
                data = entry[key]

            data = ListUtils.sortObjectList(data, 'value')

            index  += 1

            if len(data) < 2:
                continue

            average = NumericUtils.weightedAverage(*data[1:])
            means.append(average)
            totals.extend(data[1:])
            twValues.append(average.value)

            maxVal = data[0]
            for v in data[1:]:
                if v.value > maxVal.value:
                    maxVal = v

            if maxVal.value < 15.0:
                target = lows
            elif maxVal.value < 50.0:
                target = mids
            else:
                target = highs

            for v in data[1:]:
                tsValues.append(v.value)

                target['x'].append(index)
                target['y'].append(v.value)
                target['error'].append(v.uncertainty)

        return lows, mids, highs, tsValues, twValues, totals

#___________________________________________________________________________________________________ _scatterSparseness
    def _scatterSparseness(self, label, *plots):
        """_scatterSparseness doc..."""

        yRange  = (-25.0, 175.0)
        pl      = self.plot

        self.owner.createFigure('items')
        pl.xlabel('Trackway Index')
        pl.ylabel('Relative Sparseness (%)')
        pl.title('Trackway Series Sparseness (%s)' % label)
        pl.xlim(0.0, 160)
        pl.ylim(*yRange)

        pl.grid(True)
        ax = pl.gca()
        ax.set_yticks(np.arange(yRange[0], yRange[1], 25))
        ax.set_yticks(np.arange(yRange[0], yRange[1], 6.25), minor=True)
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)

        for item in plots:
            pl.scatter(x=item['x'], y=item['y'], s=12, c=item['color'], linewidths=0.0)
        return self.owner.saveFigure('items')

#___________________________________________________________________________________________________ _histogramSeriesSparseness
    def _histogramSeriesSparseness(self, label, values):
        """_histogramSeriesSparseness doc..."""

        path        = self.getTempFilePath(extension='pdf')
        h           = Histogram(data=values, isLog=True)
        h.xLimits   = [0, 200]
        h.binCount  = 20
        h.xLabel    = 'Relative Sparseness (%)'
        h.title     = 'Track Series Sparseness (%s)' % label

        h.shaveDataToXLimits()
        h.save(path=path)
        return path

#___________________________________________________________________________________________________ _histogramTrackwaySparseness
    def _histogramTrackwaySparseness(self, label, values):
        """ Creates a histogram for each trackway entry in the values list. """

        path        = self.getTempFilePath(extension='pdf')
        h           = Histogram(data=values, isLog=True)
        h.xLimits   = [0, 200]
        h.binCount  = 20
        h.xLabel    = 'Relative Sparseness (%)'
        h.title     = 'Trackway Sparseness (%s)' % label

        h.shaveDataToXLimits()
        h.save(path=path)
        return path
