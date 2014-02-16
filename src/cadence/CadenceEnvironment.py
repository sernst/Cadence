# CadenceEnvironment.py
# (C)2012-2014
# Scott Ernst

import os

from pyaid.file.FileUtils import FileUtils
from pyaid.string.StringUtils import StringUtils
from pyaid.radix.Base64 import Base64
from pyaid.time.TimeUtils import TimeUtils

#___________________________________________________________________________________________________ CadenceEnvironment
class CadenceEnvironment(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    NIMBLE_IS_ACTIVE = False

    BASE_UNIX_TIME = 1373932675

    _ENV_PATH = os.path.dirname(os.path.abspath(__file__))

    _UID_INDEX = 0

#___________________________________________________________________________________________________ createUniqueId
    @classmethod
    def createUniqueId(cls, prefix = u''):
        """ Creates a universally unique identifier string based on current time, active
            application instance state, and a randomized hash """
        cls._UID_INDEX += 1
        return prefix \
            + TimeUtils.getNowTimecode(cls.BASE_UNIX_TIME) + u'-' \
            + Base64.to64(cls._UID_INDEX) + u'-' \
            + StringUtils.getRandomString(12)

#___________________________________________________________________________________________________ getConfigPath
    @classmethod
    def getConfigPath(cls, folder =None, filename =None):
        return cls._createAbsolutePath('config', folder, filename)

#___________________________________________________________________________________________________ getConfigPath
    @classmethod
    def getDataPath(cls, folder =None, filename =None):
        return cls._createAbsolutePath('data', folder, filename)

#___________________________________________________________________________________________________ getResourcePath
    @classmethod
    def getResourcePath(cls, folder =None, filename =None):
        return cls._createAbsolutePath('resources', folder, filename)

#___________________________________________________________________________________________________ getResourceScriptPath
    @classmethod
    def getResourceScriptPath(cls, *args, **kwargs):
        return FileUtils.createPath(
            cls._ENV_PATH, '..', '..', 'resources', 'scripts', *args, **kwargs)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _createAbsolutePath
    @classmethod
    def _createAbsolutePath(cls, rootFolder, folder, filename):
        p = rootFolder if isinstance(rootFolder, list) else [rootFolder]
        if isinstance(folder, basestring):
            p.append(folder)
        elif isinstance(folder, list):
            p += folder

        if isinstance(filename, basestring):
            p.append(filename)

        out = os.path.join(cls._ENV_PATH, '..', '..', *p)
        if filename or out.split(os.sep)[-1].find('.') > 0:
            return out

        return out + os.sep
