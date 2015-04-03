# PositionValue2D.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import math

from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

#*************************************************************************************************** PositionValue2D
class PositionValue2D(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, x = 0.0, y = 0.0, xUnc = 0.0, yUnc = 0.0):
        """Creates a new instance of PositionValue."""
        self.x    = x
        self.y    = y
        self.xUnc = xUnc
        self.yUnc = yUnc

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: xValue
    @property
    def xValue(self):
        return NumericUtils.toValueUncertainty(self.x, self.xUnc)

#___________________________________________________________________________________________________ GS: yValue
    @property
    def yValue(self):
        return NumericUtils.toValueUncertainty(self.y, self.yUnc)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ clone
    def clone(self):
        """clone doc..."""
        return PositionValue2D(x=self.x, y=self.y, xUnc=self.xUnc, yUnc=self.yUnc)

#___________________________________________________________________________________________________ add
    def add(self, point):
        """add doc..."""
        self.x += point.x
        self.y += point.y
        self.xUnc = math.sqrt(self.xUnc*self.xUnc + point.xUnc*point.xUnc)
        self.yUnc = math.sqrt(self.yUnc*self.yUnc + point.yUnc*point.yUnc)

#___________________________________________________________________________________________________ subtract
    def subtract(self, point):
        """add doc..."""
        self.x -= point.x
        self.y -= point.y
        self.xUnc = math.sqrt(self.xUnc*self.xUnc + point.xUnc*point.xUnc)
        self.yUnc = math.sqrt(self.yUnc*self.yUnc + point.yUnc*point.yUnc)

#___________________________________________________________________________________________________ rotate
    def rotate(self, angle, origin =None):
        """ Rotates the position value by the specified angle using a standard 2D rotation matrix
            formulation. If an origin Position2D instance is not specified the rotation will
            occur around the origin. Also, if an origin is specified, the uncertainty in that
            origin value will be propagated through to the uncertainty of the rotated result. """

        if origin is None:
            origin = PositionValue2D()

        a = angle.radians
        x = self.x - origin.x
        y = self.y - origin.y

        self.x = x*math.cos(a) - y*math.sin(a) + origin.x
        self.y = y*math.cos(a) + x*math.sin(a) + origin.y

        self.xUnc = math.sqrt(self.xUnc*self.xUnc + origin.xUnc*origin.xUnc)
        self.yUnc = math.sqrt(self.yUnc*self.yUnc + origin.yUnc*origin.yUnc)

#___________________________________________________________________________________________________ distanceTo
    def distanceTo(self, position):
        """distanceBetween doc..."""
        xDelta   = self.x - position.x
        yDelta   = self.y - position.y
        distance = math.sqrt(xDelta*xDelta + yDelta*yDelta)

        # Use the absolute value because the derivatives in error propagation are always
        # absolute values
        xDelta = abs(xDelta)
        yDelta = abs(yDelta)
        try:
            error = (xDelta*(self.xUnc + position.xUnc)
                  + yDelta*(self.yUnc + position.yUnc) )/distance
        except ZeroDivisionError:
            error = 1.0

        return NumericUtils.toValueUncertainty(distance, error)

#___________________________________________________________________________________________________ xFromUncertaintyValue
    def xFromUncertaintyValue(self, value):
        """xFromUncertaintyValue doc..."""
        self.x = value.value
        self.xUnc = value.uncertainty

#___________________________________________________________________________________________________ yFromUncertaintyValue
    def yFromUncertaintyValue(self, value):
        """xFromUncertaintyValue doc..."""
        self.y = value.value
        self.yUnc = value.uncertainty

#___________________________________________________________________________________________________ toTuple
    def toTuple(self):
        """toList doc..."""
        return self.x, self.y, self.xUnc, self.yUnc

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        """__str__ doc..."""
        return StringUtils.toStr2(self.__unicode__())

#___________________________________________________________________________________________________ __str__
    def __unicode__(self):
        isPy2 = bool(sys.version < '3')

        return '<%s (%s, %s)>' % (
            self.__class__.__name__,
            NumericUtils.toValueUncertainty(self.x, self.xUnc, asciiLabel=isPy2).label,
            NumericUtils.toValueUncertainty(self.y, self.yUnc, asciiLabel=isPy2).label)


