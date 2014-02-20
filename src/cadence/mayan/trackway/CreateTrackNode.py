# CreateTrackNode.py
# (C)2013-2014
# Kent A. Stevens and Scott Ernst

import math

from nimble import cmds
from nimble import NimbleScriptBase

#___________________________________________________________________________________________________ findTrackNode
class CreateTrackNode(NimbleScriptBase):
    """ TODO: Kent... """

#===================================================================================================
#                                                                                     P U B L I C

    RADIUS = 50
    Y_VEC  = (0, 1, 0)

#___________________________________________________________________________________________________ run
    def run(self, *args, **kwargs):
        a = 2.0*self.RADIUS
        c = cmds.polyCylinder(
            r=self.RADIUS, h=5, sx=40, sy=1, sz=1, ax=self.Y_VEC, rcp=0, cuv=2, ch=1, n='track0')[0]

        for item in self.getKwarg('trackProps', []):
            if item['intrinsic']:
                continue

            if item['type'] == 'string':
                cmds.addAttr(ln=item['name'], dt=item['type'])
            else:
                cmds.addAttr(ln=item['name'], at=item['type'])

        cmds.addAttr(ln='prevTrack', at='message')

        p = cmds.polyPrism(l=4, w=a, ns=3, sh=1, sc=0, ax=self.Y_VEC, cuv=3, ch=1, n='pointer')[0]

        cmds.rotate(0.0, -90.0, 0.0)
        cmds.scale(1.0/math.sqrt(3.0), 1.0, 1.0)
        cmds.move(0, 5, a/6.0)

        cmds.setAttr(p + '.overrideEnabled', 1)
        cmds.setAttr(p + '.overrideDisplayType', 2)

        cmds.parent(p, c)
        cmds.select(c)
        cmds.setAttr(c + '.translateY', l=1)
        cmds.setAttr(c + '.rotateX',    l=1)
        cmds.setAttr(c + '.rotateZ',    l=1)
        cmds.setAttr(c + '.scaleY',     l=1)

        self.response.put('name', c)


