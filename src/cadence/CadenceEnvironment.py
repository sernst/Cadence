# CadenceEnvironment.py
# (C)2012-2014
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import os

from pyaid.file.FileUtils import FileUtils
from pyaid.string.StringUtils import StringUtils
from pyaid.radix.Base64 import Base64
from pyaid.time.TimeUtils import TimeUtils

try:
    from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
except Exception:
    # Handles the in-maya case where PyGlassEnvironment cannot be
    # successfully imported
    PyGlassEnvironment = None

#_______________________________________________________________________________
class CadenceEnvironment(object):
    """A class for..."""

#===============================================================================
#                                                                   C L A S S

    APP_ID = 'Cadence'

    # Whether or not the Maya ENV files have been properly initialized with
    # source paths for Cadence's dependent libraries
    MAYA_IS_INITIALIZED = False

    # Whether or not the Cadence Maya plugins have been initialized for use
    PLUGINS_ARE_ACTIVE  = False

    # Whether or not an active Nimble connection has been established with a
    # Maya application running a Nimble server
    NIMBLE_IS_ACTIVE    = False

    BASE_UNIX_TIME      = 1373932675

    ENV_PATH = os.path.dirname(os.path.abspath(__file__))

    _UID_INDEX = 0

#_______________________________________________________________________________
    @classmethod
    def createUniqueId(cls, prefix = u''):
        """ Creates a universally unique identifier string based on current
            time, active application instance state, and a randomized hash
        """
        cls._UID_INDEX += 1
        return '%s%s-%s-%s' % (
            prefix,
            TimeUtils.getNowTimecode(cls.BASE_UNIX_TIME),
            Base64.to64(cls._UID_INDEX),
            StringUtils.getRandomString(12))

#_______________________________________________________________________________
    @classmethod
    def getConfigPath(cls, *args, **kwargs):
        return cls.getPath('config', *args, **kwargs)

#_______________________________________________________________________________
    @classmethod
    def getDataPath(cls, *args, **kwargs):
        return cls.getPath('data', *args, **kwargs)

#_______________________________________________________________________________
    @classmethod
    def getResourcePath(cls, *args, **kwargs):
        return cls.getPath('resources', *args, **kwargs)

#_______________________________________________________________________________
    @classmethod
    def getPath(cls, *args, **kwargs):
        """getPath doc..."""
        return FileUtils.createPath(
            cls.ENV_PATH, '..', '..', *args, **kwargs)

#_______________________________________________________________________________
    @classmethod
    def getResourceScriptPath(cls, *args, **kwargs):
        return cls.getResourcePath('scripts', *args, **kwargs)

#_______________________________________________________________________________
    @classmethod
    def getAppResourcePath(cls, *args, **kwargs):
        """getAppResourcePath doc..."""
        return PyGlassEnvironment.getRootResourcePath(
            'apps', cls.APP_ID, *args, **kwargs)

#_______________________________________________________________________________
    @classmethod
    def getLocalAppResourcePath(cls, *args, **kwargs):
        """getLocalAppResourcePath doc..."""
        return PyGlassEnvironment.getRootLocalResourcePath(
            'apps', cls.APP_ID, *args, **kwargs)
