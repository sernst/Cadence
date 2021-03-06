# RotationStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from pyaid.number.Angle import Angle
from pyaid.number.NumericUtils import NumericUtils

from pyaid.string.StringUtils import StringUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.StrideLine import StrideLine
from cadence.analysis.shared.CsvWriter import CsvWriter

from cadence.svg.CadenceDrawing import CadenceDrawing


#*******************************************************************************
class RotationStage(AnalysisStage):
    """ Compares the rotational values from the field measurements, where they
        exist, with the measurements entered digitally determine the level of
        equivalence between the data sets.
    """

    DRAWING_FOLDER_NAME = 'Rotation-Comparison-Maps'

    #___________________________________________________________________________
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

    #===========================================================================
    #                                                             G E T / S E T

    #___________________________________________________________________________
    @property
    def deviations(self):
        return self.cache.get('trackDeviations')

    #===========================================================================
    #                                                         P R O T E C T E D

    #___________________________________________________________________________
    def _preAnalyze(self):
        """_preAnalyze doc..."""
        self.cache.set('trackDeviations', {})
        self._diffs = []
        self._data  = []
        self._currentDrawing = None

        csv = CsvWriter()
        csv.path = self.getPath('Rotation-Report.csv', isFile=True)
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('delta', 'Discrepancy'),
            ('entered', 'Entered'),
            ('measured', 'Measured'),
            ('deviation', 'Deviation'),
            ('relative', 'Relative'),
            ('axis', 'Axis'),
            ('axisPairing', 'Axis Pairing'))
        self._csv = csv

    #___________________________________________________________________________
    def _analyzeSitemap(self, sitemap):

        # start a drawing for the SVG and PDF files
        fileName = sitemap.name + "_" + sitemap.level + '_rotation.svg'
        path = self.getPath(self.DRAWING_FOLDER_NAME, fileName, isFile=True)
        self._currentDrawing = CadenceDrawing(path, sitemap)

        # create a group to be instanced for the map annotations
        self._currentDrawing.createGroup('pointer')
        self._currentDrawing.line(
            p1=(0, 0),
            p2=(0, -10),
            scene=False,
            groupId='pointer')

        # and place a grid and the federal coordinates in the drawing file
        self._currentDrawing.grid()
        self._currentDrawing.federalCoordinates()

        super(RotationStage, self)._analyzeSitemap(sitemap)

        if self._currentDrawing:
            self._currentDrawing.save()

    #___________________________________________________________________________
    def _analyzeTrackSeries(self, series, trackway, sitemap):

        if len(series.tracks) < 2:
            # At least two tracks are required to make the comparison
            return

        for track in series.tracks:
            fieldAngle = Angle(
                degrees=track.rotationMeasured \
                    if track.rotationMeasured \
                    else  0.0)
            dataAngle  = Angle(degrees=track.rotation)
            strideLine = StrideLine(track=track, series=series)

            if track.hidden or strideLine.pairTrack.hidden:
                continue

            try:
                strideLine.vector.normalize()
            except ZeroDivisionError:
                pair = strideLine.pairTrack
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

            axisAngle = strideLine.angle
            if track.left:
                fieldAngle.radians += axisAngle.radians
            else:
                fieldAngle.radians = axisAngle.radians - fieldAngle.radians

            # Adjust field angle into range [-180, 180]
            fieldAngle.constrainToRevolution()
            if fieldAngle.degrees > 180.0:
                fieldAngle.degrees -= 360.0

            fieldAngleUnc = Angle(degrees=5.0)
            fieldAngleUnc.radians += \
                0.03/math.sqrt(1.0 - math.pow(strideLine.vector.x, 2))
            fieldDeg = NumericUtils.toValueUncertainty(
                value=fieldAngle.degrees,
                uncertainty=fieldAngleUnc.degrees)

            # Adjust data angle into range [-180, 180]
            dataAngle.constrainToRevolution()
            if dataAngle.degrees > 180.0:
                dataAngle.degrees -= 360.0

            dataAngleUnc = Angle(degrees=track.rotationUncertainty)
            dataDeg = NumericUtils.toValueUncertainty(
                value=dataAngle.degrees,
                uncertainty=dataAngleUnc.degrees)

            angle1 = Angle(degrees=dataDeg.value)
            angle2 = Angle(degrees=fieldDeg.value)

            # fill color for the disks to be added to the map are based on
            # diffDeg
            diffDeg = NumericUtils.toValueUncertainty(
                value=angle1.differenceBetween(angle2).degrees,
                uncertainty=min(90.0, math.sqrt(
                    math.pow(dataAngleUnc.degrees, 2) +
                    math.pow(fieldAngleUnc.degrees, 2))) )

            self._diffs.append(diffDeg.value)

            deviation = diffDeg.value/diffDeg.uncertainty
            self.deviations[track.uid] = diffDeg

            # for now, convert +/- 180 headings to 0-360, using e and m
            # comment the next four lines toggle comments for entered and
            # measured below to revert
            e = dataDeg.value
            m = fieldDeg.value
            if e < 0.0:
                e += 360.0
            if m < 0.0:
                m += 360.0

            data = dict(
                uid=track.uid,
                fingerprint=track.fingerprint,
                entered=str(e),
                measured=str(m),
                delta=abs(diffDeg.value),
                deviation=deviation,
                relative=NumericUtils.roundToOrder(track.rotationMeasured, -2),
                axis=NumericUtils.roundToOrder(axisAngle.degrees, -2),
                axisPairing='NEXT' if strideLine.isNext else 'PREV')
            self._csv.createRow(**data)

            data['track'] = track
            self._data.append(data)

            # draw the stride line pointer for reference in green
            self._currentDrawing.use(
                'pointer',
                (track.x, track.z),
                scene=True,
                rotation=axisAngle.degrees,
                stroke_width=1,
                scale=0.5,
                stroke='green')

            # indicate in blue the map-derived estimate of track rotation
            self._currentDrawing.use(
                'pointer',
                (track.x, track.z),
                scene=True,
                rotation=dataDeg.value,
                stroke_width=1,
                stroke='blue')

            # add the measured (spreadsheet) estimate of rotation
            self._currentDrawing.use(
                'pointer',
                (track.x, track.z),
                scene=True,
                rotation=fieldDeg.value,
                stroke_width=1,
                stroke='red')

            # place a translucent disk of radius proportional to the difference
            # in degrees
            radius = 100.0*diffDeg.value/180.0
            self._currentDrawing.circle(
                (track.x, track.z),
                radius,
                scene=True,
                fill='red',
                stroke_width=0.5,
                stroke='red',
                fill_opacity='0.5')


