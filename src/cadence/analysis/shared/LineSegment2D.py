# LineSegment2D.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from pyaid.number.Angle import Angle
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

#___________________________________________________________________________________________________ GS: isValid
    @property
    def isValid(self):
        return bool(abs(self.end.x - self.start.x) + abs(self.end.y - self.start.y))

#___________________________________________________________________________________________________ GS: length
    @property
    def length(self):
        """ The length of the line segment. """
        return self.start.distanceTo(self.end)

#___________________________________________________________________________________________________ GS: angle
    @property
    def angle(self):
        v = self.end.clone()
        v.subtract(self.start)
        vxUnc = math.sqrt(math.pow(self.start.xUnc, 2) + math.pow(self.end.xUnc, 2))
        vyUnc = math.sqrt(math.pow(self.start.yUnc, 2) + math.pow(self.end.yUnc, 2))

        value = math.atan2(v.y, v.x)
        lengthSqr = math.pow(v.length.raw, 2)
        unc = abs(v.y/lengthSqr)*vxUnc + abs(v.x/lengthSqr)*vyUnc
        return Angle(radians=value, uncertainty=unc)

#___________________________________________________________________________________________________ GS: slope
    @property
    def slope(self):
        """ Returns the slope of the line as a ValueUncertainty named tuple. """
        s       = self.start
        e       = self.end
        deltaX  = e.x - s.x
        deltaY  = e.y - s.y

        try:
            slope   = deltaY/deltaX
            unc     = abs(1.0/deltaX)*(s.yUnc + e.yUnc) + abs(slope/deltaX)*(s.xUnc + e.xUnc)
            return NumericUtils.toValueUncertainty(slope, unc)
        except Exception:
            return None

#___________________________________________________________________________________________________ GS: midpoint
    @property
    def midpoint(self):
        """ Returns the midpoint of the line as a PositionValue2D instance. """
        x = 0.5*(self.start.x + self.end.x)
        y = 0.5*(self.start.y + self.end.y)

        xUnc = 0.5*(self.start.xUnc + self.end.xUnc)
        yUnc = 0.5*(self.start.yUnc + self.end.yUnc)

        return PositionValue2D(x=x, y=y, xUnc=xUnc, yUnc=yUnc)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ echo
    def echo(self, asciiLabel =False):
        """echo doc..."""
        return '[%s %s -> %s]' % (
            'LINE',
            self.start.echo(asciiLabel=asciiLabel),
            self.end.echo(asciiLabel=asciiLabel) )

#___________________________________________________________________________________________________ addOffset
    def addOffset(self, point):
        """addOffset doc..."""
        self.start.x += point.x
        self.start.y += point.y
        self.end.x   += point.x
        self.end.y   += point.y

#___________________________________________________________________________________________________ getParametricPosition
    def getParametricPosition(self, value, clamp =True):
        """getParametricPosition doc..."""
        if clamp:
            value = max(0.0, min(value, 1.0))

        x    = self.start.x + value*(self.end.x - self.start.x)
        xUnc = abs(1.0 - value)*self.start.xUnc + abs(value)*self.end.xUnc

        y    = self.start.y + value*(self.end.y - self.start.y)
        yUnc = abs(1.0 - value)*self.start.yUnc + abs(value)*self.end.yUnc

        return PositionValue2D(x=x, y=y, xUnc=xUnc, yUnc=yUnc)

#___________________________________________________________________________________________________ adjustPointAlongLine
    def adjustPointAlongLine(self, point, delta, inPlace =False):
        """adjustPointAlongLine doc..."""

        assert isinstance(point, PositionValue2D), 'Argument point not a PositionValue2D instance'

        if not inPlace:
            point = point.clone()

        remove = self.start.clone()
        remove.invert()
        l = self.clone()
        l.addOffset(remove)

        position = l.getParametricPosition(delta/self.length.raw, clamp=False)
        point.add(position)

        return point

#___________________________________________________________________________________________________ rotate
    def rotate(self, angle, origin =None):
        """rotate doc..."""
        self.start.rotate(angle, origin=origin)
        self.end.rotate(angle, origin=origin)

#___________________________________________________________________________________________________ angleBetween
    def angleBetween(self, line):
        """ Returns an Angle instance that represents the angle between this line segment and the
            one specified in the arguments. """

        return self.angle.differenceBetween(line.angle)

#___________________________________________________________________________________________________ angleBetweenPoint
    def angleBetweenPoint(self, position):
        """angleBetweenPoint doc..."""
        a = self.end.clone()
        a.subtract(self.start)
        b = position.clone()
        b.subtract(self.start)

        return b.angleBetween(a)

