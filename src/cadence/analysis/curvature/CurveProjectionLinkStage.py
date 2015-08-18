# CurveProjectionLinkStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.list.ListUtils import ListUtils
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.analysis.shared.PositionValue2D import PositionValue2D
from cadence.analysis.shared.plotting.ScatterPlot import ScatterPlot


#*************************************************************************************************** CurveProjectionLinkStage
class CurveProjectionLinkStage(AnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    EXTENSION_LENGTH      = 10.0
    CURVE_MAP_FOLDER_NAME = 'Projection-Linkage-Maps'

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of CurveProjectionLinkStage."""
        super(CurveProjectionLinkStage, self).__init__(
            key, owner,
            label='Curve Projection Linking',
            **kwargs)

        self._paths = []

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _preAnalyze(self):
        self._paths = []

#_______________________________________________________________________________
    def _analyzeSitemap(self, sitemap):
        """_analyzeSitemap doc..."""

        self._createDrawing(sitemap, 'LINKAGES', self.CURVE_MAP_FOLDER_NAME)
        super(CurveProjectionLinkStage, self)._analyzeSitemap(sitemap)
        self._saveDrawing(sitemap)

#_______________________________________________________________________________
    def _analyzeTrackway(self, trackway, sitemap):

        seriesBundle = self.owner.getSeriesBundle(trackway)

        analysisTrackway = trackway.getAnalysisPair(self.analysisSession)
        if not analysisTrackway or not analysisTrackway.curveSeries:
            # Ignore trackways that are too short to have a curve series
            self.logger.write('SKIPPED[%s]: %s' % (trackway.name, seriesBundle.echoStatus()))
            return

        curveSeries = None
        for value in seriesBundle.asList():
            if value.firstTrackUid == analysisTrackway.curveSeries:
                curveSeries = value
                break

        if curveSeries is None:
            self.logger.write([
                '[ERROR]: No curve series found',
                'TRACKWAY: %s' % trackway.name,
                'FIRST_CURVE_TRACK: %s' % analysisTrackway.curveSeries,
                'BUNDLE STATUS: %s' % seriesBundle.echoStatus(),
                'BUNDLE START UIDS: %s' % seriesBundle.echoStartUids()])
            return

        drawing = sitemap.cache.get('drawing')

        # Draw the curve series
        self._drawCurveSeries(drawing, curveSeries)

        # Draw a path connecting each track in the trackway in the order they appear in the curve
        # series projection
        track = self._getNextTrack(None, trackway)
        line = None

        tracks = []
        curveIndex = 0
        while track is not None:
            tracks.append(track)
            nextTrack = self._getNextTrack(track, trackway)
            at = track.analysisPair
            if not nextTrack:
                at.nextCurveTrack = ''
                self._drawLine(drawing, line, opacity=0.25, startCap=False, connect=False)
                break

            at.nextCurveTrack = nextTrack.uid
            at.curveIndex = curveIndex
            curveIndex += 1

            line = LineSegment2D(track.positionValue, nextTrack.positionValue)
            self._drawLine(
                drawing, line,
                color='black' if curveIndex & 1 else 'blue',
                opacity=0.25, endCap=False)

            track = nextTrack

        self._plotTracks(tracks, trackway)

#_______________________________________________________________________________
    def _getNextTrack(self, track, trackway):
        """ Iterates through all the tracks in the trackway and finds the track closest to the
            specified track. If the track argument is None the first track in the trackway will
            be returned. """

        bundle = self.owner.getSeriesBundle(trackway)
        trackPosition = -1.0e8
        targetPosition = 1.0e8
        nextTrack = None
        analysisTrack = None

        if track:
            analysisTrack = track.getAnalysisPair(self.analysisSession)
            trackPosition = analysisTrack.curvePosition

        for value in bundle.asList():
            for t in value.tracks:
                if track and t == track:
                    continue

                at = t.getAnalysisPair(self.analysisSession)
                if  at.curvePosition < trackPosition:
                    continue

                if NumericUtils.equivalent(at.curvePosition, targetPosition):
                    log = [
                        '[ERROR]: Found multiple tracks at the same curve location',
                        'TARGET: %s' % NumericUtils.roundToSigFigs(targetPosition, 5),
                        'TEST: %s [%s]' % (t.fingerprint, t.uid),
                        'LOCATION[TEST]: %s (%s)' % (
                            NumericUtils.roundToSigFigs(at.curvePosition, 5),
                            NumericUtils.roundToSigFigs(at.segmentPosition, 5) )]

                    if nextTrack:
                        nat = nextTrack.getAnalysisPair(self.analysisSession)
                        log.append('COMPARE: %s [%s]' % (nextTrack.fingerprint, nextTrack.uid) )
                        log.append('LOCATION[COMP]: %s (%s)' % (
                            NumericUtils.roundToSigFigs(nat.curvePosition, 5),
                            NumericUtils.roundToSigFigs(nat.segmentPosition, 5) ))

                    if track:
                        log.append('TRACK: %s [%s]' % (track.fingerprint, track.uid))
                        log.append('LOCATION[TRACK]: %s (%s)' % (
                            NumericUtils.roundToSigFigs(analysisTrack.curvePosition, 5),
                            NumericUtils.roundToSigFigs(analysisTrack.segmentPosition, 5) ))

                    self.logger.write(log)
                    raise ValueError('Found multiple tracks at the same curve location')

                if at.curvePosition < targetPosition:
                    nextTrack = t
                    targetPosition = at.curvePosition
                else:
                    break

        return nextTrack

#_______________________________________________________________________________
    def _plotTracks(self, tracks, trackway):
        """_plotTracks doc..."""

        points = []
        labels = []
        for t in tracks:
            at = t.getAnalysisPair(self.analysisSession)
            if t.pes:
                signal = 1 if t.left else 2
            else:
                signal = 3 if t.left else 4
            p = PositionValue2D(x=at.curvePosition, y=signal)
            points.append(p)
            labels.append(t.shortFingerprint)

        plot = ScatterPlot(
            data=points,
            title='%s Trackway Ordering' % trackway.name,
            xLabel='Trackway Curve Position (m)',
            yLabel='Classification',
            yLimits=[0, 5],
            yTickFunc=self._plotLabelChannelsFunc)
        self._paths.append(plot.save(self.getTempFilePath(extension='pdf')))

#_______________________________________________________________________________
    @classmethod
    def _plotLabelChannelsFunc(cls, value, position):
        if value == 1:
            return 'LP'
        elif value == 2:
            return 'RP'
        elif value == 3:
            return 'LM'
        elif value == 4:
            return 'RM'
        else:
            return ''

#_______________________________________________________________________________
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

#_______________________________________________________________________________
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

#_______________________________________________________________________________
    def _postAnalyze(self):
        self.mergePdfs(self._paths, 'Trackway-Ordering.pdf')
