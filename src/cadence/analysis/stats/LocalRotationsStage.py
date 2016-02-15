# LocalRotationsStage.py
# (C)2015
# Scott Ernst

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyaid.file.CsvWriter import CsvWriter
from pyaid.number.Angle import Angle
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.enums.ImportFlagsEnum import ImportFlagsEnum


class LocalRotationsStage(CurveOrderedAnalysisStage):
    """A class for..."""

    #___________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of LocalRotationsStage."""
        super(LocalRotationsStage, self).__init__(
            key, owner, label='Local Rotation', **kwargs)

        self._csv = None


    #___________________________________________________________________________
    def _preAnalyze(self):
        self._csv = CsvWriter(
            path=self.getPath('Local_Rotations.csv'),
            autoIndexFieldName='index',
            fields=[
                ('uid', 'UID'),
                ('fingerprint', 'Fingerprint'),
                ('localRotation', 'Local Rotation'),
                ('measuredRotation', 'Measured Rotation'),
                ('difference', 'Difference'),
                ('deviation', 'Deviation')
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


            if not prev_track.left:
                local_angle = stride_angle.differenceBetween(abs_angle)
            else:
                local_angle = abs_angle.differenceBetween(stride_angle)

            has_field_measurements = not prev_track.hasImportFlag(
                ImportFlagsEnum.NO_FIELD_MEASUREMENTS
            )

            if has_field_measurements:
                measuredRotation = prev_track.rotationMeasured
                difference = round(abs(measuredRotation - local_angle.degrees))
                deviation = NumericUtils.roundToOrder(
                    value=difference/prev_track.rotationUncertainty,
                    orderOfMagnitude=-2)
            else:
                measuredRotation = ''
                difference = ''
                deviation = ''

            self._csv.createRow(
                uid=prev_track.uid,
                fingerprint=prev_track.fingerprint,
                difference=difference,
                deviation=deviation,
                localRotation=round(local_angle.degrees),
                measuredRotation=measuredRotation)
            prev_track = track

    #___________________________________________________________________________
    def _postAnalyze(self):
        self._csv.save()
        self._csv = None
