# SpatialUncertaintyStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.analysis.shared.plotting.Histogram import Histogram



#*************************************************************************************************** SpatialUncertaintyStage
class SpatialUncertaintyStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of SpatialUncertaintyStage."""
        super(SpatialUncertaintyStage, self).__init__(
            key, owner,
            label='Spatial Uncertainty',
            **kwargs)

        self._uncs        = []
        self._largeUncCsv = None
        self._tracks      = []

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._uncs = []
        self._tracks = []

        csv = CsvWriter()
        csv.path = self.getPath('Large-Spatial-Uncertainties.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('x', 'X'),
            ('z', 'Z') )
        self._largeUncCsv = csv

#___________________________________________________________________________________________________ _anal
    def _analyzeTrack(self, track, series, trackway, sitemap):
        self._tracks.append(track)
        x = track.xValue
        self._uncs.append(x.uncertainty)
        z = track.zValue
        self._uncs.append(z.uncertainty)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        h = Histogram(
            data=self._uncs,
            binCount=40,
            xLimits=(0, max(*self._uncs)),
            color='r',
            title='Distribution of Spatial (X, Z) Uncertainties',
            xLabel='Uncertainty Value (m)',
            yLabel='Frequency')
        p1 = h.save(self.getTempFilePath(extension='pdf'))

        h.isLog = True
        h.title += ' (log)'
        p2 = h.save(self.getTempFilePath(extension='pdf'))

        self.mergePdfs([p1, p2], self.getPath('Spatial-Uncertainty-Distribution.pdf'))

        average = NumericUtils.getMeanAndDeviation(self._uncs)
        self.logger.write('Average spatial uncertainty: %s' % average.label)

        largeUncertaintyCount = 0
        for t in self._tracks:
            x = t.xValue
            z = t.zValue
            if max(x.uncertainty, z.uncertainty) > 2.0*average.uncertainty:
                largeUncertaintyCount += 1
                self._largeUncCsv.createRow(
                    uid=t.uid,
                    fingerprint=t.fingerprint,
                    x=x.label,
                    z=z.label)

        self.logger.write('%s Tracks with large spatial uncertainties found (%s%%)' % (
            largeUncertaintyCount, NumericUtils.roundToOrder(
                100.0*float(largeUncertaintyCount)/float(len(self._tracks)), -1) ))

        self._largeUncCsv.save()
        self._tracks = []


