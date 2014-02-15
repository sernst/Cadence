# findTrackNode.py
# (C)2014
# Scott Ernst

from nimble import cmds
from nimble import NimbleScriptBase

#___________________________________________________________________________________________________ findTrackNode
class FindTrackNode(NimbleScriptBase):
    """A class for..."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ publicMethod
    def run(self):
        """Doc..."""
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

####################################################################################################
####################################################################################################

# Run the script
FindTrackNode().run()
