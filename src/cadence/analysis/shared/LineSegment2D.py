# LineSegment2D.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.shared.PositionValue2D import PositionValue2D

#*************************************************************************************************** LineSegment2D
class LineSegment2D(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, start =None, end =None):
        """Creates a new instance of LineSegment2D."""
        self.start = start if start else PositionValue2D()
        self.end   = end if end else PositionValue2D()

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: length
    @property
    def length(self):
        try:
            return self.start.distanceTo(self.end)
        except Exception:
            raise

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ distanceToPoint
    def distanceToPoint(self, point):
        """ Calculates the smallest distance between the specified point and this line segment
            using the standard formulation as described in:
            http://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points """

        length = self.length
        if not length:
            raise ValueError('Cannot calculate point distance. Invalid line segment.')

        s = self.start
        e = self.end
        deltaX = e.x - s.x
        deltaY = e.y - s.y

        distance = abs(deltaY*point.x - deltaX*point.y - s.x*e.y + e.x*s.y)/length.raw

        B       = deltaY*point.x - deltaX*point.y - s.x*e.y + e.x*s.y
        AbsB    = abs(B)
        D       = math.sqrt(deltaX*deltaX + deltaY*deltaY)
        DPrime  = 1.0/math.pow(deltaX*deltaX + deltaY*deltaY, 3.0/2.0)
        bBD     = B/(AbsB*D)

        pointXErr = point.xUnc*abs(deltaY*B/(AbsB*D))
        pointYErr = point.yUnc*abs(deltaX*B/(AbsB*D))
        startXErr = s.xUnc*abs(AbsB*DPrime + bBD*(point.y - e.y))
        startYErr = s.yUnc*abs(AbsB*DPrime + bBD*(e.x - point.x))
        endXErr   = e.xUnc*abs(bBD*(s.y - point.y) - AbsB*DPrime)
        endYErr   = e.yUnc*abs(bBD*(point.x - s.x) - AbsB*DPrime)
        error     = pointXErr + pointYErr + startXErr + startYErr + endXErr + endYErr

        return NumericUtils.toValueUncertainty(distance, error)

#___________________________________________________________________________________________________ extendLine
    def postExtendLine(self, lengthAdjust, replace =True):
        """extendLine doc..."""
        newX, newY = self._extrapolateByLength(lengthAdjust, pre=False)
        if not replace:
            self.end = self.end.clone()
        self.end.x = newX
        self.end.y = newY

#___________________________________________________________________________________________________ preExtendLine
    def preExtendLine(self, lengthAdjust, replace =True):
        """preExtendLine doc..."""
        newX, newY = self._extrapolateByLength(lengthAdjust, pre=True)
        if not replace:
            self.start = self.start.clone()
        self.start.x = newX
        self.start.y = newY

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _extrapolateByLength
    def _extrapolateByLength(self, lengthAdjust, pre =False):
        """_extrapolateByLength doc..."""

        length = self.length
        delta  = -abs(lengthAdjust) if self.start.x > self.end.x else abs(lengthAdjust)
        if pre:
            delta *= -1.0

        targetLengthSqr = math.pow(length.raw + lengthAdjust, 2)

        s = self.start
        e = self.end
        deltaX = e.x - s.x
        deltaY = e.y - s.y

        if pre:
            prevX = s.x
            point = self.end
        else:
            prevX = e.x
            point = self.start

        i = 0
        while i < 100000:
            x = prevX + delta
            y = s.y + deltaY*(x - s.x)/deltaX
            testLengthSqr = math.pow(x - point.x, 2) + math.pow(y - point.y, 2)

            if NumericUtils.equivalent(testLengthSqr/targetLengthSqr, 1.0, 0.000001):
                return x, y
            elif testLengthSqr > targetLengthSqr:
                delta *= 0.5
            else:
                prevX = x
            i += 1

        raise ValueError('Unable to extrapolate line segment to specified length')

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