#___________________________________________________________________________________________________ clone
    def clone(self):
        """ Returns a new LineSegment2D that is a clone of this instance. The start and end
            points are cloned as well making a completely separate copy with no reference
            dependencies on this instance. """

        return LineSegment2D(
            start=self.start.clone(),
            end=self.end.clone())

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

        if deltaX == 0.0:
            # Vertical Line
            distance = abs(s.x - point.x)
        elif deltaY == 0.0:
            # Horizontal line
            distance = abs(s.y - point.y)
        else:
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

#___________________________________________________________________________________________________ closestPointOnLine
    def closestPointOnLine(self, point, contained =True):
        """ Finds the closest point on a line to the specified point using the formulae
            discussed in the "another formula" section of:
            http://en.m.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Another_formula """

        length = self.length
        if not length:
            raise ValueError('Cannot calculate point. Invalid line segment.')

        s = self.start
        e = self.end
        deltaX = e.x - s.x
        deltaY = e.y - s.y
        rotate = False
        slope = 0.0
        slopeUnc = 0.0

        try:
            slope = deltaY/deltaX
            slopeUnc = abs(1.0/deltaX)*(s.yUnc + e.yUnc) + abs(slope/deltaX)*(s.xUnc + e.xUnc)
        except Exception:
            rotate = True

        if rotate or (abs(slope) > 1.0 and abs(slopeUnc/slope) > 0.5):
            a = Angle(degrees=20.0)
            line = self.clone()
            line.rotate(a, self.start)
            p = point.clone()
            p.rotate(a, self.start)
            result = line.closestPointOnLine(p, contained=contained)
            if result is None:
                return result

            a.degrees = -20.0
            result.rotate(a, self.start)
            return result

        intercept = s.y - slope*s.x
        denom = slope*slope + 1.0
        numer = point.x + slope*(point.y - intercept)

        x = numer/denom
        y = (slope*numer)/denom + intercept

        if contained:
            # Check to see if point is between start and end values
            xRange = sorted([self.start.x, self.end.x])
            yRange = sorted([self.start.y, self.end.y])
            eps = 1e-8
            xMin = x - eps
            xMax = x + eps
            yMin = y - eps
            yMax = y + eps
            if xRange[1] < xMin or xMax < xRange[0] or yRange[1] < yMin or yMax < yRange[0]:
                return None

        pos = PositionValue2D(x=x, y=y)

        startDist = self.start.distanceTo(pos)
        endDist = self.end.distanceTo(pos)

        xUnc = startDist.raw/length.raw*self.start.xUnc + endDist.raw/length.raw*self.end.xUnc
        pos.xUnc = math.sqrt(xUnc**2 + point.xUnc**2)

        yUnc = startDist.raw/length.raw*self.start.yUnc + endDist.raw/length.raw*self.end.yUnc
        pos.yUnc = math.sqrt(yUnc**2 + point.yUnc**2)

        return pos

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

#___________________________________________________________________________________________________ createNextLineSegment
    def createNextLineSegment(self, length =None):
        """ Creates a line segment using this line segment as a guide that starts where this segment
            ends and has the same slope and orientation. The new line segment will be of the
            specified length, or if no length is specified the same length as this line segment. """

        if length is None:
            length = self.length
        target = self.clone()
        target.postExtendLine(lengthAdjust=length)
        target.start = self.end.clone()
        return target

#___________________________________________________________________________________________________ createPreviousLineSegment
    def createPreviousLineSegment(self, length =None):
        """ Creates a line segment using this line segment as a guide that ends where this segment
            begins and has the same slope and orientation. The new line segment will be of the
            specified length, or if no length is specified the same length as this line segment. """

        if length is None:
            length = self.length
        target = self.clone()
        target.preExtendLine(lengthAdjust=length)
        target.end = self.start.clone()
        return target

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _extrapolateByLength
    def _extrapolateByLength(self, lengthAdjust, pre =False):
        """_extrapolateByLength doc..."""

        length = self.length
        targetLengthSqr = (length.raw + lengthAdjust)**2

        s = self.start
        e = self.end
        deltaX = e.x - s.x
        deltaY = e.y - s.y

        delta = lengthAdjust
        if NumericUtils.equivalent(deltaX, 0.0):
            # Vertical lines should invert delta if start is above the end
            delta *= -1.0 if deltaY < 0.0 else 1.0
        elif deltaX < 0.0:
            # Other lines should invert delta if start is right of the end
            delta *= -1.0

        if pre:
            delta *= -1.0
            startY = s.y
            prevX = s.x
            point = self.end
        else:
            startY = e.y
            prevX = e.x
            point = self.start

        if NumericUtils.equivalent(deltaX, 0.0):
            return s.x, startY + delta

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

