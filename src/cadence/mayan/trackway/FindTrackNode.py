# findTrackNode.py
# (C)2014
# Scott Ernst

from nimble import cmds
from nimble import NimbleScriptBase

#___________________________________________________________________________________________________ findTrackNode
class FindTrackNode(NimbleScriptBase):
    """A remote script class for locating a track based on its uid property.
        -> uid          | UID to find within the Maya scene nodes.
        -> [uidKey]     | String name of the maya attribute on which to search. Default 'uid'.

        <- success      | Boolean specifying if the find operation was able to locate a node with
                            the specified uid argument.
        <- [node]       | Node name of the transform node found with the matching uid if such a
                            node was found. """

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ run
    def run(self, *args, **kwargs):
        uidKey = self.getKwarg('uidKey', 'uid')
        uid    = self.getKwarg('uid', None)

        if not uid:
            self.response.put('success', False)
            return

        for xform in cmds.ls(exactType='transform'):
            if not cmds.hasAttr(xform + '.' + uidKey):
                continue
            if uid == cmds.getAttr(xform + '.' + uidKey):
                self.response.puts({'success':True, 'node':xform})

        self.response.put('success', False)

