# GetTrackNodeData.py
# (C)2014
# Scott Ernst

from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#___________________________________________________________________________________________________ GetTrackNodeData
class GetTrackNodeData(NimbleScriptBase):
    """ A remote script class for locating a track based on its uid property and returning its
        property data.

        uid:        UID to find within the Maya scene nodes.
        [node]:     Name of the node for the specified uid if one has been cached.

        <- success      | Boolean specifying if the find operation was able to locate a node with
                            the specified uid argument.
        <- [node]       | Node name of the transform node found with the matching uid if such a
                            node was found. """

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ run
    def run(self, *args, **kwargs):
        uid  = self.fetch('uid', None)
        node = self.fetch('node', None)

        if not uid:
            self.puts(success=False, error=True, message='Invalid or missing UID')
            return

        if node and TrackSceneUtils.checkNodeUidMatch(uid, node):
            self.puts(success=True, node=node, props=TrackSceneUtils.getTrackProps(node))
            return

        node = TrackSceneUtils.getTrackNode(uid)
        if node:
            self.puts(success=True, node=node, props=TrackSceneUtils.getTrackProps(node))
            return

        self.response.puts(success=False)

