# CreateToken.py
# (C)2013-2016
# Kent A. Stevens and Scott Ernst

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#_______________________________________________________________________________
class CreateToken(NimbleScriptBase):
    """ A remotely run script to creates a Maya scene node to represent a
        specific token. The procedure to create the transforms and geometry is
        createToken in TrackSceneUtils. """

#===============================================================================
#                                                                   P U B L I C
#
#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        """ This script first gets the UID and the property list for the given
            proxy node to be created in Maya. """

        uid   = self.fetch('uid', None)
        props = self.fetch('props', None)

        if uid is None:
            self.putErrorResult(
                u'Invalid or missing UID. Unable to create token.')
            return

        node = TrackSceneUtils.createToken(uid, props=props)
        self.puts(nodeName=node, props=props)