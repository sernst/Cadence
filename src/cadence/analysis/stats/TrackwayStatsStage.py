# TrackwayStatsStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

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
            ('length', 'Length') )
        self._csv = csv

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):
        pass

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        self.logger.write('TRACKWAY COUNT: %s' % len(self._trackways))

