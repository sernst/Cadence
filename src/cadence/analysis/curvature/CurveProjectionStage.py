# CurveProjectionStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.dict.DictUtils import DictUtils
from pyaid.list.ListUtils import ListUtils
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.svg.CadenceDrawing import CadenceDrawing

#*************************************************************************************************** CurveProjectionStage
class CurveProjectionStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    CURVE_MAP_FOLDER_NAME = 'Projection-Maps'

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of CurveProjectionStage."""
        super(CurveProjectionStage, self).__init__(
            key, owner,
            label='Curve Projection Stage',
            **kwargs)

        self._drawing = None
        self._paths = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: orderData
    @property
    def data(self):
        return self.cache.getOrAssign('data', {})

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
                '%s-%s-PROJECTION.svg' % (sitemap.name, sitemap.level),
                isFile=True),
            sitemap)

        self._drawing.grid()
        self._drawing.federalCoordinates()

        super(CurveProjectionStage, self)._analyzeSitemap(sitemap)

        self._drawing.save()
        self._drawing = None

#___________________________________________________________________________________________________ _analyzeTrackway
    def _analyzeTrackway(self, trackway, sitemap):

        analysisTrackway = trackway.getAnalysisPair(self.analysisSession)
        if not analysisTrackway or not analysisTrackway.curveSeries:
            return

        curveSeries = None
        series = self.owner.getTrackwaySeries(trackway)
        for key, value in DictUtils.iter(series):
            if value.firstTrackUid == analysisTrackway.curveSeries:
                curveSeries = value
                break

        if not curveSeries:
            return

        data = dict(
            trackway=trackway,
            analysisTrackway=analysisTrackway,
            curveSeries=curveSeries,
            segments=[])
        self.data[trackway.uid] = data

        segments = data['segments']
        tracks   = curveSeries.tracks

        for i in ListUtils.range(len(tracks) - 1):
            # Create a segment For each track in the reference series
            line = LineSegment2D(start=tracks[i].positionValue, end=tracks[i + 1].positionValue)
            if not line.isValid:
                self.logger.write([
                    '[ERROR]: Invalid curve series line segment',
                    'START: %s at %s | %s' % (
                        tracks[i].fingerprint,
                        tracks[i].positionValue.echo(True),
                        tracks[i].uid),
                    'END: %s at %s | %s' % (
                        tracks[i + 1].fingerprint,
                        tracks[i + 1].positionValue.echo(True),
                        tracks[i + 1].uid) ])
                continue

            segments.append({'track':tracks[i], 'line':line, 'pairs':[]})

        # Add segments to the beginning and end to handle overflow conditions where the paired
        # track series extend beyond the bounds of the reference series
        srcLine = segments[0]['line']
        segLine = srcLine.createPreviousLineSegment(10.0)
        segments.insert(0, { 'track':None, 'pairs':[], 'line':segLine })

        srcLine = segments[-1]['line']
        segLine = srcLine.createNextLineSegment(10.0)
        segments.append({'track':tracks[-1], 'pairs':[], 'line':segLine })

        super(CurveProjectionStage, self)._analyzeTrackway(trackway, sitemap)

        for segment in segments:
            self._drawSegment(segment, segments)

            # Sort the paired segments by distance from the segment start position to order them
            # properly from first to last
            if segment['pairs']:
                ListUtils.sortDictionaryList(segment['pairs'], 'distance', inPlace=True)

        # self._debugTrackway(trackway, segments)

#___________________________________________________________________________________________________ _drawSegment
    def _drawSegment(self, segment, segments):
        segLine = segment['line']
        edgeLineStyle = dict(stroke="#006666", stroke_width=1, stroke_opacity='0.25')
        lineStyles = [
            dict(stroke='#00CC00', stroke_width=1, stroke_opacity='0.25'),
            dict(stroke='#002200', stroke_width=1, stroke_opacity='0.25') ]

        index = segments.index(segment)

        if segment == segments[0] or segment == segments[-1]:
            styles = edgeLineStyle
        else:
            styles = lineStyles[1 if index & 1 else 0]

        self._drawing.line(segLine.start.toMayaTuple(), segLine.end.toMayaTuple(), **styles)

        self._drawing.circle(
            segLine.start.toMayaTuple(), 5,
            stroke='none', fill='#002200', fill_opacity='0.1')
        self._drawing.circle(
            segLine.end.toMayaTuple(), 5,
            stroke='none', fill='#002200', fill_opacity='0.1')

#___________________________________________________________________________________________________ _debugTrackway
    def _debugTrackway(self, trackway, segments):
        print('\nTRACKWAY[%s]:' % trackway.name)
        for segment in segments:
            print('  TRACK: %s' % (segment['track'].fingerprint if segment['track'] else 'NONE'))
            for item in segment['pairs']:
                print('    * %s (%s)' % (item['track'].fingerprint, item['distance'].label))
                for debugItem in item['debug']:
                    print('      - %s' % self._debugDrawTrackResults(debugItem))

#___________________________________________________________________________________________________ _debugDrawTrackResults
    def _debugDrawTrackResults(self, debugItem, verbose =False):
        if not verbose:
            return DictUtils.prettyPrint(debugItem['print'])

        data = debugItem['data']
        if False and 'testPoint' in data:
            self._drawing.circle(data['testPoint'].toMayaTuple(), 5,
            stroke='none', fill='black', fill_opacity='0.25')

        line = data.get('trackToTrack', data.get('testLine'))
        if line:
            self._drawing.line(
                line.start.toMayaTuple(), line.end.toMayaTuple(),
                stroke='red', stroke_width=1, stroke_opacity='0.33')
        elif 'matchLine' in data:
            line = data['matchLine']
            self._drawing.line(
                line.start.toMayaTuple(), line.end.toMayaTuple(),
                stroke='blue', stroke_width=1, stroke_opacity='0.5')

        return DictUtils.prettyPrint(debugItem['print'])

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        data = self.data[trackway.uid]
        if data['curveSeries'] == series:
            return

        super(CurveProjectionStage, self)._analyzeTrackSeries(series, trackway, sitemap)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        data         = self.data[trackway.uid]
        segments     = data['segments']
        debug        = []
        position     = track.positionValue
        segmentMatch = None
        pointOnLine  = None
        matchLine    = None

        self._drawing.circle(
            track.positionValue.toMayaTuple(), 5,
            stroke='none', fill='blue', fill_opacity='0.5')

        for segment in segments:
            segmentTrack = segment['track']
            segmentLine  = segment['line']
            debugItem    = {'TRACK':segmentTrack.fingerprint if segmentTrack else 'NONE'}
            debugData    = {}
            debug.append({'print':debugItem, 'data':debugData})

            # Make sure the track resides in a generally forward direction relative to
            # the direction of the segment. The prevents tracks from matching from behind.
            angle = segmentLine.angleBetweenPoint(position)
            if abs(angle.degrees) > 100.0:
                debugItem['CAUSE'] = 'Segment position angle [%s]' % angle.prettyPrint
                continue

            # Calculate the closest point on the line segment. If the point and line are not
            # properly coincident, the testPoint will be None and the attempt should be aborted.
            testPoint = segmentLine.closestPointOnLine(position, contained=True)
            if not testPoint:
                debugItem['CAUSE'] = 'Not aligned to segment'
                continue

            testLine = LineSegment2D(testPoint, position.clone())

            # Make sure the test line intersects the segment line at 90 degrees, or the
            # value is invalid.
            angle = testLine.angleBetweenPoint(segmentLine.end)
            if not NumericUtils.equivalent(angle.degrees, 90.0, 2.0):
                debugItem['CAUSE'] = 'Projection angle [%s]' % angle.prettyPrint
                debugData['testLine'] = testLine
                debugData['testPoint'] = testPoint
                continue

            # Skip if the test line length is greater than the existing test line
            if matchLine and testLine.length.value > matchLine.length.value:
                debugItem['CAUSE'] = 'Greater distance [%s > %s]' % (
                    matchLine.length.label, testLine.length.label)
                debugData['testLine'] = testLine
                debugData['testPoint'] = testPoint
                continue

            segmentMatch = segment
            pointOnLine  = testPoint.clone()
            pointOnLine.xUnc = position.xUnc
            pointOnLine.yUnc = position.yUnc
            matchLine    = LineSegment2D(pointOnLine.clone(), position.clone())
            debugData['matchLine'] = matchLine

        # If no segments match it means that the track resides at a kink in the curve series
        # curve and should be matched to a specific track instead of a segment
        if not segmentMatch:
            distanceTo = 1e10
            for segment in segments:
                line = segment['line']
                p = line.start.clone()
                d = p.distanceTo(position)
                if d.raw < distanceTo:
                    distanceTo = d.raw
                    segmentMatch = segment

            pointOnLine = segmentMatch['line'].start.clone()
            pointOnLine.xUnc = position.xUnc
            pointOnLine.yUnc = position.yUnc
            matchLine = LineSegment2D(pointOnLine.clone(), position.clone())

        self._drawing.line(
            matchLine.start.toMayaTuple(), matchLine.end.toMayaTuple(),
            stroke='black', stroke_width=1, stroke_opacity='1.0')
        self._drawing.circle(
            pointOnLine.toMayaTuple(), 5,
            stroke='none', fill='black', fill_opacity='1.0')

        distance = LineSegment2D(segmentMatch['line'].start, pointOnLine).length
        segmentMatch['pairs'].append({
            'track':track,
            'point':pointOnLine,
            'distance':distance,
            'debug':debug })

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        # self.mergePdfs(self._paths, 'Trackway-Curve-Stats.pdf')
