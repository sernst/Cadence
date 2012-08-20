# DataChannel.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from cadence.shared.io.channel.DataChannelKey import DataChannelKey
from cadence.util.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ DataChannel
class DataChannel(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """ Creates a new instance of DataChannel.

            @@@param name:string
                The name identifying the data channel.
        """

        self._name   = ArgsUtils.get('name', None, kwargs)
        self._kind   = ArgsUtils.get('kind', None, kwargs)
        self._target = ArgsUtils.get('target', None, kwargs)
        self._keys   = self._createKeys(ArgsUtils.get('keys', None, kwargs))

        if not self._keys:
            self.addKeysFromLists(**kwargs)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        """The name identifying the DataChannel instance."""
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

#___________________________________________________________________________________________________ GS: kind
    @property
    def kind(self):
        """The kind of DataChannel instance."""
        return self._kind
    @kind.setter
    def kind(self, value):
        self._kind = value

#___________________________________________________________________________________________________ GS: target
    @property
    def target(self):
        """The kind of DataChannel instance."""
        return self._target
    @target.setter
    def target(self, value):
        self._target = value

#___________________________________________________________________________________________________ GS: keys
    @property
    def keys(self):
        """Data keyframes in the created/loaded dataset."""
        return self._keys

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ addKeysFromLists
    def addKeysFromLists(self, **kwargs):
        x = ArgsUtils.get('times', None, kwargs)
        if not x:
            return

        y = ArgsUtils.get('values', None, kwargs)
        if not y:
            return

        tans    = ArgsUtils.get('tangents', None, kwargs)
        inTans  = ArgsUtils.get('inTangents', tans, kwargs)
        outTans = ArgsUtils.get('outTangents', tans, kwargs)

        if not inTans:
            inTans = 'lin'

        if not outTans:
            outTans = 'lin'

        for i in range(0,len(x)):
            self._keys.append(DataChannelKey(
                time=x[i],
                value=y[i],
                inTangent=inTans if isinstance(inTans, basestring) else inTans[i],
                outTangent=outTans if isinstance(outTans, basestring) else outTans[i]
            ))

#___________________________________________________________________________________________________ addKeyframe
    def addKeyframe(self, keyframe):
        if isinstance(keyframe, DataChannelKey):
            self._keys.append(keyframe)
        else:
            self._keys.append(DataChannelKey.fromDict(keyframe))

        return True

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        keys = []
        for k in self._keys:
            keys.append(k.toDict())
        return {
            'name':self.name,
            'kind':self.kind,
            'target':self.target,
            'keys':keys
        }

#___________________________________________________________________________________________________ fromDict
    @classmethod
    def fromDict(cls, src):
        return DataChannel(**src)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _createKeys
    def _createKeys(self, src):
        if not src:
            return []

        keys = []
        for key in src:
            if isinstance(key, DataChannelKey):
                keys.append(key)
            else:
                keys.append(DataChannelKey.fromDict(key))

        return keys