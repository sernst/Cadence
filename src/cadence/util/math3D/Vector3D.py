# Vector3D.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import math

import scipy

from cadence.util.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ Vector3D
class Vector3D(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, *args, **kwargs):
        """Creates a new instance of Vector3D."""
        if args and isinstance(args[0], list):
            self._values = args[0] + []
        elif args and isinstance(args[0], Vector3D):
            self._values = [args[0].x, args[0].y, args[0].z]
        else:
            x            = ArgsUtils.get('x', 0.0, kwargs, args, 0)
            y            = ArgsUtils.get('y', 0.0, kwargs, args, 1)
            z            = ArgsUtils.get('z', 0.0, kwargs, args, 2)
            self._values = [x, y, z]

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
            mag += v*v
        return mag

#___________________________________________________________________________________________________ GS: x
    @property
    def x(self):
        return self._values[0]
    @x.setter
    def x(self, value):
        self._values[0] = value

#___________________________________________________________________________________________________ GS: y
    @property
    def y(self):
        return self._values[1]
    @y.setter
    def y(self, value):
        self._values[1] = value

#___________________________________________________________________________________________________ GS: z
    @property
    def z(self):
        return self._values[2]
    @z.setter
    def z(self, value):
        self._values[2] = value

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ updateValues
    def updateValues(self, *args, **kwargs):
        x = ArgsUtils.get('x', None, kwargs, args, 0)
        if x is not None:
            self.x = x

        y = ArgsUtils.get('y', None, kwargs, args, 1)
        if y is not None:
            self.y = y

        z = ArgsUtils.get('z', None, kwargs, args, 2)
        if z is not None:
            self.z = z

        return True

#___________________________________________________________________________________________________ normalize
    def normalize(self, length =1.0):
        pass

#___________________________________________________________________________________________________ toList
    def toList(self):
        return [self.x, self.y, self.z]

#___________________________________________________________________________________________________ toSerialDict
    def toSerialDict(self):
        return {
            'objectType':self.__class__.__name__,
            'args':self.toList()
        }

#___________________________________________________________________________________________________ clone
    def clone(self):
        return Vector3D(self)

#___________________________________________________________________________________________________ fromSerialDict
    @classmethod
    def fromSerialDict(cls, value):
        return Vector3D(*value['args'])

#___________________________________________________________________________________________________ fromConfig
    @classmethod
    def fromConfig(cls, source):
        source = str(source).strip().split(',')
        out    = []
        for coordinate in source:
            out.append(float(coordinate.strip()))
        return Vector3D(*out)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _validateTargetPosition
    def _validateTargetPosition(self):
        """Doc..."""
        return False

