# DataChannel.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.ArgsUtils import ArgsUtils
from pyaid.string.StringUtils import StringUtils

from cadence.shared.io.channel.DataChannelKey import DataChannelKey

#_______________________________________________________________________________
class DataChannel(object):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
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

        self._clearCache()

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def name(self):
        """The name identifying the DataChannel instance."""
        return self._name if self._name else (self._target + '_' + self._kind)
    @name.setter
    def name(self, value):
        self._name = value

#_______________________________________________________________________________
    @property
    def kind(self):
        """The kind of DataChannel instance."""
        return self._kind
    @kind.setter
    def kind(self, value):
        self._kind = value

#_______________________________________________________________________________
    @property
    def target(self):
        """The kind of DataChannel instance."""
        return self._target
    @target.setter
    def target(self, value):
        self._target = value

#_______________________________________________________________________________
    @property
    def keys(self):
        """Data keyframes in the created/loaded dataset."""
        return self._keys if self._keys is not None else []

#_______________________________________________________________________________
    @property
    def times(self):
        """Data keyframes in the created/loaded dataset."""
        if self._times is None:
            out = []
            for k in self._keys:
                out.append(k.time)
            self._times = out

        return self._times

#_______________________________________________________________________________
    @property
    def values(self):
        """Data keyframes in the created/loaded dataset."""
        if self._values is None:
            out = []
            for k in self._keys:
                out.append(k.value)
            self._values = out

        return self._values

#_______________________________________________________________________________
    @property
    def inTangents(self):
        """Data keyframes in the created/loaded dataset."""
        if self._inTangents is None:
            out = []
            for k in self._keys:
                out.append(k.inTangent)
            self._inTangents = out

        return self._inTangents

#_______________________________________________________________________________
    @property
    def outTangents(self):
        """Data keyframes in the created/loaded dataset."""
        if self._outTangents is None:
            out = []
            for k in self._keys:
                out.append(k.outTangent)
            self._outTangents = out

        return self._outTangents

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def addKeysFromLists(self, **kwargs):
        self._clearCache()

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
                inTangent=inTans if StringUtils.isStringType(inTans) else inTans[i],
                outTangent=outTans if StringUtils.isStringType(outTans) else outTans[i] ))

#_______________________________________________________________________________
    def addKeyframe(self, keyframe):
        self._clearCache()

        if not isinstance(keyframe, DataChannelKey):
            keyframe = DataChannelKey.fromDict(keyframe)

        if not self._keys:
            self._keys.append(keyframe)
            return True

        index = 0
        for k in self._keys:
            if k.time <= keyframe.time:
                index += 1
                continue

            self._keys.insert(index, keyframe)
            return True

        self._keys.append(keyframe)
        return True

#_______________________________________________________________________________
    def echo(self):
        print(self.toString())

#_______________________________________________________________________________
    def toString(self):
        s = 'CHANNEL [%s] [%s]%s:\n' % (
            str(self.target),
            str(self.kind),
            (' ' +str(self.name)) if self.name else ''
        )
        out = []
        for k in self._keys:
             out.append(k.toString())
        s += ', '.join(out)
        return s

#_______________________________________________________________________________
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

#_______________________________________________________________________________
    @classmethod
    def fromDict(cls, src):
        return DataChannel(**src)

#===============================================================================
#                                                                               I N T R I N S I C

#_______________________________________________________________________________
    def __len__(self):
        return len(self._keys) if self._keys else 0

#_______________________________________________________________________________
    def __repr__(self):
        return self.__str__()

#_______________________________________________________________________________
    def __unicode__(self):
        return StringUtils.toUnicode(self.__str__())

#_______________________________________________________________________________
    def __str__(self):
        return '<%s::%s[%s] K:%s T:%s>' % (
            self.__class__.__name__, str(self.name), str(len(self.keys)), str(self.kind),
            str(self.target) )

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _clearCache(self):
        self._times         = None
        self._values        = None
        self._inTangents    = None
        self._outTangents   = None

#_______________________________________________________________________________
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
