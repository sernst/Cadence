# SetNodeDatum.py
# (C)2015
# Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division

from nimble import cmds
from nimble import NimbleScriptBase

#_______________________________________________________________________________
class SetNodeDatum(NimbleScriptBase):
    """ A remote script class for setting the prev and next links for a given set of nodes, passed
        in as a list of 'nodeLinks'.  Each is a tuple (thisNode, prevNode, nextNode).
         --- RETURNS ---
        success:    True if at least one track node is processed else False """

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________

    def run(self, *args, **kwargs):
        """ Sets the prev and next links for a list of node-value pairs that provide information
            about the prev and next to each specified node. """

        nodeValuePairs = self.fetch('nodeValuePairs', None)

        for nodeValuePair in nodeValuePairs:
            node  = nodeValuePair[0]
            value = nodeValuePair[1]
            self.setNodeDatum(node, value)

        self.puts(success=True)
        return

#_______________________________________________________________________________
    def setNodeDatum(self, node, value):
        """ Sets the node's datum value, creating the attribute if not already defined. """

        if not cmds.attributeQuery('datum', node=node, exists=True):
            cmds.addAttr(node, longName='cadence_datum', shortName='datum', niceName='Datum')

        cmds.setAttr(node + '.datum', value)

