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
from cadence.models.analysis.Analysis_Trackway import Analysis_Trackway
from cadence.svg.CadenceDrawing import CadenceDrawing

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

        self._drawing = None
        self._paths = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: trackwaySparseness
    @property
    def trackwaySparseness(self):
        return self.cache.getOrAssign('trackwaySparseness', {})

#___________________________________________________________________________________________________ GS: orderData
    @property
    def orderData(self):
        return self.cache.getOrAssign('orderData', {})

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._drawing = None
        self._paths = []

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        """_analyzeSitemap doc..."""
        self._drawing = CadenceDrawing(self.getPath(sitemap.name + '.svg'), sitemap)

        # and place a grid and the federal coordinates in the drawing file
        self._drawing.grid()
        self._drawing.federalCoordinates()

        super(TrackwayCurveStatsStage, self)._analyzeSitemap(sitemap)

        self._drawing.save()
        self._drawing = None

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        pesSpacings     = []
        manusSpacings   = []
        denseSeries     = None
        denseSpacing    = None
        trackwaySeries  = self.owner.getTrackwaySeries(trackway)

        for key, series in trackwaySeries.items():
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

        self.trackwaySparseness[trackway.uid] = dict(
            manus=manusSpacings,
            pes=pesSpacings,
            dense=denseSeries)

        if not denseSeries:
            return

        orderData = dict(
            trackway=trackway,
            denseSeries=denseSeries,
            segments=[])
        self.orderData[trackway.uid] = orderData

        segments = orderData['segments']
        tracks   = denseSeries.tracks

        for i in ListUtils.range(len(tracks) - 1):
            # Create a segment For each track in the reference series
            line = LineSegment2D(start=tracks[i].positionValue, end=tracks[i + 1].positionValue)
            segments.append({'track':tracks[i], 'line':line, 'pairs':[]})
            self._drawing.circle(
                tracks[i].positionValue.toMayaTuple(), 5,
                stroke='none', fill='green', fill_opacity='0.5')

        # Add segments to the beginning and end to handle overflow conditions where the paired
        # track series extend beyond the bounds of the reference series
        segments.insert(0, {
            'track':None, 'pairs':[],
            'line':segments[0]['line'].createPreviousLineSegment(100.0) })

        segments.append({
            'track':tracks[-1], 'pairs':[],
            'line':segments[-1]['line'].createNextLineSegment(100.0) })

        super(TrackwayCurveStatsStage, self)._analyzeTrackway(trackway, sitemap)

        for segment in segments:
            # Sort the paired segments by distance from the segment start position to order them
            # properly from first to last
            if segment['pairs']:
                ListUtils.sortDictionaryList(segment['pairs'], 'distance', inPlace=True)

        #-------------------------------------------------------------------------------------------
        # DEBUG PRINT OUT
        print('\nTRACKWAY[%s]:' % trackway.name)
        for segment in segments:
            print('  TRACK: %s' % (segment['track'].fingerprint if segment['track'] else 'NONE'))
            for item in segment['pairs']:
                print('    * %s (%s)' % (item['track'].fingerprint, item['distance'].label))
                for debugItem in item['debug']:
                    print('      - %s' % DictUtils.prettyPrint(debugItem['print']))

                    data = debugItem['data']

                    if 'testPoint' in data:
                        self._drawing.circle(data['testPoint'].toMayaTuple(), 5)

                    line = data.get('trackToTrack', data.get('testLine'))
                    if line:
                        self._drawing.line(
                            line.start.toMayaTuple(), line.end.toMayaTuple(),
                            stroke='red', stroke_width=1, stroke_opacity='0.33')
                    elif 'matchLine' in data:
                        line = data['matchLine']
                        self._drawing.line(
                            line.start.toMayaTuple(), line.end.toMayaTuple(),
                            stroke='blue', stroke_width=1, stroke_opacity='0.5')

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        orderData = self.orderData[trackway.uid]
        if orderData['denseSeries'] == series:
            return

        super(TrackwayCurveStatsStage, self)._analyzeTrackSeries(series, trackway, sitemap)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        orderData    = self.orderData[trackway.uid]
        segments     = orderData['segments']
        debug        = []
        position     = track.positionValue
        segmentMatch = segments[0]
        pointOnLine  = segmentMatch['line'].closestPointOnLine(position)
        matchLine    = None

        self._drawing.circle(
            track.positionValue.toMayaTuple(), 5, stroke='none', fill='red', fill_opacity='0.5')

        for segment in segments[1:]:
            segmentTrack = segment['track']
            segmentLine  = segment['line']
            trackToTrack = LineSegment2D(segmentLine.start.clone(), position)
            debugItem    = {'TRACK':segmentTrack.fingerprint if segmentTrack else 'NONE'}
            debugData    = {}
            debug.append({'print':debugItem, 'data':debugData})

            # Make sure the track resides in a generally forward direction relative to
            # the direction of the segment. The prevents tracks from matching from behind.
            angle = trackToTrack.angleBetween(segmentLine)
            if abs(angle.degrees) > 100.0:
                debugItem['CAUSE'] = 'Track-to-track angle [%s]' % angle.prettyPrint
                debugData['trackToTrack'] = trackToTrack
                continue

            testPoint = segmentLine.closestPointOnLine(position)
            testLine  = LineSegment2D(testPoint, position.clone())

            # Make sure the test line intersects the segment line at 90 degrees, or the
            # value is invalid.
            angle = testLine.angleBetween(segmentLine)
            if not NumericUtils.equivalent(angle.degrees, 90.0, 2.0):
                debugItem['CAUSE'] = 'Projection angle [%s]' % angle.prettyPrint
                debugData['testLine'] = testLine
                debugData['testPoint'] = testPoint
                continue

            # Skip if the test line length is greater than the existing test line
            if matchLine and testLine.length.value > matchLine.length.value:
                debugItem['CAUSE'] = 'Greater distance [%s > %s]' % (
                    matchLine.length.label, testLine.length.label)
                debugData['testLine'] = testLine
                debugData['testPoint'] = testPoint
                continue

            segmentMatch = segment
            pointOnLine  = testPoint.clone()
            matchLine    = LineSegment2D(pointOnLine.clone(), position.clone())
            debugData['matchLine'] = matchLine

        distance = LineSegment2D(segmentMatch['line'].start, pointOnLine).length
        segmentMatch['pairs'].append({
            'track':track,
            'point':pointOnLine,
            'distance':distance,
            'debug':debug })

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

        #-------------------------------------------------------------------------------------------
        return # DEBUG RETURN TO PREVENT POPULATING DATABASE UNTIL ORDERING WORKS
        #-------------------------------------------------------------------------------------------

        # Add the reference series to the session object for storage in the Analysis_Trackway
        # table. This data persists because it is used later to rebuild track curves in other
        # analyzers.
        model = Analysis_Trackway.MASTER
        session = model.createSession()

        for uid, data in DictUtils.iter(self.trackwaySparseness):
            result = session.query(model).filter(model.uid == uid).first()
            if not result:
                result = model(uid=uid)
                session.add(result)
            result.referenceSeries = data['dense'].firstTrackUid

        session.commit()
        session.close()

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

        for uid, entry in DictUtils.iter(self.trackwaySparseness):
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
