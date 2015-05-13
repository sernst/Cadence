# CurveProjectionLinkStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.dict.DictUtils import DictUtils
from pyaid.list.ListUtils import ListUtils
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.svg.CadenceDrawing import CadenceDrawing

#*************************************************************************************************** CurveProjectionLinkStage
class CurveProjectionLinkStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    EXTENSION_LENGTH      = 10.0
    CURVE_MAP_FOLDER_NAME = 'Projection-Linkage-Maps'

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of CurveProjectionLinkStage."""
        super(CurveProjectionLinkStage, self).__init__(
            key, owner,
            label='Curve Projection Linking',
            **kwargs)

        self._drawing = None
        self._paths = []

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._drawing = None
        self._paths = []

        self.initializeFolder(self.CURVE_MAP_FOLDER_NAME)

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        """_analyzeSitemap doc..."""

        self._drawing = CadenceDrawing(
            self.getPath(
                self.CURVE_MAP_FOLDER_NAME,
                '%s-%s-LINKAGES.svg' % (sitemap.name, sitemap.level),
                isFile=True),
            sitemap)

        self._drawing.grid()
        self._drawing.federalCoordinates()

        super(CurveProjectionLinkStage, self)._analyzeSitemap(sitemap)

        self._drawing.save()
        self._drawing = None

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):

        analysisTrackway = trackway.getAnalysisPair(self.analysisSession)
        if not analysisTrackway or not analysisTrackway.curveSeries:
            # Ignore trackways that are too short to have a curve series
            return

        trackwaySeries = self.owner.getTrackwaySeries(trackway)

        curveSeries = None
        for key, value in DictUtils.iter(trackwaySeries):
            if value.firstTrackUid == analysisTrackway.curveSeries:
                curveSeries = value
                break

        # Draw the curve series
        self._drawCurveSeries(self._drawing, curveSeries)

        # Draw a path connecting each track in the trackway in the order they appear in the curve
        # series projection
        track = self._getNextTrack(None, trackway)
        line = None

        curveIndex = 0
        while track is not None:
            nextTrack = self._getNextTrack(track, trackway)
            at = track.analysisPair
            if not nextTrack:
                at.nextCurveTrack = ''
                self._drawLine(self._drawing, line, opacity=0.25, startCap=False, connect=False)
                break

            at.nextCurveTrack = nextTrack.uid
            at.curveIndex = curveIndex
            curveIndex += 1

            line = LineSegment2D(track.positionValue, nextTrack.positionValue)
            self._drawLine(
                self._drawing, line,
                color='black' if curveIndex & 1 else 'blue',
                opacity=0.25, endCap=False)

            track = nextTrack

#___________________________________________________________________________________________________ _getNextTrack
    def _getNextTrack(self, track, trackway):
        """ Iterates through all the tracks in the trackway and finds the track closest to the
            specified track. If the track argument is None the first track in the trackway will
            be returned. """

        trackwaySeries = self.owner.getTrackwaySeries(trackway)
        trackPosition = -1.0e8
        targetPosition = 1.0e8
        nextTrack = None

        if track:
            analysisTrack = track.getAnalysisPair(self.analysisSession)
            trackPosition = analysisTrack.curvePosition

        for key, value in DictUtils.iter(trackwaySeries):
            for t in value.tracks:
                if track and t == track:
                    continue

                at = t.getAnalysisPair(self.analysisSession)
                if  at.curvePosition < trackPosition:
                    continue

                if NumericUtils.equivalent(at.curvePosition, targetPosition):
                    self.logger.write([
                        '[ERROR]: Found multiple tracks at the same curve location',
                        'LOCATION: %s' % NumericUtils.roundToSigFigs(at.curvePosition, 4),
                        'TRACK: %s [%s]' % (track.fingerprint, track.uid),
                        'NEXT: %s [%s]' % (t.fingerprint, t.uid) ])
                    raise ValueError, 'Found multiple tracks at the same curve location'

                if at.curvePosition < targetPosition:
                    nextTrack = t
                    targetPosition = at.curvePosition
                else:
                    break

        return nextTrack

#___________________________________________________________________________________________________ _drawCurveSeries
    @classmethod
    def _drawCurveSeries(cls, drawing, series):
        """_drawCurveSeries doc..."""

        line = None
        for i in ListUtils.rangeOn(series.tracks):
            track = series.tracks[i]

            try:
                nextTrack = series.tracks[i + 1]
            except Exception:
                cls._drawLine(
                    drawing=drawing, line=line,
                    color='#009900', opacity=0.1,
                    startCap=False, connect=False)
                return

            line = LineSegment2D(track.positionValue, nextTrack.positionValue)
            cls._drawLine(drawing=drawing, line=line, color='#009900', opacity=0.1, endCap=False)

#___________________________________________________________________________________________________ _drawPaceLine
    @classmethod
    def _drawLine(
            cls, drawing, line, color ='black', opacity=1.0, endCap =True, startCap=True,
            connect =True
    ):
        """_drawPaceLine doc..."""

        if not line:
            return

        if connect:
            drawing.line(
                line.start.toMayaTuple(), line.end.toMayaTuple(),
                stroke=color, stroke_width=1, stroke_opacity=opacity)

        if endCap:
            drawing.circle(
                line.end.toMayaTuple(), 5, stroke='none', fill=color, fill_opacity=opacity)

        if startCap:
            drawing.circle(
                line.start.toMayaTuple(), 5, stroke='none', fill=color, fill_opacity=opacity)

