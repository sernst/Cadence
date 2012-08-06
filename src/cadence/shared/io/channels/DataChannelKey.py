# DataChannelKey.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from cadence.util.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ DataChannelKey
class DataChannelKey(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """ Creates a new instance of DataChannelKey.

            @@@param name:string
                The name identifying the data channel.
        """

        self.name          = ArgsUtils.get('name', None, kwargs)
        self.time          = ArgsUtils.get('time', 0.0, kwargs)
        self.value         = ArgsUtils.get('value', 0.0, kwargs)
        self.event         = ArgsUtils.get('event', None, kwargs)
        self.inTangent     = ArgsUtils.get('inTangent', None, kwargs)
        self.outTangent    = ArgsUtils.get('outTangent', None, kwargs)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        d = {
            'name':self.name,
            'time':self.time,
            'value':self.value,
            'event':self.event,
            'inTangent':self.inTangent,
            'outTangent':self.outTangent
        }

#___________________________________________________________________________________________________ fromDict
    @classmethod
    def fromDict(cls, src):
        return DataChannelKey(**src)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________