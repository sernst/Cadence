# TrackPriorityStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.enums.TrackCsvColumnEnum import TrackCsvColumnEnum

#*************************************************************************************************** TrackPriorityStage
class TrackPriorityStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackPriorityStage."""
        super(TrackPriorityStage, self).__init__(
            key, owner,
            label='Track Priority Report',
            **kwargs)

        self._tracks = []
        self._csv = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._tracks = []

        csv = CsvWriter()
        csv.path = self.getPath('Track-Priority.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('priority', 'Priority'),
            ('preserved', 'Preserved'),
            ('cast', 'Cast'),
            ('outlined', 'Outlined') )
        self._csv = csv

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):

        snapshot = track.snapshot
        isPreserved = TrackCsvColumnEnum.PRESERVED.name in snapshot
        isCast = TrackCsvColumnEnum.CAST.name in snapshot
        isOutlined = TrackCsvColumnEnum.OUTLINE_DRAWING.name in snapshot

        bundle = series.bundle
        trackwayTrackCount = bundle.count

        self._csv.createRow(
            uid=track.uid,
            fingerprint=track.fingerprint,
            priority=trackwayTrackCount,
            preserved=1 if isPreserved else 0,
            cast=1 if isCast else 0,
            outlined=1 if isOutlined else 0)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        self._csv.save()

