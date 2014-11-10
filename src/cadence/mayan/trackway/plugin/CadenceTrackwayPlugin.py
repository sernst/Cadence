# CadenceTrackwayPlugin.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.ModuleUtils import ModuleUtils

try:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    from maya import OpenMayaMPx
except Exception:
    maya = None

from cadence.mayan.trackway.plugin.commands import VersionInfoCommand
from cadence.mayan.trackway.plugin.nodes import TrackManagerNode

#___________________________________________________________________________________________________ PLUGIN_VERSION
PLUGIN_VERSION = (1, 0, 0, 0)

#___________________________________________________________________________________________________ initializePlugin
def initializePlugin(plugin):
    """ Initialize the script plug-in """
    pluginMFn = OpenMayaMPx.MFnPlugin(plugin)

    ModuleUtils.reloadModule(TrackManagerNode)
    TrackManagerNode.TrackManagerNode.register(pluginMFn)

    ModuleUtils.reloadModule(VersionInfoCommand)
    VersionInfoCommand.VersionInfoCommand.register(pluginMFn, version=PLUGIN_VERSION)

#___________________________________________________________________________________________________ uninitializePlugin
def uninitializePlugin(plugin):
    """ Un-initialize the script plug-in """

    pluginMFn = OpenMayaMPx.MFnPlugin(plugin)
    VersionInfoCommand.VersionInfoCommand.deregister(pluginMFn)
    TrackManagerNode.TrackManagerNode.deregister(pluginMFn)
