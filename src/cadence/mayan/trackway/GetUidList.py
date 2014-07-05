# GetUidList.py
# (C)2014
# Kent A. Stevens

from nimble import cmds
from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils


#___________________________________________________________________________________________________ GetUidList
class GetUidList(NimbleScriptBase):
    """ A remote script class for returning a list of the UIDs for all track nodes in Maya.
         --- RETURNS ---
        success:    True if at least one valid track node is found, else False
        UidList:    (string[]) (default: []) The list of all UIDs. """

#===================================================================================================
#                                                                                     P U B L I C


#___________________________________________________________________________________________________ run
    def run(self, *args, **kwargs):
        """ Fetches the nodes in the current trackSetNode, then for each such node, appends its UID
            to a list l which is then returned. """
        setNode = TrackSceneUtils.getTrackSetNode()
        nodes = cmds.sets(setNode, q=True)

        if len(nodes) == 0:
            self.puts(success=False, uidList=[])
            return

        l = []
        for n in nodes:
            uid = TrackSceneUtils.getUid(node=n, trackSetNode=setNode)
            if uid is not None:
                l.append(uid)

        self.puts(success=True, uidList=l)
        return
