# RotationStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math
from pyaid.dict.DictUtils import DictUtils
from pyaid.number.Angle import Angle

from pyaid.number.NumericUtils import NumericUtils

from pyaid.string.StringUtils import StringUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.util.math2D.Vector2D import Vector2D

from cadence.svg.CadenceDrawing import CadenceDrawing


#*************************************************************************************************** RotationStage
class RotationStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of RotationStage."""
        super(RotationStage, self).__init__(
            key, owner,
            label='Rotation Comparison',
            **kwargs)

        self._paths = []
        self._diffs = []
        self._data  = []
        self._csv   = None
        self._currentDrawing = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        """_preAnalyze doc..."""
        self._diffs = []
        self._data  = []
        self._currentDrawing = None

        csv = CsvWriter()
        csv.path = self.getPath('Rotation-Report.csv', isFile=True)
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('delta', 'Difference'),
            ('entered', 'Entered'),
            ('measured', 'Measured'),
            ('deviation', 'Deviation (sigmas)'),
            ('relative', 'Relative'),
            ('axis', 'Axis'),
            ('axisPairing', 'Axis Pairing'))
        self._csv = csv

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):

        # start a drawing for the SVG and PDF files
        fileName = sitemap.name + "_" + sitemap.level + '_rotation.svg'
        path = self.getPath(fileName, isFile=True)
        self._currentDrawing = CadenceDrawing(path, sitemap)

        # create a group to be instanced for the map annotations
        self._currentDrawing.createGroup('pointer')
        self._currentDrawing.line((0, 0), (0, -10), scene=False, groupId='pointer')

        super(RotationStage, self)._analyzeSitemap(sitemap)

        if self._currentDrawing:
            self._currentDrawing.save()

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        # At least two tracks are required to make the comparison
        if len(series.tracks) < 2:
            return

        for track in series.tracks:
            fieldAngle = Angle(degrees=track.rotationMeasured)
            dataAngle  = Angle(degrees=track.rotation)
            pt = None
            nt = None

            if track == series.tracks[-1]:
                pt = series.tracks[-2]
            else:
                nt = series.tracks[series.tracks.index(track) + 1]

            # Z and X are swapped here for a 2D projection into a Right-Handed Coordinate system
            if nt:
                strideLine = Vector2D(nt.z - track.z, nt.x - track.x)
            else:
                strideLine = Vector2D(track.z - pt.z, track.x - pt.x)

            pair = nt if nt else pt
            if track.hidden or pair.hidden:
                continue

            try:
                strideLine.normalize()
            except ZeroDivisionError:
                self.logger.write([
                    '[ERROR]: Stride line was a zero length vector',
                    'TRACK: %s (%s, %s) [%s]' % (
                        track.fingerprint,
                        NumericUtils.roundToSigFigs(track.x, 3),
                        NumericUtils.roundToSigFigs(track.z, 3),
                        track.uid),
                    'PAIRING: %s (%s, %s) [%s]' % (
                        pair.fingerprint,
                        NumericUtils.roundToSigFigs(pair.x, 3),
                        NumericUtils.roundToSigFigs(pair.z, 3),
                        pair.uid) ])
                continue

            absoluteAxis = Vector2D(1, 0)
            absoluteAxis.normalize()

            axisAngle = absoluteAxis.angleBetween(strideLine)
            if track.left:
                fieldAngle.radians += axisAngle.radians
            else:
                fieldAngle.radians = axisAngle.radians - fieldAngle.radians

            # Adjust field angle into range [-180, 180]
            fieldAngle.constrainToRevolution()
            if fieldAngle.degrees > 180.0:
                fieldAngle.degrees -= 360.0

            fieldAngleUnc = Angle(degrees=5.0)
            fieldAngleUnc.radians += 0.03/math.sqrt(1 - math.pow(strideLine.x, 2))
            fieldDeg = NumericUtils.toValueUncertainty(fieldAngle.degrees, fieldAngleUnc.degrees)

            # Adjust data angle into range [-180, 180]
            dataAngle.constrainToRevolution()
            if dataAngle.degrees > 180.0:
                dataAngle.degrees -= 360.0

            dataAngleUnc = Angle(degrees=track.rotationUncertainty)
            dataDeg = NumericUtils.toValueUncertainty(dataAngle.degrees, dataAngleUnc.degrees)

            angle1 = Angle(degrees=dataDeg.value)
            angle2 = Angle(degrees=fieldDeg.value)

            diffDeg = NumericUtils.toValueUncertainty(
                angle1.differenceBetween(angle2).degrees,
                dataAngleUnc.degrees + fieldAngleUnc.degrees)

            self._diffs.append(diffDeg.value)

            deviation = diffDeg.value/diffDeg.uncertainty

            data = dict(
                uid=track.uid,
                fingerprint=track.fingerprint,
                entered=dataDeg.label,
                measured=fieldDeg.label,
                delta=NumericUtils.roundToOrder(diffDeg.value, -2),
                deviation=NumericUtils.roundToSigFigs(deviation, 3),
                relative=NumericUtils.roundToOrder(track.rotationMeasured, -2),
                axis=NumericUtils.roundToOrder(axisAngle.degrees, -2),
                axisPairing='PREV' if pt else 'NEXT')
            self._csv.createRow(**data)

            data['track'] = track
            self._data.append(data)

            # draw the stride line pointer for reference
            self._currentDrawing.use(
                'pointer',
                (track.x, track.z),
                scene=True,
                rotation=axisAngle.degrees,
                stroke_width=4,
                stroke='green')

            # draw this track indicating the map-derived estimate of rotation
            self._currentDrawing.use(
                'pointer',
                (track.x, track.z),
                scene=True,
                rotation=dataDeg.value,
                stroke_width=4,
                stroke='blue')

            # add the measured estimate of rotation, scaling by deviation
            self._currentDrawing.use(
                'pointer',
                (track.x, track.z),
                scene=True,
                rotation=fieldDeg.value,
                stroke_width=4,
                stroke='red')

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        self._csv.save()

        meanDiff = NumericUtils.getMeanAndDeviation(self._diffs)
        self.logger.write('Rotation %s' % meanDiff.label)

        self._paths.append(self._makePlot(
            label='Rotation Differences',
            data=self._diffs,
            histRange=[-180, 180]))

        self._paths.append(self._makePlot(
            label='Rotation Differences',
            data=self._diffs,
            histRange=[-180, 180],
            isLog=True))

        self.mergePdfs(self._paths)
        self._paths = []

#___________________________________________________________________________________________________ _makePlot
    def _makePlot(self, label, data, isLog =False, histRange =None, color ='r', binCount = 72):
        """_makePlot doc..."""

        pl = self.plot
        self.owner.createFigure('histogram')

        pl.hist(data, binCount, range=histRange, log=isLog, facecolor=color, alpha=0.75)
        pl.title('%s Distribution%s' % (label, ' (log)' if isLog else ''))
        pl.xlabel('Difference (Degrees)')
        pl.ylabel('Frequency')
        pl.grid(True)

        axis = pl.gca()
        xlims = axis.get_xlim()
        pl.xlim((max(histRange[0], xlims[0]), min(histRange[1], xlims[1])))

        path = self.getTempPath('%s.pdf' % StringUtils.getRandomString(16), isFile=True)
        self.owner.saveFigure('histogram', path)
        return path
