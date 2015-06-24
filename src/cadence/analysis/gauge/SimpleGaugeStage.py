# SimpleGaugeStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from collections import namedtuple

from pyaid.list.ListUtils import ListUtils
from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.curvature.CurveSeries import CurveSeries
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.analysis.shared.PositionValue2D import PositionValue2D
from cadence.analysis.shared.plotting.Histogram import Histogram
from cadence.analysis.shared.plotting.ScatterPlot import ScatterPlot

#*************************************************************************************************** SimpleGaugeStage
class SimpleGaugeStage(CurveOrderedAnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _GAUGE_DATA_NT = namedtuple('GAUGE_DATA_NT', ['abs', 'width', 'pace', 'stride'])

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of SimpleGaugeStage."""
        super(SimpleGaugeStage, self).__init__(
            key, owner,
            label='Simple Track Gauge',
            **kwargs)
        self._paths  = []
        self._errorTracks = []
        self._ignoreTracks = []
        self._trackwayGauges = None
        self._count = 0
        self._trackwayCsv = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._trackwayGauges = self._GAUGE_DATA_NT([], [], [], [])
        self._paths = []
        self._errorTracks = []
        self._ignoreTracks = []
        self._count = 0

        self._trackwayCsv = CsvWriter(
            path=self.getPath('Trackway-Gauge-Averages.csv'),
            autoIndexFieldName='Index',
            fields=[
                ('name', 'Name'),
                ('count', 'Pes Count'),
                ('abs', 'Absolute'),
                ('absUnc', 'Abs Unc'),
                ('stride', 'Stride Norm'),
                ('strideUnc', 'Stride Unc'),
                ('pace', 'Pace Norm'),
                ('paceUnc', 'Pace Unc'),
                ('width', 'Width Norm'),
                ('widthUnc', 'Width Unc')])

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        self._createDrawing(sitemap, 'SIMPLE-GAUGE', 'Simple-Gauge')
        super(SimpleGaugeStage, self)._analyzeSitemap(sitemap)
        self._saveDrawing(sitemap)

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        bundle = self.owner.getSeriesBundle(trackway)
        if not bundle.isReady:
            # Skip trackways that have incomplete series
            return

        data = self._collectGaugeData(bundle, trackway, sitemap)
        if data['gauges'].abs:
            self._processGaugeData(bundle, trackway, data)

#___________________________________________________________________________________________________ _collectGaugeData
    def _collectGaugeData(self, bundle, trackway, sitemap):
        """ Collects the trackway gauge data by generating projections for each series and then
            iterating over every track in the trackway and extracting the gauge information from
            the CurveSeries projection data.

            @param bundle: TrackSeriesBundle
            @param trackway: Tracks_Trackway
            @param sitemap: Tracks_Sitemap
            @return: dict """

        trackway.cache.set('data', {'points':[], 'gauges':self._GAUGE_DATA_NT([], [], [], [])})

        for key, series in bundle.items():
            series.cache.set('referenceWidth', series.averageTrackWidth)
            if series.count < 2:
                continue

            curve = CurveSeries(stage=self, series=series)
            try:
                curve.compute()
            except Exception as err:
                self.logger.writeError([
                    '[ERROR]: Failed to compute track curve projection',
                    'TRACKWAY: %s' % trackway.name,
                    'SERIES: %s[%s]' % (series.fingerprint, series.count) ], err)
                raise

            curve.draw(sitemap.cache.get('drawing'), drawPairs=False)
            series.cache.set('curve', curve)

        super(SimpleGaugeStage, self)._analyzeTrackway(trackway=trackway, sitemap=sitemap)

        for key, series in bundle.items():
            series.cache.remove('referenceWidth')
        return trackway.cache.extract('data')

#___________________________________________________________________________________________________ _processGaugeData
    def _processGaugeData(self, bundle, trackway, data):
        pesCount = bundle.leftPes.count + bundle.rightPes.count
        record = {'name':trackway.name, 'count':pesCount}

        gaugeData = data['gauges']

        try:
            value = NumericUtils.getWeightedMeanAndDeviation(gaugeData.abs)
            record['abs'] = value.value
            record['absUnc'] = value.uncertainty
            self._trackwayGauges.abs.append((pesCount, value))
        except ZeroDivisionError:
            return

        widthValue = NumericUtils.getWeightedMeanAndDeviation(gaugeData.width)
        record['width'] = widthValue.value
        record['widthUnc'] = widthValue.uncertainty
        self._trackwayGauges.width.append((pesCount, widthValue))

        if gaugeData.pace:
            value = NumericUtils.getWeightedMeanAndDeviation(gaugeData.pace)
            record['pace'] = value.value
            record['paceUnc'] = value.uncertainty
            self._trackwayGauges.pace.append((pesCount, value))
        else:
            record['pace'] = ''
            record['paceUnc'] = ''

        if gaugeData.stride:
            value = NumericUtils.getWeightedMeanAndDeviation(gaugeData.stride)
            record['stride'] = value.value
            record['strideUnc'] = value.uncertainty
            self._trackwayGauges.stride.append((pesCount, value))
        else:
            record['stride'] = ''
            record['strideUnc'] = ''

        self._trackwayCsv.addRow(record)

        plot = ScatterPlot(
            data=data['points'],
            title='%s Width-Normalized Gauges (%s)' % (trackway.name, widthValue.label),
            xLabel='Track Position (m)',
            yLabel='Gauge (AU)')
        self._paths.append(plot.save(self.getTempFilePath(extension='pdf')))

        analysisTrackway = trackway.getAnalysisPair(self.analysisSession)
        analysisTrackway.simpleGauge = widthValue.raw
        analysisTrackway.simpleGaugeUnc = widthValue.rawUncertainty

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        if series.count < 1 or not track.pes:
            return

        segmentPair = None
        segmentSeries = None
        skipped = 0
        for key, otherSeries in series.bundle.items():
            if not otherSeries.pes:
                continue

            if otherSeries == series or otherSeries.left == series.left or otherSeries.count < 2:
                # If the series isn't suitable for comparison then mark this as a skipped attempt
                # and continue.
                skipped += 1
                continue

            segment = otherSeries.cache.get('curve').getTrackSegment(track)
            if segment is None:
                continue

            for pair in segment.pairs:
                if pair['track'] != track:
                    continue
                if segmentPair is None or pair['line'].length.raw < segmentPair['line'].length.raw:
                    # Store the shortest of the available gauge lengths
                    segmentPair = pair
                    segmentSeries = otherSeries
                break

        if skipped == 4:
            # If skipped is 4 it means that no suitable series existed for calculating a gauge
            # value and the method should abort quietly
            self._ignoreTracks.append(track)
            return

        if segmentPair is None:
            self._errorTracks.append(track)
            return

        color = 'blue' if segmentSeries.pes == series.pes else 'orange'

        data = trackway.cache.get('data')
        gauges = data['gauges']

        line = segmentPair['line']
        sitemap.cache.get('drawing').lineSegment(
            line, stroke=color, stroke_width=1, stroke_opacity='0.5')

        length = line.length
        gauges.abs.append(length)

        analysisTrack = track.getAnalysisPair(self.analysisSession)
        analysisTrack.simpleGauge = line.length.raw
        analysisTrack.simpleGaugeUnc = line.length.rawUncertainty

        widthNormGauge = NumericUtils.divideValueUncertainties(
            numeratorValue=length,
            denominatorValue=series.cache.get('referenceWidth'))
        gauges.width.append(widthNormGauge)

        point = PositionValue2D(
            x=analysisTrack.curvePosition, xUnc=0.0,
            y=widthNormGauge.value, yUnc=widthNormGauge.uncertainty)
        data['points'].append(point)

        if analysisTrack.paceLength:
            gauges.pace.append(NumericUtils.divideValueUncertainties(
                length, analysisTrack.paceLengthValue))

        if analysisTrack.strideLength:
            gauges.stride.append(NumericUtils.divideValueUncertainties(
                length, analysisTrack.strideLengthValue))

        self._count += 1

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        self.logger.write('%s gauge calculated tracks' % self._count)

        self._trackwayCsv.save()

        csv = CsvWriter(
            path=self.getPath('Simple-Gauge-Errors.csv', isFile=True),
            autoIndexFieldName='Index',
            fields=[
                ('uid', 'UID'),
                ('fingerprint', 'Fingerprint') ])
        for track in self._errorTracks:
            csv.createRow(uid=track.uid, fingerprint=track.fingerprint)
        csv.save()

        if self._errorTracks:
            self.logger.write('Failed to calculate gauge for %s tracks' % len(self._errorTracks))

        csv = CsvWriter(
            path=self.getPath('Simple-Gauge-Ignores.csv', isFile=True),
            autoIndexFieldName='Index',
            fields=[
                ('uid', 'UID'),
                ('fingerprint', 'Fingerprint') ])
        for track in self._ignoreTracks:
            csv.createRow(uid=track.uid, fingerprint=track.fingerprint)
        csv.save()

        if self._ignoreTracks:
            self.logger.write('%s tracks lacked suitability for gauge calculation' % len(
                self._ignoreTracks))

        plotData = [
            ('stride', 'red', 'AU', 'Stride-Normalized Weighted'),
            ('pace', 'green', 'AU', 'Pace-Normalized Weighted'),
            ('width', 'blue', 'AU', 'Width-Normalized Weighted'),
            ('abs', 'purple', 'm', 'Absolute Unweighted') ]

        for data in plotData:
            out = []
            source = ListUtils.sortListByIndex(
                source=getattr(self._trackwayGauges, StringUtils.toStr2(data[0])),
                index=0,
                inPlace=True)

            for item in source:
                out.append(PositionValue2D(x=len(out), y=item[1].value, yUnc=item[1].uncertainty))
            self._plotTrackwayGauges(out, *data[1:])

        self.mergePdfs(self._paths, 'Gauges.pdf')

#___________________________________________________________________________________________________ _plotTrackwayGauges
    def _plotTrackwayGauges(self, points, color, unit, heading):

        histData = []
        for p in points:
            histData.append(p.yValue.value)

        plot = Histogram(
            data=histData,
            title='%s Trackway Gauges' % heading,
            xLabel='Averaged Trackway Gauge (%s)' % unit,
            yLabel='Frequency',
            color=color)
        self._paths.insert(0, plot.save(self.getTempFilePath(extension='pdf')))

        plot = ScatterPlot(
            data=ListUtils.sortObjectList(points, 'y', inPlace=True),
            title='%s Trackway Gauges' % heading,
            xLabel='Trackway Pes Count (#)',
            yLabel='Averaged Trackway Gauge (%s)' % unit,
            color=color)
        self._paths.insert(0, plot.save(self.getTempFilePath(extension='pdf')))
