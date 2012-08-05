# Cadence.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from cadence.solver.skeletons.Skeleton import Skeleton
from cadence.util.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ Cadence
class Cadence(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of Cadence."""
        self._skeleton = Skeleton(
            generalConfig=ArgsUtils.get('generalConfig', None, kwargs),
            skeletonConfig=ArgsUtils.get('skeletonConfig', None, kwargs)
        )

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: skeleton
    @property
    def skeleton(self):
        return self._skeleton

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ execute
    def execute(self):
        """Doc..."""
        pass

