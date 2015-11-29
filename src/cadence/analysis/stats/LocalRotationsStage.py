# LocalRotationsStage.py
# (C)2015
# Scott Ernst

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyaid.file.CsvWriter import CsvWriter
from pyaid.number.Angle import Angle

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.shared.LineSegment2D import LineSegment2D


class LocalRotationsStage(CurveOrderedAnalysisStage):
    """A class for..."""

    #___________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of LocalRotationsStage."""
        super(LocalRotationsStage, self).__init__(
            key, owner, label='Local Rotation', **kwargs)

        self._csv = None


    #_______________________________________________________________________________
    def _preAnalyze(self):
        self._csv = CsvWriter(
            path=self.getPath('Local_Rotations.csv'),
            autoIndexFieldName='index',
            fields=[
                ('uid', 'UID'),
                ('localRotation', 'Local Rotation')
            ]
        )

    #___________________________________________________________________________
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        if len(series.tracks) < 2:
            return

        prev_track = series.tracks[0]
        for track in series.tracks[1:]:
            stride_line = LineSegment2D(
                start=prev_track.positionValue,
                end=track.positionValue)

            stride_angle = stride_line.angle
            abs_angle = Angle(degrees=prev_track.rotation)


            if prev_track.left:
                local_angle = stride_angle.differenceBetween(abs_angle)
            else:
                local_angle = abs_angle.differenceBetween(stride_angle)

            self._csv.createRow(
                uid=prev_track.uid,
                localRotation=local_angle.degrees)
            prev_track = track

    #___________________________________________________________________________
    def _postAnalyze(self):
        self._csv.save()
        self._csv = None
