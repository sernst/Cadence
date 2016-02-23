# CreateProxyNode.py
# (C)2013-2016
# Kent A. Stevens and Scott Ernst

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#_______________________________________________________________________________
class CreateProxyNode(NimbleScriptBase):
    """ A remotely run script to creates a Maya node to represent a specific
        proxy track. The procedure to create the transforms and geometry is
        createProxyNode in TrackSceneUtils. """

#===============================================================================
#                                                                   P U B L I C

#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        """ This script first gets the UID and the property list for the given
            proxy node to be created in Maya. """

        props = self.fetch('props')
        TrackSceneUtils.createProxyNode(props)
        self.puts(nodeName=node, props=props)
