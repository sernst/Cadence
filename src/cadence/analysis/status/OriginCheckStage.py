# OriginCheckStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter

#*************************************************************************************************** OriginCheckStage
class OriginCheckStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of OriginCheckStage."""
        super(OriginCheckStage, self).__init__(
            key, owner,
            label='Origin Check',
            **kwargs)

        self._tracks = []
        self._csv = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._tracks = []

        csv = CsvWriter()
        csv.path = self.getPath('Origin-Located.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint') )
        self._csv = csv

#___________________________________________________________________________________________________ _anal
    def _analyzeTrack(self, track, series, trackway, sitemap):
        if NumericUtils.equivalent(track.x, 0.0) and NumericUtils.equivalent(track.z, 0.0):
            self._tracks.append(track)
            self._csv.addRow({'uid':track.uid, 'fingerprint':track.fingerprint})

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        self.logger.write('ORIGIN TRACK COUNT: %s' % len(self._tracks))
        for t in self._tracks:
            self.logger.write(' * %s (%s)' % (t.fingerprint, t.uid))
