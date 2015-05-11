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

    EXTENSION_LENGTH      = 10.0
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
            # Ignore trackways that are too short to have a curve series
            return

        # Fetch the curve series from the analysisTrackway.curveSeries value
        curveSeries = None
        series = self.owner.getTrackwaySeries(trackway)
        for key, value in DictUtils.iter(series):
            if value.firstTrackUid == analysisTrackway.curveSeries:
                curveSeries = value
                break

        if not curveSeries:
            # Abort if no curve series was found. This should only occur if the there's a data
            # corruption between the Tracks_Trackway table and the Analysis_Trackway.curveSeries
            # value.
            self.logger.write([
                '[ERROR]: No curve series found',
                'TRACKWAY[%s]: %s' % (trackway.index, trackway.name),
                'CURVE_SERIES: %s' % analysisTrackway.curveSeries])
            return

        trackwayData = self._generateTrackwaySegments(curveSeries, trackway, analysisTrackway)
        self.data[trackway.uid] = trackwayData
        super(CurveProjectionStage, self)._analyzeTrackway(trackway, sitemap)

        length = 0.0
        segments = trackwayData['segments']
        for segment in segments:
            self._drawSegment(segment, segments)
            length = max(length, segment['offset'])

            # Sort the paired segments by distance from the segment start position to order them
            # properly from first to last
            if segment['pairs']:
                ListUtils.sortDictionaryList(segment['pairs'], 'distance', inPlace=True)
                length = max(length, segment['pairs'][-1]['offset'])

        trackwayData['length'] = length
        analysisTrackway.curveLength = length

#___________________________________________________________________________________________________ _generateTrackwaySegments
    def _generateTrackwaySegments(self, curveSeries, trackway, analysisTrackway):
        segments = []
        tracks   = curveSeries.tracks
        output = dict(
            trackway=trackway,
            analysisTrackway=analysisTrackway,
            curveSeries=curveSeries,
            segments=segments)

        offset = 0.0
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

            segments.append(dict(index=i, track=tracks[i], line=line, pairs=[], offset=offset))
            offset += line.length.raw

        # Add segments to the beginning and end to handle overflow conditions where the paired
        # track series extend beyond the bounds of the reference series
        srcLine = segments[0]['line']
        segLine = srcLine.createPreviousLineSegment(self.EXTENSION_LENGTH)
        segments.insert(0, dict(
            index=-1,
            track=None,
            pairs=[],
            line=segLine,
            offset=-self.EXTENSION_LENGTH))

        srcLine = segments[-1]['line']
        segLine = srcLine.createNextLineSegment(self.EXTENSION_LENGTH)
        segments.append(dict(
            index=len(tracks) - 1,
            track=tracks[-1],
            pairs=[],
            line=segLine,
            offset=offset))

        return output

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):
        data = self.data[trackway.uid]
        if data['curveSeries'] == series:
            return

        super(CurveProjectionStage, self)._analyzeTrackSeries(series, trackway, sitemap)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """ Analyze the track by finding the segment on which it should be projected, along with
            the projection results data, and then drawing the projection to a sitemap drawing for
            reference. """

        result = self._findSegmentMatch(track, self.data[trackway.uid]['segments'])
        segment = result['segment']

        result['distance'] = LineSegment2D(segment['line'].start, result['point']).length
        result['offset'] = segment['offset'] + result['distance'].raw
        segment['pairs'].append(result)

        analysisTrack = track.getAnalysisPair(self.analysisSession, createIfMissing=True)
        analysisTrack.curveSegment = segment['index']
        analysisTrack.segmentPosition = result['distance'].raw
        analysisTrack.curvePosition = result['offset']

        self._drawing.line(
            result['line'].start.toMayaTuple(), result['line'].end.toMayaTuple(),
            stroke='black', stroke_width=1, stroke_opacity='1.0')

        self._drawing.circle(
            result['line'].end.toMayaTuple(), 5,
            stroke='none', fill='blue', fill_opacity='0.5')

        self._drawing.circle(
            result['line'].start.toMayaTuple(), 5,
            stroke='none', fill='black', fill_opacity='1.0')

