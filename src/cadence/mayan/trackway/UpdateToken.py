# UpdateToken.py
# (C)2016
# Kent A. Stevens

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from nimble import cmds
from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#_______________________________________________________________________________
class UpdateToken(NimbleScriptBase):


#===============================================================================
#                                                                   P U B L I C
#
#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        uid   = self.fetch('uid', None)
        props = self.fetch('props', dict())

        if not uid:
            self.puts(
                success=False, error=True, message='Invalid or missing UID')
            return

        trackSetNode = TrackSceneUtils.getTrackSetNode()
        if not trackSetNode:
            self.puts(
                success=False,
                error=True,
                message='Scene not initialized for Cadence')
            return

        for node in cmds.sets(trackSetNode, query=True):
            if not cmds.hasAttr(node + '.track_uid'):
                continue
            if uid == cmds.getAttr(node + '.track_uid'):
                TrackSceneUtils.setTokenProps(node, props)
                self.puts(success=True, nodeName=node)
                return

        self.response.puts(success=False)
