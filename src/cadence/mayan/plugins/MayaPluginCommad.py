# MayaPluginCommand.py
# (C)2014
# Scott Ernst

import sys

from maya import OpenMaya
from maya import OpenMayaMPx

#___________________________________________________________________________________________________ MayaPluginCommand
class MayaPluginCommand(OpenMayaMPx.MPxCommand):

#===================================================================================================
#                                                                                       C L A S S

    COMMAND_NAME = None

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        self.argData = None

#___________________________________________________________________________________________________ doIt
    def doIt(self, mArgs):
        """ Invoked when the command is run. """
        self.argData = OpenMaya.MArgDatabase(self.syntax(), mArgs)
        self._runImpl()

#___________________________________________________________________________________________________ hasArg
    def hasArg(self, key):
        return self.argData.isFlagSet(key)

#___________________________________________________________________________________________________ register
    @classmethod
    def register(cls, plugin, *args, **kwargs):
        cls._registerImpl(*args, **kwargs)

        # Command instance creation function
        def createCommand():
            return OpenMayaMPx.asMPxPtr(cls())

        # Syntax creation function
        def createSyntax():
            syntax = OpenMaya.MSyntax()
            cls._populateSyntax(syntax)
            return syntax

        try:
            plugin.registerCommand(cls.COMMAND_NAME, createCommand, createSyntax)
        except Exception, err:
            sys.stderr.write('Failed to register command: %s\n' % cls.COMMAND_NAME)
            raise

#___________________________________________________________________________________________________ deregister
    @classmethod
    def deregister(cls, plugin):
        try:
            plugin.deregisterCommand(cls.COMMAND_NAME)
        except:
            sys.stderr.write('Failed to unregister command: %s\n' % cls.COMMAND_NAME)
            raise

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _populateSyntax
    @classmethod
    def _populateSyntax(cls, syntax):
        pass

#___________________________________________________________________________________________________ _registerImpl
    @classmethod
    def _registerImpl(cls, *args, **kwargs):
        pass

#___________________________________________________________________________________________________ _runImpl
    def _runImpl(self):
        pass

