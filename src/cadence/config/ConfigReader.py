# ConfigReader.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import re
import os
import ConfigParser

from cadence.util.ArgsUtils import ArgsUtils

#___________________________________________________________________________________________________ ConfigReader
class ConfigReader(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    GENERAL_CONFIG_ID        = 'general'
    SKELETON_CONFIG_ID       = 'skeleton'
    GAIT_CONFIG_ID           = 'gait'

    DEFAULT_GENERAL_CONFIG  = 'general/default.cfg'
    DEFAULT_SKELETON_CONFIG = 'skeleton/default.cfg'
    DEFAULT_GAIT_CONFIG     = 'gaits/default.cfg'
    DEFAULT_CONFIG_PATH     = os.path.dirname(os.path.abspath(__file__)) + '/../../../config/'

    _NUMERIC_REGEX = re.compile('^[-\.0-9]+$')

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of ConfigReader."""
        self._configs     = ArgsUtils.get('configs', dict(), kwargs)
        self._filenames   = ArgsUtils.get('filenames', None, kwargs)
        self._configPath  = ArgsUtils.get('rootConfigPath', ConfigReader.DEFAULT_CONFIG_PATH, kwargs)

        if self._filenames:
            for n,v in self._filenames.iteritems():
                path     = os.path.join(self._configPath, v)
                if not path.endswith('.cfg'):
                    path += '.cfg'

                parser = ConfigParser.ConfigParser()
                if os.path.exists(path):
                    parser.read(path)
                else:
                    raise Exception, path + ' config file does not exist!'

                self._configs[n] = self._configParserToDict(parser)

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

#___________________________________________________________________________________________________ get
    def get(self, propertyID, default =None, reps =None):
        parts = propertyID.split('_')

        if parts[0] not in self._configs:
            raise Exception, 'No %s config exists. Unable to access property %s' % \
                             (parts[0], propertyID)

        if reps:
            for n,v in reps.iteritems():
                for i in range(0, len(parts)):
                    parts[i] = parts[i].replace(n, v)

        return self._getValue(*parts, defaultValue=default)

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        return self._configs

#___________________________________________________________________________________________________ fromDict
    @classmethod
    def fromDict(cls, src):
        return ConfigReader(configs=src)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _configParserToDict
    def _configParserToDict(self, parser):
        out = dict()
        for section in parser.sections():
            s = dict()
            for opt in parser.options(section):
                value = parser.get(section, opt)
                test = str(value).lower()
                if test.startswith('"') and test.endswith('"'):
                    value = value[1:-1]

                if isinstance(value, basestring) and (value in ['None', 'none', '']):
                    value = None

                if test in ['on', 'true', 'yes']:
                    value = True
                elif test in ['off', 'false', 'no']:
                    value = False
                elif ConfigReader._NUMERIC_REGEX.match(test):
                    try:
                        value = float(value) if test.find('.') else int(value)
                    except Exception, err:
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
            return g.get(key)
        except Exception, err:
            return defaultValue