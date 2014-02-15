# createTrackNode.py
# (C)2013
# Kent A. Stevens and Scott Ernst

import math

import nimble
from nimble import cmds

kwargs  = nimble.getRemoteKwargs(globals())
r       = 50
a       = 2.0*r
y       = (0, 1, 0)
c       = cmds.polyCylinder(r=r, h=5, sx=40, sy=1, sz=1, ax=y, rcp=0, cuv=2, ch=1, n='track0')[0]

for item in kwargs.get('trackProps'):
    if item['intrinsic']:
        continue
    if item['type'] == 'string':
        cmds.addAttr(ln=item['name'], dt=item['type'])
    else:
        cmds.addAttr(ln=item['name'], at=item['type'])
cmds.addAttr(ln='prevTrack', at='message')

p = cmds.polyPrism(l=4, w=a, ns=3, sh=1, sc=0, ax=y, cuv=3, ch=1, n='pointer')[0]

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

response = nimble.createRemoteResponse(globals())
response.put('name', c)
