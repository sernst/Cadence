# cadencePlugin.py
# (C)2012 http://cadence.ThreeAddOne.com
# Scott Ernst

from maya.api import OpenMaya
from cadence.mayan.trackway.TrackwayNode import TrackwayNode

# Initialize the script plug-in
def initializePlugin(plugin):
    pluginFn = OpenMaya.MFnPlugin(plugin)
    TrackwayNode.register(pluginFn)

# Uninitialize the script plug-in
def uninitializePlugin(plugin):
    pluginFn = OpenMayaMPx.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(HelloWorldCmd.kPluginCmdName)
    except:
        sys.stderr.write(
            "Failed to unregister command: %s\n" % HelloWorldCmd.kPluginCmdName
        )
        raise