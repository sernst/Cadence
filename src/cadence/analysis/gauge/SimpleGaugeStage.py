# SimpleGaugeStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.list.ListUtils import ListUtils

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.curvature.CurveSeries import CurveSeries
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.analysis.shared.PositionValue2D import PositionValue2D
from cadence.analysis.shared.plotting.ScatterPlot import ScatterPlot

#*************************************************************************************************** SimpleGaugeStage
class SimpleGaugeStage(CurveOrderedAnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

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
        self._trackwayGauges = []
        self._trackwayGaugeMeans = []
        self._count = 0

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._paths = []
        self._errorTracks = []
        self._ignoreTracks = []
        self._trackwayGauges = []
        self._trackwayGaugeMeans = []
        self._count = 0

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

        trackway.cache.set('simpleGauges', [])

        for key, series in bundle.items():
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

        out = trackway.cache.extract('simpleGauges')
        if not out:
            return

        points = []
        lengths = []
        for entry in out:
            points.append(entry['point'])
            lengths.append(entry['length'])

        try:
            simpleGauge = NumericUtils.weightedAverage(lengths)
            self._trackwayGauges.append(simpleGauge)
        except ZeroDivisionError:
            return

        values = []
        for l in lengths:
            values.append(l.raw)

        try:
            simpleGaugeVariance = NumericUtils.getMeanAndDeviation(values)
            self._trackwayGaugeMeans.append(simpleGaugeVariance)
        except ZeroDivisionError:
            return

        plot = ScatterPlot(
            data=points,
            title='%s Gauges (%s)' % (trackway.name, simpleGauge.label),
            xLabel='Track Position (m)',
            yLabel='Gauge (m)')
        self._paths.append(plot.save(self.getTempFilePath(extension='pdf')))

        analysisTrackway = trackway.getAnalysisPair(self.analysisSession)
        analysisTrackway.simpleGauge = simpleGauge.raw
        analysisTrackway.simpleGaugeUnc = simpleGauge.rawUncertainty

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        if series.count < 1:
            return

        segmentPair = None
        segmentSeries = None
        skipped = 0
        for key, otherSeries in series.bundle.items():
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

        line = segmentPair['line']
        sitemap.cache.get('drawing').lineSegment(
            line, stroke=color, stroke_width=1, stroke_opacity='0.5')

        analysisTrack = track.getAnalysisPair(self.analysisSession)
        analysisTrack.simpleGauge = line.length.raw
        analysisTrack.simpleGaugeUnc = line.length.rawUncertainty

        length = line.length
        point = PositionValue2D(
            x=analysisTrack.curvePosition, xUnc=0.0,
            y=length.value, yUnc=length.uncertainty)
        trackway.cache.get('simpleGauges').append({'point':point, 'length':length})

        self._count += 1

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        self.logger.write('%s gauge calculated tracks' % self._count)

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

        out = []
        for entry in self._trackwayGaugeMeans:
            out.append(PositionValue2D(x=len(out), y=entry.value, yUnc=entry.uncertainty))

        plot = ScatterPlot(
            data=ListUtils.sortObjectList(out, 'y'),
            title='Trackway Gauges & Variances',
            xLabel='Arbitrary Trackway Index',
            yLabel='Average Trackway Gauge (m)',
            color='purple')
        self._paths.insert(0, plot.save(self.getTempFilePath(extension='pdf')))

        out = []
        for entry in self._trackwayGauges:
            out.append(PositionValue2D(x=len(out), y=entry.value, yUnc=entry.uncertainty))

        plot = ScatterPlot(
            data=ListUtils.sortObjectList(out, 'y'),
            title='Trackway Gauges',
            xLabel='Arbitrary Trackway Index',
            yLabel='Average Trackway Gauge (m)',
            color='red')
        self._paths.insert(0, plot.save(self.getTempFilePath(extension='pdf')))

        self.mergePdfs(self._paths, 'Simple-Gauge.pdf')
