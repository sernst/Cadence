# ConfigReader.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import os
import sys
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
    DEFAULT_CONFIG_PATH     = sys.path.append(os.path.dirname(os.path.abspath(__file__)) +
                                               '/../../../../config/')

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of ConfigReader."""
        self._configPath        = ArgsUtils.get('configPath', ConfigReader.DEFAULT_CONFIG_PATH, kwargs)
        self._generalFilename   = ArgsUtils.getFrom('files', 'general', None, kwargs)
        self._general           = ArgsUtils.get('general', None, kwargs)
        self._skeletonFilename  = ArgsUtils.getFrom('files', 'skeleton', None, kwargs)
        self._skeleton          = ArgsUtils.get('skeleton', None, kwargs)
        self._gaitFilename      = ArgsUtils.getFrom('files', 'gait', None, kwargs)
        self._gait              = ArgsUtils.get('gait', None, kwargs)

        configs = (
            ('general', ConfigReader.DEFAULT_GENERAL_CONFIG),
            ('skeleton', ConfigReader.DEFAULT_SKELETON_CONFIG),
            ('gait', ConfigReader.DEFAULT_GAIT_CONFIG),
        )

        for cfg in configs:
            # Allows for overriding the loading of configs through constructor arguments.
            if getattr(self, '_' + cfg[0]) is not None:
                continue

            filename = kwargs.get(cfg[0] + 'File', cfg[1])
            parser   = ConfigParser.ConfigParser()
            if os.path.exists(filename):
                parser.read(filename)
            else:
                raise Exception, cfg[0] + ' config file does not exist!'

            setattr(self, '_' + cfg[0] + 'Filename', filename)
            setattr(self, '_' + cfg[0], parser)


#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: configPath
    @property
    def configPath(self):
        return self._configPath
    @configPath.setter
    def configPath(self, value):
        self._configPath = value

#___________________________________________________________________________________________________ GS: skeletonFilename
    @property
    def skeletonFilename(self):
        return self._skeletonFilename if self._skeletonFilename.startswith('/') else \
            os.path.join(self.configPath, self.skeletonFilename)

#___________________________________________________________________________________________________ GS: generalFile
    @property
    def generalFilename(self):
        return self._generalFilename if self._generalFilename.startswith('/') else \
            os.path.join(self._configPath, self._generalFilename)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ get
    def get(self, propertyID, reps =None):
        parts = propertyID.split('_')

        if reps:
            for n,v in reps.iteritems():
                for i in range(0, len(parts)):
                    parts[i] = parts[i].replace(n, v)

        return self._getValue(*parts)

#___________________________________________________________________________________________________ getGeneralValue
    def getGeneralValue(self, group, key):
        return self._getValue(ConfigReader.GENERAL_CONFIG_ID, group, key)

#___________________________________________________________________________________________________ getSkeletonValue
    def getSkeletonValue(self, group, key):
        return self._getValue(ConfigReader.SKELETON_CONFIG_ID, group, key)

#___________________________________________________________________________________________________ getGaitValue
    def getGaitValue(self, group, key):
        return self._getValue(ConfigReader.GAIT_CONFIG_ID, group, key)

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        return {
            'general':self._general,
            'skeleton':self._skeleton,
            'gait':self._gait,
            'files':{
                'general':self._generalFilename,
                'skeleton':self._skeletonFilename,
                'gait':self._gaitFilename
            }
        }

#___________________________________________________________________________________________________ fromDict
    @classmethod
    def fromDict(cls, src):
        return ConfigReader(**src)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getValue
    def _getValue(self, configID, group, key):
        if configID == ConfigReader.SKELETON_CONFIG_ID:
            config = self._skeleton
        elif configID == ConfigReader.GAIT_CONFIG_ID:
            config = self._gait
        else:
            config = self._general

        try:
            return config.get(group, key)
        except Exception, err:
            return None
