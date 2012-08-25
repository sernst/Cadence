# DataChannelKey.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from cadence.shared.enum.DataTypeEnum import DataTypeEnum
from cadence.util.ArgsUtils import ArgsUtils
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

        self.event         = ArgsUtils.get('event', None, kwargs)
        self.inTangent     = ArgsUtils.get('inTangent', 'lin', kwargs)
        self.outTangent    = ArgsUtils.get('outTangent', 'lin', kwargs)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ echo
    def echo(self):
        print self.toString('KEY')

#___________________________________________________________________________________________________ toString
    def toString(self,  prefix =''):
        tangents = ''
        if self.inTangent != 'lin' or self.outTangent != 'lin':
            tangents = ' (%s, %s)' % (str(self.inTangent), str(self.outTangent))

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
        d = {
            't':self.time,
            'v':self.__class__._getSerializedValue(self.value, self.dataType),
            'it':self.inTangent,
            'ot':self.outTangent
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
        value    = ArgsUtils.get(['y', 'value'], 0.0, src)
        return DataChannelKey(
            name=ArgsUtils.get(['n', 'name'], None, src),
            event=ArgsUtils.get(['e', 'event'], None, src),
            time=ArgsUtils.get(['x', 'time'], 0.0, src),
            value=value,
            dataType=dataType,
            inTangent=ArgsUtils.get(['it', 'inTangent'], 'lin', src),
            outTangent=ArgsUtils.get(['ot', 'outTangent'], 'lin', src)
        )

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getSerializedValue
    @classmethod
    def _getSerializedValue(cls, value, dataType):
        if dataType == DataTypeEnum.VECTOR or isinstance(value, Vector3D):
            return value.toList()
        return value

#___________________________________________________________________________________________________ _getDataTypeFromValue
    @classmethod
    def _getDataTypeFromValue(cls, value):
        if isinstance(value, basestring):
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
