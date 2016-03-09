# GetTrackNodeProps.py
# (C)2014-2016
# Scott Ernst

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#_______________________________________________________________________________
class GetTrackNodeProps(NimbleScriptBase):
    """ A remote script class for locating a track based on its uid property
        and returning its property data.

        uid:            UID to find within the Maya scene nodes.
        [nodeName]:     Name of the nodeName for the specified uid if one has
                        been cached.

        <- success      | Boolean specifying if the find operation was able to
                        locate a nodeName with the specified uid argument.
        <- [nodeName]   | Node name of the transform nodeName found with the
                        matching uid if such a nodeName was found. """

#===============================================================================
#                                                                   P U B L I C
#
#_______________________________________________________________________________
    def run(self, *args, **kwargs):

        uid  = self.fetch('uid', None)
        node = self.fetch('nodeName', None)

        if not uid:
            self.puts(
                success=False,
                error=True,
                message='Invalid or missing UID')
            return

        if node and TrackSceneUtils.checkNodeUidMatch(uid, node):
            self.puts(
                success=True,
                nodeName=node,
                props=TrackSceneUtils.getTrackProps(node))
            return

        node = TrackSceneUtils.getTrackNode(uid)
        if node:
            self.puts(
                success=True,
                nodeName=node,
                props=TrackSceneUtils.getTrackProps(node))
            return

        self.response.puts(success=False)
