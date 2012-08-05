# Effector.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import scipy

from cadence.config.enum.GaitConfigEnum import GaitConfigEnum
from cadence.config.enum.SkeletonConfigEnum import SkeletonConfigEnum
from cadence.util.math3D.Vector3D import Vector3D

#___________________________________________________________________________________________________ Effector
class Effector(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of Effector."""
        self._id                = kwargs.get('id', 'UnknownEffector')
        self._skeleton          = kwargs.get('skeleton', None)
        self._left              = self._id.lower().startswith('left')
        self._posterior         = self._id.lower().endswith('pes')
        self._positions         = []
        self._neutralPosition   = Vector3D(
            self._skeleton.configs.get(
                SkeletonConfigEnum.START_POSITION_GROUPLESS,
                reps={'#GROUP#':self._id.lower()}
            )
        )

        pos                    = self._neutralPosition.clone()
        pos.z                 += 0.5*self._skeleton.strideLength
        self._flexionPosition  = pos

        pos                      = self._neutralPosition.clone()
        pos.z                   -= 0.5*self._skeleton.stridLength
        self._extensionPosition  = pos

        self._phaseOffset = 0.0 if self._left else 180.0
        if not self._posterior:
            self._phaseOffset += self._skeleton.configs.get(GaitConfigEnum.PHASE)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: skeleton
    @property
    def skeleton(self):
        return self._skeleton

#___________________________________________________________________________________________________ GS: position
    @property
    def position(self):
        return self._positions[-1]

#___________________________________________________________________________________________________ GS: velocity
    @property
    def velocity(self):
        return self.getVelocityAt()

#___________________________________________________________________________________________________ GS: acceleration
    @property
    def acceleration(self):
        return self.getAccelerationAt()

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getVelocityAt
    def getVelocityAt(self, index =None):
        """Doc..."""
        if index is None:
            index = len(self._positions) - 1

        if index > 0:
            return scipy.spatial.distance.euclidean(
                self._positions[index - 1],
                self._positions[index]) / self._skeleton.deltaTime

        return 0

#___________________________________________________________________________________________________ getAccelerationAt
    def getAccelerationAt(self, index =None):
        """Doc..."""
        if index is None:
            index = len(self._positions) - 1

        v2 = self.getVelocityAt(index)
        v1 = self.getAccelerationAt(index - 1)
        return (v2 - v1) / self._skeleton.deltaTime

