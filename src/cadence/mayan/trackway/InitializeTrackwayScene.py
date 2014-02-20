# InitializeTrackwayScene.py
# (C)2014
# Scott Ernst

from nimble import cmds
from nimble.mayan.NimbleScriptBase import NimbleScriptBase

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.mayan.trackway.plugin import CadenceTrackwayPlugin

#___________________________________________________________________________________________________ InitializeTrackwayScene
class InitializeTrackwayScene(NimbleScriptBase):
    """A class for..."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ run
    def run(self, *args, **kwargs):
        """Doc..."""
        if self._checkScene():
            return

        # Load the Cadence Trackway Plugin
        cmds.loadPlugin(CadenceTrackwayPlugin.__file__)

        # Create the track manager node
        node = cmds.createNode('trackManager')
        self.put('trackManager', node)

        # Create the track set
        trackSet = cmds.sets(name=CadenceEnvironment.TRACKWAY_SET_NODE_NAME, empty=True)
        self.put('trackSet', trackSet)

        # Connect the manager and set nodes
        cmds.connectAttr(node + '.trackSet', trackSet + '.usedBy', force=True)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _checkScene
    def _checkScene(self):
        trackSet = None
        for s in cmds.ls(exactType='objectSet'):
            if s == CadenceEnvironment.TRACKWAY_SET_NODE_NAME:
                trackSet = s
                break

        if trackSet is None:
            return False

        self.put('trackSet', trackSet)

        trackManager = None
        for node in cmds.listConnections(trackSet + '.usedBy', source=True, destination=False):
            if cmds.nodeType(node) == 'trackManager':
                trackManager = node
                break

        if trackManager is None:
            return False

        self.put('trackManager', trackManager)

        return True
