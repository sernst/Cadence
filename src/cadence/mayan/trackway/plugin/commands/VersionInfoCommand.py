# VersionInfoCommand.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

try:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    from maya import OpenMaya
except Exception:
    maya = None

from pyaid.ArgsUtils import ArgsUtils

from elixir.commands.ElixirCommand import ElixirCommand

#_______________________________________________________________________________
class VersionInfoCommand(ElixirCommand):

#===============================================================================
#                                                                                       C L A S S

    COMMAND_NAME   = 'cadenceVersionInfo'
    PLUGIN_VERSION = (0, 0, 0, 0)

#_______________________________________________________________________________
    def __init__(self):
        ElixirCommand.__init__(self)

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    @classmethod
    def _registerImpl(cls, *args, **kwargs):
        cls.PLUGIN_VERSION = ArgsUtils.get('version', cls.PLUGIN_VERSION, kwargs, args, 0)

#_______________________________________________________________________________
    @classmethod
    def _populateSyntax(cls, syntax):
        """ Defines the argument and flag syntax for this command. """

        syntax.addFlag('-e', '-echo', OpenMaya.MSyntax.kNoArg)

#_______________________________________________________________________________
    def _runImpl(self):
        if self.hasArg('-echo'):
            print('Cadence Trackway Plugin: %s.%s.%s:%s' % self.PLUGIN_VERSION)
        out = OpenMaya.MIntArray()
        for element in self.PLUGIN_VERSION:
            out.append(int(element))
        self.setResult(out)
