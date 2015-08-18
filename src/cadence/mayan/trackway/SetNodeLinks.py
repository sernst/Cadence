# SetNodeLinks.py
# (C)2015
# Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division

from nimble import cmds
from nimble import NimbleScriptBase

#_______________________________________________________________________________
class SetNodeLinks(NimbleScriptBase):
    """ A remote script class for setting the prev and next links for a given set of nodes, passed
        in as a list of 'nodeLinks'.  Each is a tuple (thisNode, prevNode, nextNode).
         --- RETURNS ---
        success:    True if at least one track node is processed else False """

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        """ Sets the prev and next links for a list of 'nodeLinks' that provide information about
            the prev and next to each specified node. """

        nodeLinks = self.fetch('nodeLinks', None)

        for nodeTriple in nodeLinks:
            node = nodeTriple[0]
            prevNode = nodeTriple[1]
            nextNode = nodeTriple[2]
            self.setNodeLinks(node, prevNode, nextNode)

        self.puts(success=True)
        return

#_______________________________________________________________________________
    def setNodeLinks(self, node, prevNode, nextNode):
        """ Sets up two attributes, prev and next, that directly link the given node to its
            previous and next nodes. """

        if not cmds.attributeQuery('prevNode', node=node, exists=True):
            cmds.addAttr(
                node,
                longName='cadence_prevNode',
                shortName='prevNode',
                dataType='string',
                niceName='PrevNode')

        if not cmds.attributeQuery('nextNode', node=node, exists=True):
            cmds.addAttr(
                node,
                longName='cadence_nextNode',
                shortName='nextNode',
                dataType='string',
                niceName='NextNode')

        if prevNode:
            cmds.setAttr(node + '.prevNode', prevNode, type='string')
        if nextNode:
            cmds.setAttr(node + '.nextNode', nextNode, type='string')
