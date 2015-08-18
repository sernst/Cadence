# CurveSeries.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.dict.DictUtils import DictUtils

from pyaid.list.ListUtils import ListUtils
from pyaid.number.NumericUtils import NumericUtils
from cadence.analysis.curvature.CurveProjectionSegment import CurveProjectionSegment
from cadence.analysis.shared.LineSegment2D import LineSegment2D

#*************************************************************************************************** CurveSeries
class CurveSeries(object):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    EXTENSION_LENGTH = 10.0

#_______________________________________________________________________________
    def __init__(self, stage, series, **kwargs):
        """Creates a new instance of CurveSeries."""

        self.saveToAnalysisTracks = kwargs.get('saveToAnalysisTracks', False)

        self._series = series
        self._stage = stage
        self._analysisTrackway = kwargs.get('analysisTrackway')

        self._populated = False
        self._length = 0.0
        self._errors = []
        self._segments = []

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def segments(self):
        return self._segments

#_______________________________________________________________________________
    @property
    def bundle(self):
        return self.series.bundle

#_______________________________________________________________________________
    @property
    def series(self):
        return self._series

#_______________________________________________________________________________
    @property
    def trackway(self):
        return self.bundle.trackway

#_______________________________________________________________________________
    @property
    def stage(self):
        return self._stage

#_______________________________________________________________________________
    @property
    def analysisTrackway(self):
        if not self._analysisTrackway:
            self._analysisTrackway = self.trackway.getAnalysisPair(self.stage.analysisSession)
        return self._analysisTrackway

#_______________________________________________________________________________
    @property
    def length(self):
        return self._length
    @length.setter
    def length(self, value):
        self._length = value
        if self.saveToAnalysisTracks:
            self.analysisTrackway.curveLength = value

#_______________________________________________________________________________
    @property
    def errors(self):
        return self._errors

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def getTrackSegment(self, track):
        """ Finds the segment in which the specified track resides and returns that segment or
            None if no such segment was found.

            @return CurveProjectionSegment """

        for segment in self._segments:
            if track == segment.track:
                return segment

            for pair in segment.pairs:
                if pair['track'] == track:
                    return segment
        return None

#_______________________________________________________________________________
    def compute(self):
        """load doc..."""

        if self._populated:
            return True
        self._populated = True

        self._generateSegments()
        self._populate()
        self._process()

#_______________________________________________________________________________
    def draw(self, drawing, **kwargs):
        """draw doc..."""

        for segment in self.segments:
            segment.draw(drawing, **kwargs)

