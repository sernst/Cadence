# DataChannelKey.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.ArgsUtils import ArgsUtils
from pyaid.string.StringUtils import StringUtils

from cadence.shared.enum.DataTypeEnum import DataTypeEnum
from cadence.shared.enum.MayaTangentsEnum import MayaTangentsEnum
from cadence.shared.enum.TangentsEnum import TangentsEnum
from cadence.util.math3D.Vector3D import Vector3D

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

        cls = self.__class__

        self.name          = ArgsUtils.get('name', None, kwargs)
        self.time          = ArgsUtils.get('time', 0.0, kwargs)
        self.value         = ArgsUtils.get('value', 0.0, kwargs)
        self.dataType      = ArgsUtils.get('dataType', None, kwargs)
        if not self.dataType:
            self.dataType = cls._getDataTypeFromValue(self.value)
        else:
            self.value = cls._formatValueFromDataType(self.value, self.dataType)

        self.event = ArgsUtils.get('event', None, kwargs)

        self._inTangent = cls._getTangentEnum(
            ArgsUtils.get('inTangent', None, kwargs), self.dataType
        )
        self._outTangent = cls._getTangentEnum(
            ArgsUtils.get('outTangent', None, kwargs), self.dataType
        )

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: inTangent
    @property
    def inTangent(self):
        return self.__class__._getTangentEnum(self._inTangent, self.dataType, maya=False)

#___________________________________________________________________________________________________ GS: inTangentMaya
    @property
    def inTangentMaya(self):
        return self.__class__._getTangentEnum(self.inTangent, self.dataType, maya=True)

#___________________________________________________________________________________________________ GS: outTangent
    @property
    def outTangent(self):
        return self.__class__._getTangentEnum(self._outTangent, self.dataType, maya=False)

#___________________________________________________________________________________________________ GS: outTangentMaya
    @property
    def outTangentMaya(self):
        return self.__class__._getTangentEnum(self.outTangent,  self.dataType, maya=True)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ echo
    def echo(self):
        print(self.toString('KEY'))

#___________________________________________________________________________________________________ toString
    def toString(self,  prefix =''):
        tangents = ''
        if self.inTangent == 'lin' and self.outTangent == 'lin':
            tangents = ''
        else:
            inTans = ''
            if isinstance(self.inTangent, list):
                tanValue = self.inTangent[0]
                for v in self.inTangent[1:]:
                    if tanValue != v:
                        inTans = str(self.inTangent)
                if not inTans:
                    inTans = tanValue
            else:
                inTans = self.inTangent

            outTans = ''
            if isinstance(self.outTangent, list):
                tanValue = self.outTangent[0]
                for v in self.outTangent[1:]:
                    if tanValue != v:
                        outTans = str(self.outTangent)
                if not outTans:
                    outTans = tanValue
            else:
                outTans = self.outTangent

            tangents = ' (%s, %s)' % (str(inTans), str(outTans))

        info = ''
        if self.event:
            info = ' ' + str(self.event)

        return '<%s%s%s (%s, %s)%s%s>' % (
            (str(prefix) + '::') if prefix else '',
            ((str(self.name) + ':') if self.name else ''),
            str(self.dataType),
            str(self.time),
            str(self.__class__._getSerializedValue(self.value, self.dataType)),
            tangents,
            info
        )

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        if self.dataType == DataTypeEnum.VECTOR:
            inTangent = self.inTangent
            if inTangent[0] == inTangent[1] and inTangent[1] == inTangent[2]:
                inTangent = inTangent[0]
        else:
            inTangent = self.inTangent

        if self.dataType == DataTypeEnum.VECTOR:
            outTangent = self.outTangent
            if outTangent[0] == outTangent[1] and outTangent[1] == outTangent[2]:
                outTangent = outTangent[0]
        else:
            outTangent = self.outTangent

        d = {
            't':self.time,
            'v':self.__class__._getSerializedValue(self.value, self.dataType),
            'it':inTangent,
            'ot':outTangent
        }

        if self.name:
            d['n'] = self.name

        if self.event:
            d['e'] = self.event

        if self.dataType != DataTypeEnum.SCALAR:
            d['dt'] = self.dataType

        return d

