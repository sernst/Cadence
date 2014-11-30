# RotationStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math
from pyaid.number.NumericUtils import NumericUtils

from pyaid.string.StringUtils import StringUtils
from pyaid.time.TimeUtils import TimeUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.CsvWriter import CsvWriter
from cadence.util.math2D.Vector2D import Vector2D


#*************************************************************************************************** RotationStage
class RotationStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of RotationStage."""
        super(RotationStage, self).__init__(key, owner, **kwargs)
        self._paths = []
        self._diffs = []
        self._csv   = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        """_preAnalyze doc..."""
        self.logger.write('\n'.join([
            'ROTATION INTEGRITY ANALYSIS',
            'Run on %s' % TimeUtils.toZuluFormat().replace('T', ' at ') ]))

        self._diffs = []

        csv   = CsvWriter()
        csv.path = self.getPath('Rotation-Report.csv', isFile=True)
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('delta', 'Difference'),
            ('entered', 'Entered'),
            ('measured', 'Measured'),
            ('relative', 'Relative'),
            ('axis', 'Axis'),
            ('axisPairing', 'Axis Pairing'))
        self._csv = csv

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        # At least two tracks are required to make the
        if len(series.tracks) < 2:
            return

        for track in series.tracks:
            rm = math.pi/180.0*track.rotationMeasured

            pt = None
            nt = None

            if track == series.tracks[-1]:
                pt = series.tracks[-2]
            else:
                nt = series.tracks[series.tracks.index(track) + 1]

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

            absoluteAxis = Vector2D(0, 1)
            absoluteAxis.normalize()

            rAxis = strideLine.angleBetween(absoluteAxis)
            if track.left:
                rm = rAxis + rm
            else:
                rm = rAxis - rm

            rmDeg = 180.0/math.pi*rm

            diff = abs(track.rotation - rmDeg)
            self._diffs.append(diff)

            self._csv.createRow(
                uid=track.uid,
                fingerprint=track.fingerprint,
                entered=NumericUtils.roundToOrder(track.rotation, -2),
                measured=NumericUtils.roundToOrder(rmDeg, -2),
                delta=NumericUtils.roundToOrder(diff, -2),
                relative=NumericUtils.roundToOrder(track.rotationMeasured, -2),
                axis=NumericUtils.roundToOrder(180.0/math.pi*rAxis, -2),
                axisPairing='PREV' if pt else 'NEXT')

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        self._csv.save()

        self._paths.append(self._makePlot('Rotation', self._diffs, histRange=[0, 360]))
        self._paths.append(self._makePlot('Rotation', self._diffs, histRange=[0, 360], isLog=True))

        self.mergePdfs(self._paths)
        self._paths = []

#___________________________________________________________________________________________________ _makePlot
    def _makePlot(self, label, data, isLog =False, histRange =None, color ='r', binCount = 72):
        """_makePlot doc..."""

        pl = self.plot
        self.owner.createFigure('histogram')

        pl.hist(data, binCount, range=histRange, log=isLog, facecolor=color, alpha=0.75)
        pl.title('%s Distribution%s' % (label, ' (log)' if isLog else ''))
        pl.xlabel('Difference')
        pl.ylabel('Frequency')
        pl.grid(True)

        axis = pl.gca()
        xlims = axis.get_xlim()
        pl.xlim((max(histRange[0], xlims[0]), min(histRange[1], xlims[1])))

        path = self.getTempPath('%s.pdf' % StringUtils.getRandomString(16), isFile=True)
        self.owner.saveFigure('histogram', path)
        return path
