# TrackwayStatsStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter

#*************************************************************************************************** TrackwayStatsStage
class TrackwayStatsStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayStatsStage."""
        super(TrackwayStatsStage, self).__init__(
            key, owner,
            label='Trackway Statistics',
            **kwargs)

        self._trackways = []
        self._csv = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._trackways = []

        csv = CsvWriter()
        csv.path = self.getPath('Trackway-Stats.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('name', 'Name'),
            ('length', 'Length'),
            ('gauge', 'Gauge'),
            ('gaugeUnc', 'Gauge Uncertainty'),
            ('strideLength', 'Stride Length'),
            ('strideLengthUnc', 'Stride Length Uncertainty'),
            ('paceLength', 'Pace Length'),
            ('paceLengthUnc', 'Pace Length Uncertainty'),
            ('density', 'Density'),
            ('densityNorm', 'Normalize Density'),
            ('densityNormUnc', 'Normalize Density Uncertainty'),
            ('pesWidth', 'Pes Width'),
            ('pesWidthUnc', 'Pes Width Uncertainty'),
            ('manusWidth', 'Manus Width'),
            ('manusWidthUnc', 'Manus Width Uncertainty') )
        self._csv = csv

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        aTrackway = trackway.getAnalysisPair(self.analysisSession)
        bundle = self.owner.getSeriesBundle(trackway)
        density = bundle.count/aTrackway.curveLength if aTrackway.curveLength else 0.0

        data = {'pesWidths':[], 'manusWidths':[], 'strides':[], 'paces':[]}
        trackway.cache.set('data', data)
        super(TrackwayStatsStage, self)._analyzeTrackway(trackway, sitemap)

        pesWidth = NumericUtils.getWeightedMeanAndDeviation(data['pesWidths'])
        manusWidth = NumericUtils.getWeightedMeanAndDeviation(data['manusWidths'])
        strideLengths = NumericUtils.getWeightedMeanAndDeviation(data['strides'])
        paceLengths = NumericUtils.getWeightedMeanAndDeviation(data['paces'])

        self._csv.createRow(
            name=trackway.name,
            length=bundle.count,

            strideLength=strideLengths.value,
            strideLengthUnc=strideLengths.uncertainty,

            paceLength=paceLengths.value,
            paceLengthUnc=paceLengths.uncertainty,

            gauge=aTrackway.simpleGauge,
            gaugeUnc=aTrackway.simpleGaugeUnc,

            density=density,
            densityNorm=density*pesWidth.value,
            densityNormUnc=density*pesWidth.uncertainty,

            pesWidth=pesWidth.value,
            pesWidthUnc=pesWidth.uncertainty,

            manusWidth=manusWidth.value,
            manusWidthUnc=manusWidth.uncertainty)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        data = trackway.cache.get('data')
        aTrack = track.getAnalysisPair(self.analysisSession)

        if track.pes:
            data['pesWidths'].append(track.widthValue)
        else:
            data['manusWidths'].append(track.lengthValue)

        if aTrack.strideLength:
            data['strides'].append(aTrack.strideLengthValue)

        if aTrack.paceLength:
            data['paces'].append(aTrack.paceLengthValue)


#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        self.logger.write('TRACKWAY COUNT: %s' % self._csv.count)
        self._csv.save()

