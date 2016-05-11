# DeleteTo6
# Kent A. Stevens

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from nimble import cmds
from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils


#_______________________________________________________________________________
class DeleteTokens(NimbleScriptBase):
    """ A remote script class for deleting all tokens and their annotations"""

#===============================================================================
#                                                                   P U B L I C


#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        """ Fetches the nodes in the current trackSetNode, then for each such
            node, those that start with 'Token' are deleted. """

        setNode = TrackSceneUtils.getTrackSetNode()
        nodes   = cmds.sets(setNode, q=True)

        if len(nodes) == 0:
            self.puts(success=False, uidList=[])
            return

        for node in nodes:
            if node.startswith('Token'):
                cmds.delete(node)

        # and remove the annotations (objects with name starting with 'Token'
        objects = cmds.ls(transforms=True)
        for object in objects:
            if object.startswith('Token'):
                cmds.delete(object)
        return
