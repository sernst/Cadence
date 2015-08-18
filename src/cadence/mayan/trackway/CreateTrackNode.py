# CreateTrackNode.py
# (C)2013-2014
# Kent A. Stevens and Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#_______________________________________________________________________________
class CreateTrackNode(NimbleScriptBase):
    """ A remotely run script to creates a Maya node to represent a specific track. The
        procedure to create the transforms and geometry is createTrackNode in TrackSceneUtils. """

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        uid  = self.fetch('uid', None)
        if uid is None:
            self.putErrorResult(u'Invalid or missing UID. Unable to create track nodeName.')
            return
        node = TrackSceneUtils.createTrackNode(uid)
        self.puts(nodeName=node, props=TrackSceneUtils.getTrackProps(node))
