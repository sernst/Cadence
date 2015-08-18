# TrackwayCurveStatsStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import numpy as np
from pyaid.dict.DictUtils import DictUtils
from pyaid.list.ListUtils import ListUtils
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.analysis.shared.plotting.Histogram import Histogram


#*************************************************************************************************** CurveSparsenessStage
class CurveSparsenessStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of CurveSparsenessStage."""
        super(CurveSparsenessStage, self).__init__(
            key, owner,
            label='Trackway Sparseness',
            **kwargs)

        self._paths = []

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def data(self):
        return self.cache.getOrAssign('data', {})

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _preAnalyze(self):
        self._paths = []

#_______________________________________________________________________________
    def _analyzeTrackway(self, trackway, sitemap):
        pesSpacings     = []
        manusSpacings   = []
        denseSeries     = None
        denseSpacing    = None
        bundle  = self.owner.getSeriesBundle(trackway)

        for series in bundle.asList():
            # Iterate through each series in the trackway

            spacing = self._calculateAverageSpacing(series)
            if not spacing:
                continue

            if series.tracks[0].pes:
                pesSpacings.append(spacing)
            else:
                manusSpacings.append(spacing)

            # The highest track count series should be stored for reference
            if not denseSeries:
                denseSeries  = series
                denseSpacing = spacing
                continue

            # Determine if the existing denseSeries should be overwritten, which will be true if
            # the new series has preferential properties.
            overwrite = denseSeries.count == series.count and (
                (not denseSeries.pes and series.pes) or # Pes overwrites manus
                (denseSeries.pes and series.pes and series.left) ) # Left pes overwrites right pes

            if overwrite or denseSeries.count < series.count:
                denseSeries  = series
                denseSpacing = spacing

        pesSpacings     = self._calculateSparseness(pesSpacings, denseSpacing)
        manusSpacings   = self._calculateSparseness(manusSpacings, denseSpacing)

        self.data[trackway.uid] = dict(
            trackway=trackway,
            manus=manusSpacings,
            pes=pesSpacings,
            dense=denseSeries)

#_______________________________________________________________________________
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

#_______________________________________________________________________________
    @classmethod
    def _calculateAverageSpacing(cls, series):
        """ Determines the average spacing of the tracks in the track series for use as a
            comparative measure of sparseness to the other track series in the trackway. If the
            series is not ready or does not have a sufficient number of tracks, this method will
            return None.

            :param: series | TrackSeries
                The series on which to determine the average spacing.

            :return: ValueUncertainty
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

#_______________________________________________________________________________
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

        # Add the reference series to the session object for storage in the Analysis_Trackway
        # table. This data persists because it is used later to rebuild track curves in other
        # analyzers.
        for uid, data in DictUtils.iter(self.data):
            trackway = data['trackway']
            result = trackway.getAnalysisPair(self.analysisSession, createIfMissing=True)
            result.curveSeries = data['dense'].firstTrackUid if data['dense'] else ''

#_______________________________________________________________________________
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

        for uid, entry in DictUtils.iter(self.data):
            # For each test list in track ratings process the data and filter it into the correct
            # segments for plotting.

            data = (entry['pes'] + entry['manus']) if not key else entry[key]
            data = ListUtils.sortObjectList(data, 'value')
            index += 1

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

#_______________________________________________________________________________
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

#_______________________________________________________________________________
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

#_______________________________________________________________________________
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
