# CadenceZiggurat.py
# (C)2013
# Scott Ernst

from ziggurat.ZigguratApplication import ZigguratApplication

from cadence.CadenceEnvironment import CadenceEnvironment

#___________________________________________________________________________________________________ CadenceZiggurat
class CadenceZiggurat(ZigguratApplication):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        """Creates a new instance of CadenceZiggurat."""
        super(CadenceZiggurat, self).__init__()

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: timecodeOffset
    @property
    def timecodeOffset(self):
        return CadenceEnvironment.BASE_UNIX_TIME

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _initialize
    def _initialize(self):
        configs = self.configurator
        #configs.addRouteItem()

####################################################################################################
####################################################################################################

application = CadenceZiggurat()
