# CreateTrackNode.py
# (C)2013-2014
# Kent A. Stevens and Scott Ernst

import math

from nimble import cmds
from nimble import NimbleScriptBase
from cadence.enum.TrackPropEnum import TrackPropEnum

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#___________________________________________________________________________________________________ CreateTrackNode
class CreateTrackNode(NimbleScriptBase):
    """ TODO: Kent... """

#===================================================================================================
#                                                                                     P U B L I C

    RADIUS = 50
    Y_VEC  = (0, 1, 0)

#___________________________________________________________________________________________________ run
    def run(self, *args, **kwargs):
        uid  = self.fetch('uid', None)
        node = TrackSceneUtils.getTrackNode(uid)
        if node:
            self.puts(node=node, props=TrackSceneUtils.getTrackProps(node))
            return

        a    = 2.0*self.RADIUS
        node = cmds.polyCylinder(
            r=self.RADIUS, h=5, sx=40, sy=1, sz=1, ax=self.Y_VEC, rcp=0, cuv=2, ch=1, n='track0')[0]

        p = cmds.polyPrism(l=4, w=a, ns=3, sh=1, sc=0, ax=self.Y_VEC, cuv=3, ch=1, n='pointer')[0]

        cmds.rotate(0.0, -90.0, 0.0)
        cmds.scale(1.0/math.sqrt(3.0), 1.0, 1.0)
        cmds.move(0, 5, a/6.0)

        cmds.setAttr(p + '.overrideEnabled', 1)
        cmds.setAttr(p + '.overrideDisplayType', 2)

        cmds.parent(p, node)

        cmds.select(node)
        cmds.addAttr(
            longName='cadence_uniqueId',
            shortName=TrackPropEnum.UID.maya,
            dataType='string',
            niceName='Unique ID')

        props = self.fetch('props', {})
        if props:
            TrackSceneUtils.setTrackProps(node, props)

        # Add the new node to the Cadence track scene set
        trackSetNode = TrackSceneUtils.getTrackSetNode()
        cmds.sets(node, add=trackSetNode)

        self.puts(node=node, props=TrackSceneUtils.getTrackProps(node))
