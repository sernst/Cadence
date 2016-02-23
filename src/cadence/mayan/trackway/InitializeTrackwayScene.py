# InitializeTrackwayScene.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from nimble import cmds
from nimble.mayan.NimbleScriptBase import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

try:
    from cadence.mayan.trackway.plugin import CadenceTrackwayPlugin
except Exception:
    print('[WARNING]: Maya plugin functionality has been disabled')

#_______________________________________________________________________________
class InitializeTrackwayScene(NimbleScriptBase):
    """A class for..."""

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        """Doc..."""

        # Load the Cadence Trackway Plugin
        cmds.loadPlugin(CadenceTrackwayPlugin.__file__)

        # Create the track set nodeName
        trackSetNode = TrackSceneUtils.getTrackSetNode(cls=True,
                                                       createIfMissing=True)
        self.put('trackSet', trackSetNode)

        trackManagerNode = TrackSceneUtils.getTrackManagerNode(
            trackSetNode=trackSetNode,
            createIfMissing=True)
        self.put('trackManager', trackManagerNode)
