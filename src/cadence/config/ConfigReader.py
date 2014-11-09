# ConfigReader.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re
import os
import json
import sys
from pyaid.dict.DictUtils import DictUtils
from pyaid.string.StringUtils import StringUtils

if sys.version > '3':
    import configparser as ConfigParser
else:
    import ConfigParser

from pyaid.ArgsUtils import ArgsUtils

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.util.math3D.Vector3D import Vector3D

#___________________________________________________________________________________________________ ConfigReader
class ConfigReader(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    EXTENSION = '.cfg'

    _VECTOR_PREFIX = 'VECTOR('
    _JSON_PREFIX   = 'JSON:'
    _NUMERIC_REGEX = re.compile('^[-\.0-9]+$')

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of ConfigReader."""
        self._configs     = ArgsUtils.get('configs', dict(), kwargs)
        self._filenames   = ArgsUtils.get('filenames', None, kwargs)
        self._configPath  = ArgsUtils.get(
            'rootConfigPath',
            CadenceEnvironment.getConfigPath(),
            kwargs
        )

        if self._filenames:
            for n,v in DictUtils.iter(self._filenames):
                if not v:
                    continue

                path = os.path.join(self._configPath, v)
                if not path.endswith('.cfg'):
                    path += '.cfg'

                parser = ConfigParser.ConfigParser()
                if os.path.exists(path):
                    parser.read(path)
                else:
                    raise Exception(path + ' config file does not exist!')

                self._configs[n] = self._configParserToDict(parser)

        self._overrides = dict()
        self.setOverrides(ArgsUtils.get('overrides', None, kwargs))

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: configPath
    @property
    def configPath(self):
        return self._configPath
    @configPath.setter
    def configPath(self, value):
        self._configPath = value

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ set
    def set(self, propertyID, value):
        parts = propertyID.split('_')

        if parts[0] not in self._configs:
            raise Exception('No %s config exists. Unable to set property %s on unknown config.' % \
                             (parts[0], propertyID))

        return self._setValue(*parts, value=value)

#___________________________________________________________________________________________________ setOverrides
    def setOverrides(self, overrides):
        if not overrides:
            return False

        for n,v in DictUtils.iter(overrides):
            currentValue = self.get(n)

            # Vector assignment override case
            if currentValue and isinstance(currentValue, Vector3D):
                currentValue = currentValue.clone()
                if isinstance(v, Vector3D):
                    currentValue.updateValues(*v.toList())
                elif v is not None:
                    currentValue.updateValues(x=v, y=v, z=v)
                self.set(n, currentValue)
                self._overrides[n] = currentValue
            else:
                self.set(n, v)
                self._overrides[n] = v

        return True

#___________________________________________________________________________________________________ get
    def get(self, propertyID, default =None):
        parts = propertyID.split('_')

        if parts[0] not in self._configs:
            raise Exception('No %s config exists. Unable to access property %s' % \
                             (parts[0], propertyID))

        return self._getValue(*parts, defaultValue=default)

#___________________________________________________________________________________________________ getOverrides
    def getOverrides(self):
        out = dict()
        for n,v in DictUtils.iter(self._overrides):
            out[n] = v

        return out

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        return self.__class__._toSerializedDict(self._configs)

#___________________________________________________________________________________________________ fromDict
    @classmethod
    def fromDict(cls, src):
        return ConfigReader(configs=cls._fromSerializedDict(src))

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _fromSerializedDict
    @classmethod
    def _fromSerializedDict(cls, src):
        out = dict()
        for n,v in DictUtils.iter(src):
            if isinstance(v, dict):
                if 'objectType' in v:
                    if v['objectType'] == Vector3D.__name__:
                        v = Vector3D.fromSerialDict(v)
                else:
                    v = cls._fromSerializedDict(v)
            out[n] = v

        return out

#___________________________________________________________________________________________________ _toSerializedDict
    @classmethod
    def _toSerializedDict(cls, src):
        out = dict()
        for n,v in DictUtils.iter(src):
            if isinstance(v, Vector3D):
                v = v.toSerialDict()
            elif isinstance(v, dict):
                v = cls._toSerializedDict(v)
            out[n] = v

        return out

#___________________________________________________________________________________________________ _configParserToDict
    def _configParserToDict(self, parser):
        out = dict()
        for section in parser.sections():
            s = dict()
            for opt in parser.options(section):
                value = str(parser.get(section, opt))
                test  = value.lower()

                if test.startswith('"') and test.endswith('"'):
                    value = value[1:-1]

                elif value.startswith(ConfigReader._VECTOR_PREFIX):
                    value = Vector3D.fromConfig(value[len(ConfigReader._VECTOR_PREFIX):-1])

                elif value.startswith(ConfigReader._JSON_PREFIX):
                    value = json.loads(value[len(ConfigReader._JSON_PREFIX):])

                elif StringUtils.isStringType(value) and (value in ['None', 'none', '']):
                    value = None

                elif test in ['on', 'true', 'yes']:
                    value = True
                elif test in ['off', 'false', 'no']:
                    value = False
                elif ConfigReader._NUMERIC_REGEX.match(test):
                    try:
                        value = float(value) if test.find('.') else int(value)
                    except Exception:
                        pass
                s[opt] = value

            out[section] = s

        return out

#___________________________________________________________________________________________________ _getValue
    def _getValue(self, configID, group, key, defaultValue =None):
        config = self._configs.get(configID)
        if not config:
            return defaultValue

        try:
            g = config.get(group)
            if not g:
                return defaultValue
            if key in g:
                return g.get(key)
            else:
                return defaultValue
        except Exception:
            return defaultValue

#___________________________________________________________________________________________________ _setValue
    def _setValue(self, configID, group, key, value):
        config = self._configs.get(configID)
        if not config:
            return False

        try:
            g = config.get(group)
            if not g:
                g = dict()
                config[group] = g
            g[key] = value
        except Exception:
            return False
