# CadenceTrackwayPlugin.py
# (C)2014
# Scott Ernst

from maya import OpenMayaMPx

from cadence.mayan.plugins.trackway.commands import VersionInfoCommand
from cadence.mayan.plugins.trackway.nodes import TrackManagerNode

#___________________________________________________________________________________________________ PLUGIN_VERSION
PLUGIN_VERSION = (1, 0, 0, 0)

#___________________________________________________________________________________________________ initializePlugin
def initializePlugin(plugin):
    """ Initialize the script plug-in """
    pluginMFn = OpenMayaMPx.MFnPlugin(plugin)

    reload(TrackManagerNode)
    TrackManagerNode.TrackManagerNode.register(pluginMFn)

    reload(VersionInfoCommand)
    VersionInfoCommand.VersionInfoCommand.register(pluginMFn, version=PLUGIN_VERSION)

#___________________________________________________________________________________________________ uninitializePlugin
def uninitializePlugin(plugin):
    """ Un-initialize the script plug-in """

    pluginMFn = OpenMayaMPx.MFnPlugin(plugin)
    VersionInfoCommand.VersionInfoCommand.deregister(pluginMFn)
    TrackManagerNode.TrackManagerNode.deregister(pluginMFn)
