# Skeleton.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from cadence.config.ConfigReader import ConfigReader
from cadence.config.enum.GaitConfigEnum import GaitConfigEnum
from cadence.config.enum.GeneralConfigEnum import GeneralConfigEnum
from cadence.config.enum.SkeletonConfigEnum import SkeletonConfigEnum
from cadence.solver.effectors.Effector import Effector

#___________________________________________________________________________________________________ Skeleton
class Skeleton(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of Skeleton."""
        self._configs = ConfigReader(
            generalFile=kwargs.get('generalConfig', None),
            skeletonFile=kwargs.get('skeletonConfig', None),
            gaitFile=kwargs.get('gaitConfig', None)
        )

        self._steps = int(self._configs.get(GeneralConfigEnum.STEPS))

        self._hips          = Effector(id='hips',     skeleton=self)
        self._leftPes       = Effector(id='leftpes',  skeleton=self, order=1)
        self._rightPes      = Effector(id='rightpes', skeleton=self, order=3)
        self._leftManus     = Effector(id='leftmanus', skeleton=self, order=2)
        self._rightManus    = Effector(id='rightmanus', skeleton=self, order=4)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: configs
    @property
    def configs(self):
        return self._configs

#___________________________________________________________________________________________________ GS: deltaTime
    @property
    def deltaTime(self):
        return 1.0 / float(self._steps)

#___________________________________________________________________________________________________ GS: strideLength
    @property
    def strideLength(self):
        scale     = self.configs.get(GaitConfigEnum.STRIDE_SCALE)
        maxLength = self.configs.get(SkeletonConfigEnum.MAX_STRIDE_LENGTH)
        return scale*maxLength

#___________________________________________________________________________________________________ GS: hips
    @property
    def hips(self):
        """The hip effector for the skeleton."""
        return self._hips

#___________________________________________________________________________________________________ GS: leftPes
    @property
    def leftPes(self):
        """The left pes for the skeleton."""
        return self._leftPes

#___________________________________________________________________________________________________ GS: rightPes
    @property
    def rightPes(self):
        """The right pes for the skeleton."""
        return self._rightPes

#___________________________________________________________________________________________________ GS: leftManus
    @property
    def leftManus(self):
        """The left manus for the skeleton."""
        return self._leftManus

#___________________________________________________________________________________________________ GS: rightManus
    @property
    def rightManus(self):
        """The right manus for the skeleton."""
        return self._rightManus

