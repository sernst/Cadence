# VersionInfoCommand.py
# (C)2014
# Scott Ernst

from maya import OpenMaya

from pyaid.ArgsUtils import ArgsUtils

from elixir.commands.ElixirCommand import ElixirCommand

#___________________________________________________________________________________________________ VersionInfoCommand
class VersionInfoCommand(ElixirCommand):

#===================================================================================================
#                                                                                       C L A S S

    COMMAND_NAME = 'cadenceFindTrackNode'

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        ElixirCommand.__init__(self)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _populateSyntax
    @classmethod
    def _populateSyntax(cls, syntax):
        """ Defines the argument and flag syntax for this command. """

        syntax.addFlag('-tm', '-trackManager', OpenMaya.MSyntax.kString)

#___________________________________________________________________________________________________ _runImpl
    def _runImpl(self):
        if not self.hasArg('-trackManager'):
            OpenMaya.MItDependencyNodes()
            pass

        if self.hasArg('-echo'):
            print 'Cadence Trackway Plugin: %s.%s.%s:%s' % self.PLUGIN_VERSION
        out = OpenMaya.MIntArray()
        for element in self.PLUGIN_VERSION:
            out.append(int(element))
        self.setResult(out)

