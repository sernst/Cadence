# UpdateTrackNode.py
# (C)2014
# Scott Ernst

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from nimble import cmds
from nimble import NimbleScriptBase

from cadence.enums.TrackPropEnum import TrackPropEnum

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#_______________________________________________________________________________
class UpdateTrackNode(NimbleScriptBase):


#===============================================================================
#                                                                   P U B L I C

#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        uid   = self.fetch('uid', None)
        node  = self.fetch('nodeName', None)
        props = self.fetch('props', dict())

        if not uid:
            self.puts(
                success=False, error=True, message='Invalid or missing UID')
            return

        if node and TrackSceneUtils.checkNodeUidMatch(uid, node):
            TrackSceneUtils.setTrackProps(node, props)
            self.puts(success=True, nodeName=node)
            return

        trackSetNode = TrackSceneUtils.getTrackSetNode()
        if not trackSetNode:
            self.puts(
                success=False,
                error=True,
                message='Scene not initialized for Cadence')
            return

        for node in cmds.sets(trackSetNode, query=True):
            if not cmds.hasAttr(node + '.' + TrackPropEnum.UID.maya):
                continue
            if uid == cmds.getAttr(node + '.' + TrackPropEnum.UID.maya):
                TrackSceneUtils.setTrackProps(node, props)
                self.puts(success=True, nodeName=node)
                return

        self.response.puts(success=False)
