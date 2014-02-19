# VersionInfoCommand.py
# (C)2014
# Scott Ernst

from maya import OpenMaya

from pyaid.ArgsUtils import ArgsUtils

from cadence.mayan.plugins.MayaPluginCommad import MayaPluginCommand

#___________________________________________________________________________________________________ VersionInfoCommand
class VersionInfoCommand(MayaPluginCommand):

#===================================================================================================
#                                                                                       C L A S S

    COMMAND_NAME   = 'cadenceVersionInfo'
    PLUGIN_VERSION = (0, 0, 0, 0)

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        MayaPluginCommand.__init__(self)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _registerImpl
    @classmethod
    def _registerImpl(cls, *args, **kwargs):
        cls.PLUGIN_VERSION = ArgsUtils.get('version', cls.PLUGIN_VERSION, kwargs, args, 0)

#___________________________________________________________________________________________________ _populateSyntax
    @classmethod
    def _populateSyntax(cls, syntax):
        """ Defines the argument and flag syntax for this command. """

        syntax.addFlag('-e', '-echo', OpenMaya.MSyntax.kNoArg)

#___________________________________________________________________________________________________ _runImpl
    def _runImpl(self):
        if self.hasArg('-echo'):
            print 'Cadence Trackway Plugin: %s.%s.%s:%s' % self.PLUGIN_VERSION
        out = OpenMaya.MIntArray()
        for element in self.PLUGIN_VERSION:
            out.append(int(element))
        self.setResult(out)