#_______________________________________________________________________________
    def getDebugReport(self):
        out = ['\nTRACKWAY[%s]:' % self.trackway.name]
        for segment in self.segments:
            out.append(
                '  TRACK: %s' % (segment.track.fingerprint if segment.track else 'NONE'))

            for item in segment.pairs:
                out.append(
                    '    * %s (%s)' % (
                        item['track'].fingerprint,
                        NumericUtils.roundToSigFigs(item['distance'], 5) ))
                for debugItem in item['debug']:
                    out.append('      - %s' % DictUtils.prettyPrint(debugItem['print']))

        return '\n'.join(out)

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _generateSegments(self):
        """_generateSegments doc..."""

        segments = self.segments
        tracks = self.series.tracks
        offset = 0.0

        for i in ListUtils.range(len(tracks) - 1):
            # Create a segment For each track in the reference series

            line = LineSegment2D(start=tracks[i].positionValue, end=tracks[i + 1].positionValue)
            if not line.isValid:
                self._errors.append([
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

            if self.saveToAnalysisTracks:
                # Populate analysis track data for curve series tracks
                analysisTrack = tracks[i].getAnalysisPair(
                    self.stage.analysisSession, createIfMissing=True)
                analysisTrack.curveSegment = len(segments)
                analysisTrack.segmentPosition = 0.0
                analysisTrack.curvePosition = offset

            s = CurveProjectionSegment(
                index=i + 1,
                track=tracks[i],
                line=line,
                offset=offset)
            segments.append(s)

            offset += line.length.raw

        # Add segments to the beginning and end to handle overflow conditions where the paired
        # track series extend beyond the bounds of the reference series
        srcLine = segments[0].line
        segLine = srcLine.createPreviousLineSegment(self.EXTENSION_LENGTH)
        s = CurveProjectionSegment(
            index=0,
            track=None,
            line=segLine,
            offset=-self.EXTENSION_LENGTH)
        segments.insert(0, s)

        track = tracks[-1]
        if self.saveToAnalysisTracks:
            analysisTrack = track.getAnalysisPair(self.stage.analysisSession, createIfMissing=True)
            analysisTrack.curveSegment = len(tracks) - 1
            analysisTrack.segmentPosition = 0.0
            analysisTrack.curvePosition = offset

        srcLine = segments[-1].line
        segLine = srcLine.createNextLineSegment(self.EXTENSION_LENGTH)
        s = CurveProjectionSegment(
            index=-1,
            track=track,
            line=segLine,
            offset=offset)
        segments.append(s)

#_______________________________________________________________________________
    def _populate(self):
        for series in self.bundle.asList():
            if self.series == series:
                continue

            for track in series.tracks:
                self._analyzeTrack(track)

#_______________________________________________________________________________
    def _analyzeTrack(self, track):
        """ Analyze the track by finding the segment on which it should be projected, along with
            the projection results data, and then drawing the projection to a sitemap drawing for
            reference. """

        result = self._findSegmentMatch(track, self.segments)
        segment = result['segment']
        segment.pairs.append(result)

        if not self.saveToAnalysisTracks:
            return

        analysisTrack = track.getAnalysisPair(self.stage.analysisSession, createIfMissing=True)
        analysisTrack.curveSegment = segment.index
        analysisTrack.segmentPosition = result['distance']
        analysisTrack.curvePosition = segment.offset + result['distance']

#_______________________________________________________________________________
    def _process(self):
        """_process doc..."""
        length = 0.0
        for segment in self.segments:
            length = max(length, segment.offset)

            # Sort the paired segments by distance from the segment start position to order them
            # properly from first to last
            if segment.pairs:
                ListUtils.sortDictionaryList(segment.pairs, 'distance', inPlace=True)

                for p in segment.pairs:
                    self._resolveSpatialCoincidences(p)

                length = max(length, segment.offset + segment.pairs[-1]['distance'])

        self.length = length

#_______________________________________________________________________________
    def _resolveSpatialCoincidences(self, pair):
        """ Correct for cases where projected prints reside at the same spatial location on the
            curve series by adjusting one of the tracks projection position slightly. """

        segment = pair['segment']

        try:
            nextSegment = self.segments[self.segments.index(segment) + 1]
            nextOffset = nextSegment.offset
        except Exception:
            nextOffset = 1.0e8

        # Adjust a pair print if it resides at the same position as its curve series track
        if NumericUtils.equivalent(pair['distance'], 0.0):
            self._adjustPositionForward(pair, nextOffset)

        try:
            # Retrieve the next pair track in the segment if one exists
            nextPair = segment.pairs[segment.pairs.index(pair) + 1]
        except Exception:
            return

        pDist = pair['distance']
        npDist = nextPair['distance']

        # Adjust pair tracks that reside at the same spatial position
        if npDist <= pDist or NumericUtils.equivalent(pDist, npDist):
            self._adjustPositionForward(nextPair, nextOffset)

#_______________________________________________________________________________
    def _adjustPositionForward(self, pair, maxOffset =1.0e8):
        """_adjustPositionForward doc..."""

        delta = 0.001
        segment = pair['segment']
        offset = segment.offset + pair['distance']

        while maxOffset <= (offset + delta) or NumericUtils.equivalent(maxOffset, offset + delta):
            delta *= 0.5

        point = pair['line'].start.clone()
        segment.line.adjustPointAlongLine(point, delta, inPlace=True)
        dist = segment.line.start.distanceTo(point).raw

        if not NumericUtils.equivalent(pair['distance'] + delta, dist, machineEpsilonFactor=1000.0):
            self.stage.logger.write([
                '[ERROR]: Forward adjust failure in CurveSeries.adjustPositionForward',
                'TRACK: %s [%s]' % (pair['track'].fingerprint, pair['track'].uid),
                'EXPECTED: %s' % (pair['distance'] + delta),
                'ACTUAL: %s' % dist,
                'DELTA: %s' % delta])

        pair['line'].start.copyFrom(point)

        track = pair['track']
        pair['distance'] = dist

        if not self.saveToAnalysisTracks:
            return

        at = track.getAnalysisPair(self.stage.analysisSession)
        at.curvePosition = segment.offset + dist
        at.segmentPosition = dist

#_______________________________________________________________________________
    @classmethod
    def _findSegmentMatch(cls, track, segments):
        position = track.positionValue
        pair = dict(track=track)

        for segment in segments:
            # Attempt to project the track position onto each of the available segments. The data
            # dictionary is updated if the projection was successful
            segment.project(track, pair)

        if not pair.get('segment'):
            # If no segments projections were successful, the track resides at a kink in the curve
            # series curve and should be matched to a specific track instead of a segment
            distanceTo = 1e10
            for segment in segments:
                line = segment.line
                p = line.start.clone()
                d = p.distanceTo(position)
                if d.raw < distanceTo:
                    distanceTo = d.raw
                    pair['segment'] = segment

            p = pair['segment'].line.start.clone()
            p.update(xUnc=position.xUnc, yUnc=position.yUnc)
            pair['line'] = LineSegment2D(p, position)
            pair['distance'] = 0.0

        return pair

#===============================================================================
#                                                                               I N T R I N S I C

#_______________________________________________________________________________
    def __repr__(self):
        return self.__str__()

#_______________________________________________________________________________
    def __str__(self):
        return '<%s>' % self.__class__.__name__

