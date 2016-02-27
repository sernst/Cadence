# CreateTrackNodes.py
# (C)2013-2014
# Kent A. Stevens and Scott Ernst

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from nimble import NimbleScriptBase
from cadence.enums.TrackPropEnum import TrackPropEnum

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#_______________________________________________________________________________
class CreateTrackNodes(NimbleScriptBase):
    """ This is the core script for creating first the TrackSet node then all
        the individual track nodes based on the list that is passed in. """

#===============================================================================
#                                                                      C L A S S

    NO_TRACKLIST = u'noTrackList'

#===============================================================================
#                                                                    P U B L I C

#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        trackList = self.fetch('trackList', None)
        if not trackList:
            self.putErrorResult(
                u'No trackList specified. Unable to create tracks.',
                code=self.NO_TRACKLIST)
            return

        trackSetNode = TrackSceneUtils.getTrackSetNode(createIfMissing=True)
        trackNodeList = dict()
        for track in trackList:
            uid = track.get(TrackPropEnum.UID.maya)
            if not uid:
                continue
            trackNodeList[uid] = TrackSceneUtils.createTrackNode(
                uid, trackSetNode, track)
        self.put('nodes', trackNodeList)

