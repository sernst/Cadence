# PositionValue2D.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from pyaid.number.NumericUtils import NumericUtils

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
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ clone
    def clone(self):
        """clone doc..."""
        return PositionValue2D(self.x, self.y, self.xUnc, self.yUnc)

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
        error  = (xDelta*(self.xUnc + position.xUnc) + yDelta*(self.yUnc + position.yUnc))/distance

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
        return '<%s>' % self.__class__.__name__

