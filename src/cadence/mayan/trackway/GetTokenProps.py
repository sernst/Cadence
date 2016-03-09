# GetTokenProps.py
# (C)2016
# Kent A. Stevens

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#_______________________________________________________________________________
class GetTokenProps(NimbleScriptBase):
    """ A remote script class for locating a token based on its uid property
        and returning its property data.

        uid:            UID to find within the Maya scene nodes.

        <- success      | Boolean specifying if the find operation was able to
                        locate a nodeName with the specified uid argument.
        <- [nodeName]   | Node name of the transform nodeName found with the
                        matching uid if such a nodeName was found. """

#===============================================================================
#                                                                   P U B L I C
#
#_______________________________________________________________________________
    def run(self, *args, **kwargs):

        uid = self.fetch('uid', None)
        if not uid:
            self.puts(success=False, error=True, message='Invalid/missing UID')
            return

        node = TrackSceneUtils.getTokenNode(uid)
        if node:
            self.puts(
                success=True,
                nodeName=node,
                props=TrackSceneUtils.getTokenProps(node))
            return

        self.response.puts(success=False)
