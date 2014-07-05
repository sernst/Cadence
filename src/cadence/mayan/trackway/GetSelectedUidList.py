# GetSelectedUidList.py
# (C)2013
# Kent A. Stevens

from nimble import cmds
from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils


#___________________________________________________________________________________________________ GetSelectedUidList
class GetSelectedUidList(NimbleScriptBase):
    """ A remote script class for returning a list of the UIDs for the track nodes currently
     selected in Maya.
         --- RETURNS ---
        success:           True if at least one valid track nodeName selected, else False
        selectedUidList:   (string[]) (default: []) The UIDs of the selected nodes. """

#===================================================================================================
#                                                                                     P U B L I C


#___________________________________________________________________________________________________ run
    def run(self, *args, **kwargs):
        selectedNodes = cmds.ls(selection=True, exactType='transform')

        selectedUidList = list()

        if len(selectedNodes) == 0:
            self.puts(success=False, selectedUidList=selectedUidList)
            return

        for n in selectedNodes:
            uid = TrackSceneUtils.getUid(n)
            if uid is not None:
                selectedUidList.append(uid)
        self.puts(success=True, selectedUidList=selectedUidList)
        return
