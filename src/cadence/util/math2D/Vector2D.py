# Vector2D.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

from pyaid.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ Vector2D
class Vector2D(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, *args, **kwargs):
        """Creates a new instance of Vector2D."""
        if args and isinstance(args[0], (list, tuple)):
            self._values = list(args[0]) + []
        elif args and isinstance(args[0], Vector2D):
            self._values = [args[0].x, args[0].y]
        else:
            x = ArgsUtils.get('x', 0.0, kwargs, args, 0)
            y = ArgsUtils.get('y', 0.0, kwargs, args, 1)
            self._values = [x, y]

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: magnitude
    @property
    def magnitude(self):
        return math.sqrt(self.magnitudeSquared)

#___________________________________________________________________________________________________ GS: magnitudeSquared
    @property
    def magnitudeSquared(self):
        mag = 0.0
        for v in self._values:
            mag += float(v)*float(v)
        return mag

#___________________________________________________________________________________________________ GS: x
    @property
    def x(self):
        return float(self._values[0])
    @x.setter
    def x(self, value):
        self._values[0] = float(value)

#___________________________________________________________________________________________________ GS: y
    @property
    def y(self):
        return float(self._values[1])
    @y.setter
    def y(self, value):
        self._values[1] = float(value)

#___________________________________________________________________________________________________ GS: z
    @property
    def z(self):
        return float(self._values[2])
    @z.setter
    def z(self, value):
        self._values[2] = float(value)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ dot
    def dot(self, vec =None):
        """dot doc..."""
        if not vec:
            vec = self
        return self.x*vec.x + self.y*vec.y

#___________________________________________________________________________________________________ angleBetween
    def angleBetween(self, vec2D, asDegrees =False):
        """angleBetween doc..."""
        angle = math.acos(self.dot(vec2D)/(self.magnitude*vec2D.magnitude))
        if asDegrees:
            return 180/math.pi*angle
        return angle

#___________________________________________________________________________________________________ updateValues
    def updateValues(self, *args, **kwargs):
        x = ArgsUtils.get('x', None, kwargs, args, 0)
        if x is not None:
            self.x = x

        y = ArgsUtils.get('y', None, kwargs, args, 1)
        if y is not None:
            self.y = y

        return True

#___________________________________________________________________________________________________ setMagnitude
    def setMagnitude(self, length =1.0):
        """setMagnitude doc..."""
        mag = math.sqrt(self.x*self.x + self.y*self.y)
        self.x *= length/mag
        self.y *= length/mag

#___________________________________________________________________________________________________ normalize
    def normalize(self):
        self.setMagnitude(1.0)

#___________________________________________________________________________________________________ toList
    def toList(self):
        return [self.x, self.y, self.z]

#___________________________________________________________________________________________________ toSerialDict
    def toSerialDict(self):
        return {
            'objectType':self.__class__.__name__,
            'args':self.toList() }

#___________________________________________________________________________________________________ clone
    def clone(self):
        return Vector2D(self)

#___________________________________________________________________________________________________ fromSerialDict
    @classmethod
    def fromSerialDict(cls, value):
        return Vector2D(*value['args'])

#___________________________________________________________________________________________________ fromConfig
    @classmethod
    def fromConfig(cls, source):
        source = str(source).strip().split(',')
        out    = []
        for coordinate in source:
            out.append(float(coordinate.strip()))
        return Vector2D(*out)
