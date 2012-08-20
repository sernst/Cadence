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
        self.inTangent     = ArgsUtils.get('inTangent', 'lin', kwargs)
        self.outTangent    = ArgsUtils.get('outTangent', 'lin', kwargs)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        d = {
            'x':self.time,
            'y':self.value,
            'it':self.inTangent,
            'ot':self.outTangent
        }

        if self.name:
            d['n'] = self.name

        if self.event:
            d['e'] = self.event

        return d

#___________________________________________________________________________________________________ fromDict
    @classmethod
    def fromDict(cls, src):
        return DataChannelKey(
            name=ArgsUtils.get(['n', 'name'], None, src),
            event=ArgsUtils.get(['e', 'event'], None, src),
            time=ArgsUtils.get(['x', 'time'], None, src),
            value=ArgsUtils.get(['y', 'value'], None, src),
            inTangent=ArgsUtils.get(['it', 'inTangent'], 'lin', src),
            outTangent=ArgsUtils.get(['ot', 'outTangent'], 'lin', src)
        )

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________