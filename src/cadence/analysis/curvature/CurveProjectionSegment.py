# CurveProjectionSegment.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.ArgsUtils import ArgsUtils
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.shared.LineSegment2D import LineSegment2D


#*************************************************************************************************** CurveProjectionSegment
class CurveProjectionSegment(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of CurveProjectionSegment."""
        self.index = kwargs.get('index', -2)
        self.track = kwargs.get('track')
        self.line  = kwargs.get('line')
        self.offset = kwargs.get('offset')
        self.pairs = []

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ project
    def project(self, track, data =None):
        """ Tests the specified segment and modifies the data dictionary with the results of the
            test if it was successful. """

        data = self._initializeData(data, track)

        position = track.positionValue
        debugItem = {'TRACK':self.track.fingerprint if self.track else 'NONE'}
        debugData = {}
        data['debug'].append({'print':debugItem, 'data':debugData})

        # Make sure the track resides in a generally forward direction relative to
        # the direction of the segment. The prevents tracks from matching from behind.
        angle = self.line.angleBetweenPoint(position)
        if abs(angle.degrees) > 100.0:
            debugItem['CAUSE'] = 'Segment position angle [%s]' % angle.prettyPrint
            return

        # Calculate the closest point on the line segment. If the point and line are not
        # properly coincident, the testPoint will be None and the attempt should be aborted.
        testPoint = self.line.closestPointOnLine(position, contained=True)
        if not testPoint:
            debugItem['CAUSE'] = 'Not aligned to segment'
            return

        testLine = LineSegment2D(testPoint, position.clone())

        # Make sure the test line intersects the segment line at 90 degrees, or the
        # value is invalid.
        angle = testLine.angleBetweenPoint(self.line.end)
        if not NumericUtils.equivalent(angle.degrees, 90.0, 2.0):
            debugItem['CAUSE'] = 'Projection angle [%s]' % angle.prettyPrint
            debugData['testLine'] = testLine
            debugData['testPoint'] = testPoint
            return

        # Skip if the test line length is greater than the existing test line
        length = data.get('projectionLength', 1.0e10)
        if testLine.length.raw > length:
            debugItem['CAUSE'] = 'Greater length [%s > %s]' % (
                NumericUtils.roundToSigFigs(length, 5),
                NumericUtils.roundToSigFigs(testLine.length.raw, 5) )
            debugData['testLine'] = testLine
            debugData['testPoint'] = testPoint
            return

        # Populate the projection values if the projection was successful
        p  = testPoint.clone()
        p.xUnc = position.xUnc
        p.yUnc = position.yUnc
        data['segment'] = self
        data['projectionLength'] = position.distanceTo(p).raw
        data['line'] = LineSegment2D(p, position)

        data['distance'] = self.line.start.distanceTo(p).raw
        debugData['distance'] = data['distance']

        return data

#___________________________________________________________________________________________________ draw
    def draw(self, drawing, **kwargs):
        drawPairs = kwargs.get('drawPairs', True)

        segLine = self.line
        edgeLineStyle = dict(stroke="#006666", stroke_width=1, stroke_opacity='0.25')
        lineStyles = [
            dict(stroke='#00CC00', stroke_width=1, stroke_opacity='0.25'),
            dict(stroke='#002200', stroke_width=1, stroke_opacity='0.25') ]

        if self.index in [0, -1]:
            styles = edgeLineStyle
        else:
            styles = lineStyles[1 if self.index & 1 else 0]

        drawing.line(segLine.start.toMayaTuple(), segLine.end.toMayaTuple(), **styles)

        drawing.circle(
            segLine.start.toMayaTuple(), 5,
            stroke='none', fill='#002200', fill_opacity='0.1')
        drawing.circle(
            segLine.end.toMayaTuple(), 5,
            stroke='none', fill='#002200', fill_opacity='0.1')

        if not drawPairs:
            return

        for pair in self.pairs:
            # Draw projection lines for each project pair in the segment
            line = pair['line']
            drawing.lineSegment(line, stroke='blue', stroke_width=1, stroke_opacity='0.5')

            drawing.circle(
                line.end.toMayaTuple(), 5, stroke='none', fill='blue', fill_opacity='0.5')

            drawing.circle(
                line.start.toMayaTuple(), 5, stroke='none', fill='black', fill_opacity='0.25')

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _initializeData
    @classmethod
    def _initializeData(cls, data, track):
        """_initializeData doc..."""

        if data is None:
            data = dict()
        ArgsUtils.addIfMissing('track', track, data)
        ArgsUtils.addIfMissing('debug', [], data)
        return data

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

