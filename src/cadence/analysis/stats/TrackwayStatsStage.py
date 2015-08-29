# TrackwayStatsStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.dict.DictUtils import DictUtils

from pyaid.number.NumericUtils import NumericUtils

from refined_stats.density import DensityDistribution

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter

#******************************************************************************* TrackwayStatsStage
class TrackwayStatsStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                   C L A S S

    TRACKWAY_STATS_CSV = 'Trackway-Stats.csv'
    UNWEIGHTED_TRACKWAY_STATS_CSV = 'Unweighted-Trackway-Stats.csv'

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayStatsStage."""
        super(TrackwayStatsStage, self).__init__(
            key, owner,
            label='Trackway Statistics',
            **kwargs)

        self._trackways = []
        self._weightedStats = None
        self._unweightedStats = None
        self._quartileStats = dict()

#===============================================================================
#                                                           P R O T E C T E D

#_______________________________________________________________________________
    def _preAnalyze(self):
        self._trackways = []

        fields = [
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
            ('pesLength', 'Pes Length'),
            ('pesLengthUnc', 'Pes Length Uncertainty'),
            ('manusWidth', 'Manus Width'),
            ('manusWidthUnc', 'Manus Width Uncertainty'),
            ('manusLength', 'Manus Length'),
            ('manusLengthUnc', 'Manus Length Uncertainty') ]

        csv = CsvWriter()
        csv.path = self.getPath(self.TRACKWAY_STATS_CSV)
        csv.autoIndexFieldName = 'Index'
        csv.addFields(*fields)
        self._weightedStats = csv

        csv = CsvWriter()
        csv.path = self.getPath(self.UNWEIGHTED_TRACKWAY_STATS_CSV)
        csv.autoIndexFieldName = 'Index'
        csv.addFields(*fields)
        self._unweightedStats = csv

    #___________________________________________________________________________
    def _addQuartileEntry(self, label, trackway, data):
        if not data or len(data) < 4:
            return

        if label not in self._quartileStats:
            csv = CsvWriter()
            csv.path = self.getPath(
                '%s-Quartiles.csv' % label.replace(' ', '-'),
                isFile=True)
            csv.autoIndexFieldName = 'Index'
            csv.addFields(
                ('name', 'Name'),
                ('unweightedLowerBound', 'Unweighted Lower Bound'),
                ('unweightedLowerQuart', 'Unweighted Lower Quartile'),
                ('unweightedMedian',     'Unweighted Median'),
                ('unweightedUpperQuart', 'Unweighted Upper Quartile'),
                ('unweightedUpperBound', 'Unweighted Upper Bound'),

                ('lowerBound', 'Lower Bound'),
                ('lowerQuart', 'Lower Quartile'),
                ('median',     'Median'),
                ('upperQuart', 'Upper Quartile'),
                ('upperBound', 'Upper Bound'),

                ('diffLowerBound', 'Diff Lower Bound'),
                ('diffLowerQuart', 'Diff Lower Quartile'),
                ('diffMedian',     'Diff Median'),
                ('diffUpperQuart', 'Diff Upper Quartile'),
                ('diffUpperBound', 'Diff Upper Bound') )
            self._quartileStats[label] = csv

        csv = self._quartileStats[label]
        dd = DensityDistribution(values=data)
        unweighted = dd.getUnweightedTukeyBoxBoundaries()
        weighted = dd.getTukeyBoxBoundaries()

        csv.addRow({
            'index':trackway.index,
            'name':trackway.name,

            'unweightedLowerBound':unweighted[0],
            'unweightedLowerQuart':unweighted[1],
            'unweightedMedian'    :unweighted[2],
            'unweightedUpperQuart':unweighted[3],
            'unweightedUpperBound':unweighted[4],

            'lowerBound':weighted[0],
            'lowerQuart':weighted[1],
            'median'    :weighted[2],
            'upperQuart':weighted[3],
            'upperBound':weighted[4],

            'diffLowerBound':abs(unweighted[0] - weighted[0])/unweighted[0],
            'diffLowerQuart':abs(unweighted[1] - weighted[1])/unweighted[1],
            'diffMedian'    :abs(unweighted[2] - weighted[2])/unweighted[2],
            'diffUpperQuart':abs(unweighted[3] - weighted[3])/unweighted[3],
            'diffUpperBound':abs(unweighted[4] - weighted[4])/unweighted[4] })

#_______________________________________________________________________________
    def _analyzeTrackway(self, trackway, sitemap):
        spec = dict(
            pesWidth='Pes Width',
            pesLength='Pes Length',
            manusWidth='Manus Width',
            manusLength='Manus Length',
            strideLength='Stride Length',
            paceLength='Pace Length')

        data = {}
        for key, label in DictUtils.iter(spec):
            data[key] = []
        trackway.cache.set('data', data)

        super(TrackwayStatsStage, self)._analyzeTrackway(trackway, sitemap)

        self._populateCsvData(self._weightedStats, trackway, data)
        self._populateCsvData(self._unweightedStats, trackway, data, False)

        for key, label in DictUtils.iter(spec):
            self._addQuartileEntry(label, trackway, data[key])

#_______________________________________________________________________________
    def _populateCsvData(self, target, trackway, data, isWeighted =True):
        aTrackway = trackway.getAnalysisPair(self.analysisSession)
        bundle = self.owner.getSeriesBundle(trackway)
        density = bundle.count/aTrackway.curveLength if aTrackway.curveLength else 0.0

        getValue = NumericUtils.weightedAverage \
            if isWeighted \
            else NumericUtils.unweigthedAverage
        pesWidth = getValue(data['pesWidth'])
        pesLength = getValue(data['pesLength'])
        manusWidth = getValue(data['manusWidth'])
        manusLength = getValue(data['manusLength'])

        getValue = NumericUtils.getWeightedMeanAndDeviation \
            if isWeighted \
            else NumericUtils.getMeanAndDeviation

        strideLengths = getValue(data['strideLength'])
        paceLengths = getValue(data['paceLength'])

        target.createRow(
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

            pesLength=pesLength.value,
            pesLengthUnc=pesLength.uncertainty,

            manusWidth=manusWidth.value,
            manusWidthUnc=manusWidth.uncertainty,

            manusLength=manusLength.value,
            manusLengthUnc=manusLength.uncertainty)

#_______________________________________________________________________________
    def _analyzeTrack(self, track, series, trackway, sitemap):
        data = trackway.cache.get('data')
        aTrack = track.getAnalysisPair(self.analysisSession)

        if track.width > 0:
            if track.pes:
                data['pesWidth'].append(track.widthValue)
            else:
                data['manusWidth'].append(track.widthValue)

        if track.length > 0:
            if track.pes:
                data['pesLength'].append(track.lengthValue)
            else:
                data['manusLength'].append(track.lengthValue)

        if aTrack.strideLength:
            data['strideLength'].append(aTrack.strideLengthValue)

        if aTrack.paceLength:
            data['paceLength'].append(aTrack.paceLengthValue)

#_______________________________________________________________________________
    def _postAnalyze(self):
        self.logger.write('TRACKWAY COUNT: %s' % self._weightedStats.count)
        self._weightedStats.save()
        self._unweightedStats.save()

        for key, csv in DictUtils.iter(self._quartileStats):
            csv.save()
