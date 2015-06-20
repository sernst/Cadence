# SimpleGaugeStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.curvature.CurveSeries import CurveSeries
from cadence.analysis.shared.CsvWriter import CsvWriter

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
        self._count = 0

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._paths = []
        self._errorTracks = []
        self._ignoreTracks = []
        self._count = 0

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        self._createDrawing(sitemap, 'SIMPLE-GAUGE', 'Simple-Gauge')
        super(SimpleGaugeStage, self)._analyzeSitemap(sitemap)
        self._saveDrawing(sitemap)

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        trackway.cache.set('simpleGauges', [])
        bundle = self.owner.getSeriesBundle(trackway)
        for key, series in bundle.items():
            if series.count < 2:
                continue

            curve = CurveSeries(stage=self, series=series)
            curve.compute()
            curve.draw(sitemap.cache.get('drawing'), drawPairs=False)
            series.cache.set('curve', curve)

        super(SimpleGaugeStage, self)._analyzeTrackway(trackway=trackway, sitemap=sitemap)

        out = trackway.cache.extract('simpleGauges')
        if not out:
            return

        try:
            simpleGauge = NumericUtils.weightedAverage(out)
        except ZeroDivisionError:
            return

        analysisTrackway = trackway.getAnalysisPair(self.analysisSession)
        analysisTrackway.simpleGauge = simpleGauge.raw
        analysisTrackway.simpleGaugeUnc = simpleGauge.rawUncertainty

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        if series.count < 1:
            return

        segmentPair = None
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
                if segmentPair is None:
                    segmentPair = pair
                elif pair['line'].length.raw < segmentPair['line'].length.raw:
                    # Store the shortest of the available gauge lengths
                    segmentPair = pair
                break

        if skipped == 4:
            # If skipped is 4 it means that no suitable series existed for calculating a gauge
            # value and the method should abort quietly
            self._ignoreTracks.append(track)
            return

        if segmentPair is None:
            self._errorTracks.append(track)
            return

        line = segmentPair['line']
        sitemap.cache.get('drawing').lineSegment(
            line, stroke='blue', stroke_width=1, stroke_opacity='0.5')

        trackway.cache.get('simpleGauges').append(line.length)
        analysisTrack = track.getAnalysisPair(self.analysisSession)
        analysisTrack.simpleGauge = line.length.raw
        analysisTrack.simpleGaugeUnc = line.length.rawUncertainty
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
