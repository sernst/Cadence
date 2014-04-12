# CreateTrackNode.py
# (C)2013-2014
# Kent A. Stevens and Scott Ernst

from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#___________________________________________________________________________________________________ CreateTrackNode
class CreateTrackNode(NimbleScriptBase):
    """ TODO: Kent... """

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ run
    def run(self, *args, **kwargs):
        uid  = self.fetch('uid', None)
        if uid is None:
            self.putErrorResult(u'Invalid or missing UID. Unable to create track nodeName.')
            return
        node = TrackSceneUtils.createTrackNode(uid)
        self.puts(node=node, props=TrackSceneUtils.getTrackProps(node))