#___________________________________________________________________________________________________ fromDict
    @classmethod
    def fromDict(cls, src):
        dataType = ArgsUtils.get(['dt', 'dataType'], None, src)
        value    = ArgsUtils.get(['v', 'value'], 0.0, src)
        return DataChannelKey(
            name=ArgsUtils.get(['n', 'name'], None, src),
            event=ArgsUtils.get(['e', 'event'], None, src),
            time=ArgsUtils.get(['t', 'time'], 0.0, src),
            value=value,
            dataType=dataType,
            inTangent=ArgsUtils.get(['it', 'inTangent'], TangentsEnum.LINEAR, src),
            outTangent=ArgsUtils.get(['ot', 'outTangent'], TangentsEnum.LINEAR, src)
        )

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getTangentEnum
    @classmethod
    def _getTangentEnum(cls, source, dataType, maya =False):
        if dataType == DataTypeEnum.VECTOR:
            if isinstance(source, list):
                out = []
                for src in source:
                    out.append(cls._getTangentEnumValue(src, maya))
                return out
            else:
                value = cls._getTangentEnumValue(source, maya)
                return [value, value, value]
        else:
            return cls._getTangentEnumValue(source, maya)

#___________________________________________________________________________________________________ _getTangentEnumValue
    @classmethod
    def _getTangentEnumValue(cls, source, maya =False):
        enums = MayaTangentsEnum if maya else TangentsEnum
        if not source:
            return enums.LINEAR

        t = source.strip().lower().replace('_', '')

        if t in [TangentsEnum.SPLINE, MayaTangentsEnum.SPLINE]:
            return enums.SPLINE
        elif t in [TangentsEnum.LINEAR, MayaTangentsEnum.LINEAR]:
            return enums.LINEAR
        elif t in [TangentsEnum.FAST, MayaTangentsEnum.FAST]:
            return enums.FAST
        elif t in [TangentsEnum.SLOW, MayaTangentsEnum.SLOW]:
            return enums.SLOW
        elif t in [TangentsEnum.FLAT, MayaTangentsEnum.FLAT]:
            return enums.FLAT
        elif t in [TangentsEnum.STEPPED, MayaTangentsEnum.STEPPED]:
            return enums.STEPPED
        elif t in [TangentsEnum.STEPPED_NEXT, 'stepnext', MayaTangentsEnum.STEPPED_NEXT]:
            return enums.STEPPED_NEXT
        elif t in [TangentsEnum.FIXED, MayaTangentsEnum.FIXED]:
            return enums.FIXED
        elif t in [TangentsEnum.CLAMPED, MayaTangentsEnum.CLAMPED]:
            return enums.CLAMPED
        elif t in [TangentsEnum.PLATEAU, MayaTangentsEnum.PLATEAU]:
            return enums.PLATEAU

        return enums.LINEAR

#___________________________________________________________________________________________________ _getSerializedValue
    @classmethod
    def _getSerializedValue(cls, value, dataType):
        if dataType == DataTypeEnum.VECTOR or isinstance(value, Vector3D):
            return value.toList()
        return value

#___________________________________________________________________________________________________ _getDataTypeFromValue
    @classmethod
    def _getDataTypeFromValue(cls, value):
        if StringUtils.isStringType(value):
            return DataTypeEnum.ENUM
        elif isinstance(value, Vector3D):
            return DataTypeEnum.VECTOR
        elif isinstance(value, dict) or isinstance(value, list):
            return DataTypeEnum.ARBITRARY

        return DataTypeEnum.SCALAR

#___________________________________________________________________________________________________ _formatValueFromDataType
    @classmethod
    def _formatValueFromDataType(cls, value, dataType):
        if dataType == DataTypeEnum.VECTOR:
            if isinstance(value, list):
                return Vector3D(*value)

        return value