#___________________________________________________________________________________________________ _findSegmentMatch
    @classmethod
    def _findSegmentMatch(cls, track, segments):
        position = track.positionValue
        data = {'track':track, 'debug':[]}

        for segment in segments:
            cls._testSegment(position, segment, data)

        if not data.get('segment'):
            # If no segments match it means that the track resides at a kink in the curve series
            # curve and should be matched to a specific track instead of a segment
            distanceTo = 1e10
            for segment in segments:
                line = segment['line']
                p = line.start.clone()
                d = p.distanceTo(position)
                if d.raw < distanceTo:
                    distanceTo = d.raw
                    data['segment'] = segment

            pointOnLine = data['segment']['line'].start.clone()
            pointOnLine.xUnc = position.xUnc
            pointOnLine.yUnc = position.yUnc
            data['point'] = pointOnLine

        data['line'] = LineSegment2D(data['point'].clone(), position.clone())
        return data

#___________________________________________________________________________________________________ _testSegment
    @classmethod
    def _testSegment(cls, position, segment, data):
        """ Tests the specified segment and modifies the data dictionary with the results of the
            test if it was successful. """

        segmentTrack = segment['track']
        segmentLine  = segment['line']

        debugItem    = {'TRACK':segmentTrack.fingerprint if segmentTrack else 'NONE'}
        debugData    = {}
        data['debug'].append({'print':debugItem, 'data':debugData})

        # Make sure the track resides in a generally forward direction relative to
        # the direction of the segment. The prevents tracks from matching from behind.
        angle = segmentLine.angleBetweenPoint(position)
        if abs(angle.degrees) > 100.0:
            debugItem['CAUSE'] = 'Segment position angle [%s]' % angle.prettyPrint
            return

        # Calculate the closest point on the line segment. If the point and line are not
        # properly coincident, the testPoint will be None and the attempt should be aborted.
        testPoint = segmentLine.closestPointOnLine(position, contained=True)
        if not testPoint:
            debugItem['CAUSE'] = 'Not aligned to segment'
            return

        testLine = LineSegment2D(testPoint, position.clone())

        # Make sure the test line intersects the segment line at 90 degrees, or the
        # value is invalid.
        angle = testLine.angleBetweenPoint(segmentLine.end)
        if not NumericUtils.equivalent(angle.degrees, 90.0, 2.0):
            debugItem['CAUSE'] = 'Projection angle [%s]' % angle.prettyPrint
            debugData['testLine'] = testLine
            debugData['testPoint'] = testPoint
            return

        # Skip if the test line length is greater than the existing test line
        matchLine = data.get('line')
        if matchLine and testLine.length.value > matchLine.length.value:
            debugItem['CAUSE'] = 'Greater distance [%s > %s]' % (
                matchLine.length.label, testLine.length.label)
            debugData['testLine'] = testLine
            debugData['testPoint'] = testPoint
            return

        p  = testPoint.clone()
        p.xUnc = position.xUnc
        p.yUnc = position.yUnc
        data['point'] = p
        data['segment'] = segment

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        # self.mergePdfs(self._paths, 'Trackway-Curve-Stats.pdf')

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
    @classmethod
    def _debugTrackway(cls, trackway, segments):
        print('\nTRACKWAY[%s]:' % trackway.name)
        for segment in segments:
            print('  TRACK: %s' % (segment['track'].fingerprint if segment['track'] else 'NONE'))
            for item in segment['pairs']:
                print('    * %s (%s)' % (item['track'].fingerprint, item['distance'].label))
                for debugItem in item['debug']:
                    print('      - %s' % DictUtils.prettyPrint(debugItem['print']))