#_______________________________________________________________________________
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

        circs    = []
        circsUnc = []
        diffs    = []
        diffsUnc = []
        entries  = self.owner.getStage('lengthWidth').entries

        for entry in entries:
            track = entry['track']
            if track.uid not in self.deviations:
                # Skip those tracks with no deviation value (solo tracks)
                continue

            diffDeg = self.deviations[track.uid]
            diffs.append(abs(diffDeg.value))
            diffsUnc.append(diffDeg.uncertainty)

            # Compute the circularity of the track from its aspect ratio. If
            # the aspect is less than or equal to 1.0 use the aspect value
            # directly. However, if the value is greater than one, take the
            # reciprocal so that large and small aspect ratios can be compared
            # equally.
            aspect = entry['aspect']
            if aspect.value > 1.0:
                a = 1.0/aspect.raw
                aspect = NumericUtils.toValueUncertainty(a, a*(aspect.rawUncertainty/aspect.raw))

            circs.append(abs(aspect.value - 1.0))
            circsUnc.append(aspect.uncertainty)

        pl = self.plot
        self.owner.createFigure('circular')
        pl.errorbar(x=circs, y=diffs, xerr=circsUnc, yerr=diffsUnc, fmt='.')
        pl.xlabel('Aspect Circularity')
        pl.ylabel('Rotation Deviation')
        pl.title('Rotation Deviation and Aspect Circularity')
        self._paths.append(self.owner.saveFigure('circular'))

        self.mergePdfs(self._paths)
        self._paths = []

#_______________________________________________________________________________
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
