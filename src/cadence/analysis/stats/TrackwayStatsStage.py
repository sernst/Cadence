# TrackwayStatsStage.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

from pyaid.dict.DictUtils import DictUtils
from pyaid.number.NumericUtils import NumericUtils
from refined_stats.density import DensityDistribution

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter


#*******************************************************************************
from cadence.analysis.shared.plotting.MultiScatterPlot import MultiScatterPlot


class TrackwayStatsStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                     C L A S S

    TRACKWAY_STATS_CSV = 'Trackway-Stats.csv'
    UNWEIGHTED_TRACKWAY_STATS_CSV = 'Unweighted-Trackway-Stats.csv'

    #___________________________________________________________________________
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
        self._densityPlots = dict()

#===============================================================================
#                                                             P R O T E C T E D

    #___________________________________________________________________________
    def _preAnalyze(self):
        self._trackways = []
        self._densityPlots = dict()

        fields = [
            ('name', 'Name'),
            ('length', 'Length'),
            ('gauge', 'Gauge'),
            ('gaugeUnc', 'Gauge Uncertainty'),
            ('widthNormGauge', 'Width Normalized Gauge'),
            ('widthNormGaugeUnc', 'Width Normalized Gauge Uncertainty'),
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

                ('normality', 'Normality'),
                ('unweightedNormality', 'Unweighted Normality'),

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

        #-----------------------------------------------------------------------
        # PLOT DENSITY
        #   Create a density plot for each value
        p = MultiScatterPlot(
            title='%s %s Density Distribution' % (trackway.name, label),
            xLabel=label,
            yLabel='Probability (AU)')

        p.addPlotSeries(
            line=True,
            markers=False,
            label='Weighted',
            color='blue',
            data=dd.createDistribution(
                xValues=dd.getAdaptiveRange(10.0),
                scaled=True,
                asPoints=True) )

        temp = DensityDistribution.fromValuesOnly(dd.getNumericValues(raw=True))
        p.addPlotSeries(
            line=True,
            markers=False,
            label='Unweighted',
            color='red',
            data=temp.createDistribution(
                xValues=temp.getAdaptiveRange(10.0),
                scaled=True,
                asPoints=True) )

        if label not in self._densityPlots:
            self._densityPlots[label] = []
        self._densityPlots[label].append(
            p.save(self.getTempFilePath(extension='pdf')))

        #-----------------------------------------------------------------------
        # NORMALITY
        #       Calculate the normality of the weighted and unweighted
        #       distributions as a test against how well they conform to
        #       the Normal distribution calculated from the unweighted data.
        #
        #       The unweighted Normality test uses a basic bandwidth detection
        #       algorithm to create a uniform Gaussian kernel to populate the
        #       DensityDistribution. It is effectively a density kernel
        #       estimation, but is aggressive in selecting the bandwidth to
        #       prevent over-smoothing multi-modal distributions.
        if len(data) < 8:
            normality = -1.0
            unweightedNormality = -1.0
        else:
            result = NumericUtils.getMeanAndDeviation(data)
            mean = result.raw
            std = result.rawUncertainty
            normality = dd.compareAgainstGaussian(mean, std)

            rawValues = []
            for value in data:
                rawValues.append(value.value)
            ddRaw = DensityDistribution.fromValuesOnly(values=rawValues)
            unweightedNormality = ddRaw.compareAgainstGaussian(mean, std)

        csv.addRow({
            'index':trackway.index,
            'name':trackway.name,

            'normality':normality,
            'unweightedNormality':unweightedNormality,

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
            paceLength='Pace Length',
            gauge='Gauge',
            widthNormGauge='Width Normalized Gauge')

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
        density = bundle.count/aTrackway.curveLength \
            if aTrackway.curveLength \
            else 0.0

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
        gauge = getValue(data['gauge'])

        temp = data['widthNormGauge']
        for g in data['gauge']:
            # Generate the width normalized gauge values after the best
            # estimate for the pes width has been determined.
            temp.append(g/pesWidth)
        widthNormGauge = getValue(temp)

        target.createRow(
            name=trackway.name,
            length=bundle.count,

            strideLength=strideLengths.value,
            strideLengthUnc=strideLengths.uncertainty,

            paceLength=paceLengths.value,
            paceLengthUnc=paceLengths.uncertainty,

            gauge=gauge.value,
            gaugeUnc=gauge.uncertainty,

            widthNormGauge=widthNormGauge.value,
            widthNormGaugeUnc=widthNormGauge.uncertainty,

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
            w = track.widthValue
            data['pesWidth' if track.pes else 'manusWidth'].append(w)

        if track.length > 0:
            l = track.lengthValue
            data['pesLength' if track.pes else 'manusLength'].append(l)

        if aTrack.strideLength:
            data['strideLength'].append(aTrack.strideLengthValue)

        if aTrack.paceLength:
            data['paceLength'].append(aTrack.paceLengthValue)

        if track.pes and aTrack.simpleGauge:
            data['gauge'].append(aTrack.gaugeValue)

#_______________________________________________________________________________
    def _postAnalyze(self):
        self.logger.write('TRACKWAY COUNT: %s' % self._weightedStats.count)
        self._weightedStats.save()
        self._unweightedStats.save()

        for key, csv in DictUtils.iter(self._quartileStats):
            csv.save()

        for label, paths in DictUtils.iter(self._densityPlots):
            self.mergePdfs(paths, '%s-Densities.pdf' % label.replace(' ', '-'))
