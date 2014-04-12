# InitializeTrackwayScene.py
# (C)2014
# Scott Ernst

from nimble import cmds
from nimble.mayan.NimbleScriptBase import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils
from cadence.mayan.trackway.plugin import CadenceTrackwayPlugin

#___________________________________________________________________________________________________ InitializeTrackwayScene
class InitializeTrackwayScene(NimbleScriptBase):
    """A class for..."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ run
    def run(self, *args, **kwargs):
        """Doc..."""

        # Load the Cadence Trackway Plugin
        cmds.loadPlugin(CadenceTrackwayPlugin.__file__)

        # Create the track set nodeName
        trackSetNode = TrackSceneUtils.getTrackSetNode(createIfMissing=True)
        self.put('trackSet', trackSetNode)

        trackManagerNode = TrackSceneUtils.getTrackManagerNode(
            trackSetNode=trackSetNode,
            createIfMissing=True)
        self.put('trackManager', trackManagerNode)
