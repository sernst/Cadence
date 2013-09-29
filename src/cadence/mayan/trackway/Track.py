# Track.py
# (C)2013
# Kent A. Stevens

import math

from nimble import cmds

from pyaid.reflection.Reflection import Reflection

from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.enum.TrackwayPropEnum import TrackwayPropEnum
from cadence.config.TrackwayShaderConfig import TrackwayShaderConfig
from cadence.util.shading.ShadingUtils import ShadingUtils

#___________________________________________________________________________________________________ Track
class Track(object):

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
#
    def __init__(self, node):
        """Creates a new instance of a Track.  Argument is the string name of the Maya node."""
        self.node  = node

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ updateProperties


#___________________________________________________________________________________________________ hasProp
    def hasProp(self, propName):
        return cmds.attributeQuery(propName, node=self.node, exists=True)

#___________________________________________________________________________________________________ _getTrackPropEnum
    def _getTrackwayPropEnum(self, name):
        for enum in Reflection.getReflectionList(TrackwayPropEnum):
            if enum.name == name:
                return enum
        return None
#___________________________________________________________________________________________________ _getTrackPropEnum
    def _getTrackPropEnum(self, name):
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.name == name:
                return enum
        return None

#___________________________________________________________________________________________________ getTrackwayProp
    def getTrackwayProp(self, p):
        enum = self._getTrackwayPropEnum(p) if isinstance(p, basestring) else p
        if not self.hasProp(enum.name):
            if enum.type == 'string':
                cmds.addAttr(ln=enum.name, dt=enum.type)
            else:
                cmds.addAttr(ln=enum.name, at=enum.type)
        else:
            return cmds.getAttr(self.node + '.' + enum.name)
#___________________________________________________________________________________________________ setTrackwayProp
    def setTrackwayProp(self, p, value):
        enum = self._getTrackwayPropEnum(p) if isinstance(p, basestring) else p

        if not self.hasProp(enum.name):
            if enum.type == 'string':
                cmds.addAttr(ln=p, dt=enum.type)
            else:
                cmds.addAttr(ln=p, at=enum.type)
        if enum.type == "string":
            cmds.setAttr(self.node + '.' + enum.name, value, type="string")
        elif enum.type == "float":
            cmds.setAttr(self.node + '.' + enum.name, value, type="float")

#___________________________________________________________________________________________________ getTrackProp
    def getTrackProp(self, p):
        enum = self._getTrackPropEnum(p) if isinstance(p, basestring) else p
        if not self.hasProp(enum.name):
            if enum.type == 'string':
                cmds.addAttr(ln=enum.name, dt=enum.type)
            else:
                cmds.addAttr(ln=enum.name, at=enum.type)
        if enum.name == TrackPropEnum.NAME.name:
            return self.getName()
        elif enum.name == TrackPropEnum.WIDTH.name:
            return self.getWidth()
        elif enum.name == TrackPropEnum.LENGTH.name:
            return self.getLength()
        elif enum.name == TrackPropEnum.ROTATION.name:
            return self.getRotation()
        elif enum.name == TrackPropEnum.X.name:
            return self.getX()
        elif enum.name == TrackPropEnum.Z.name:
            return self.getZ()
        else:
            return cmds.getAttr(self.node + '.' + enum.name)

#___________________________________________________________________________________________________ setTrackProp
    def setTrackProp(self, p, value):
        enum = self._getTrackPropEnum(p) if isinstance(p, basestring) else p

        print "n setTrackProp for p = %s, enum.name = %s, and enum.type = %s, an value = %s" % (p,
                                                                                                enum.name,
                                                                                                enum.type,
                                                                                                value)
        if not self.hasProp(enum.name):
            if enum.type == 'string':
                cmds.addAttr(ln=p, dt=enum.type)
            else:
                cmds.addAttr(ln=p, at=enum.type)
        if enum.name == TrackPropEnum.NAME.name:
            self.setName(value)
        elif enum.name == TrackPropEnum.WIDTH.name:
            self.setWidth(value)
        elif enum.name == TrackPropEnum.LENGTH.name:
            self.setLength(value)
        elif enum.name == TrackPropEnum.ROTATION.name:
            self.setRotation(value)
        elif enum.name == TrackPropEnum.X.name:
            self.setX(value)
        elif enum.name == TrackPropEnum.Z.name:
            self.setZ(value)
        elif enum.type == "string":
            cmds.setAttr(self.node + '.' + enum.name, value, type="string")
        elif enum.type == "float":
            cmds.setAttr(self.node + '.' + enum.name, value, type="float")

#___________________________________________________________________________________________________ setTrackwayProperties
    def setTrackwayProperties(self, dictionary):
        for prop,value in dictionary.iteritems():
            self.setTrackwayProp(prop, value)

#___________________________________________________________________________________________________ setTrackProperties
    def setTrackProperties(self, dictionary):
        for prop,value in dictionary.iteritems():
            self.setTrackProp(prop, value)

#___________________________________________________________________________________________________ getName
    def getName(self):
        return cmds.getAttr(self.node + "." + TrackPropEnum.NAME.name)

#___________________________________________________________________________________________________ setName
    def setName(self, name):
        cmds.setAttr(self.node + '.' + TrackPropEnum.NAME.name, name, type="string")
        if name != "":
            self.colorTrack()

#___________________________________________________________________________________________________ getWidth
    def getWidth(self):
        return cmds.getAttr(self.node + '.scaleX')

#___________________________________________________________________________________________________ setWidth
    def setWidth(self, width):
        cmds.setAttr(self.node + '.scaleX', width)

#___________________________________________________________________________________________________ getLength
    def getLength(self):
        return cmds.getAttr(self.node + '.scaleZ')

#___________________________________________________________________________________________________ setLength
    def setLength(self, length):
        cmds.setAttr(self.node + '.scaleZ', length)

#___________________________________________________________________________________________________ getDimensions
    def getDimensions(self):
        return [self.getWidth(), self.getLength()]

#___________________________________________________________________________________________________ setDimensions
    def setDimensions(self, width, length):
        self.setLength(length)
        self.setWidth(width)

#___________________________________________________________________________________________________ getRotation
    def getRotation(self):
        return cmds.getAttr(self.node + '.rotateY')

#___________________________________________________________________________________________________ setRotation
    def setRotation(self, rotation):
        cmds.setAttr(self.node + '.ry', rotation)

#___________________________________________________________________________________________________ getX
    def getX(self):
        return cmds.getAttr(self.node + '.translateX')

#___________________________________________________________________________________________________ setX
    def setX(self, x):
       cmds.setAttr(self.node + '.translateX', x)

#___________________________________________________________________________________________________ getZ
    def getZ(self):
       return cmds.getAttr(self.node + '.translateZ')

#___________________________________________________________________________________________________ setZ
    def setZ(self, z):
       cmds.setAttr(self.node + '.translateZ', z)

#___________________________________________________________________________________________________ getPosition
    def getPosition(self):
       return (self.getX(), self.getZ())

#___________________________________________________________________________________________________ setPosition
    def setPosition(self, x, z):
       self.setX(x)
       self.setZ(z)

#___________________________________________________________________________________________________ moveRelative
    def moveRelative(self, dx, dy, dz):
        cmds.move(dx, dy, dz, self.node, relative=True)

#___________________________________________________________________________________________________ colorTrack
    def colorTrack(self):
        if self.getName()[1] == 'M':
            ShadingUtils.applyShader(TrackwayShaderConfig.LIGHT_GRAY_COLOR, self.node)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.DARK_GRAY_COLOR, self.node)
        if self.getName()[0] == 'R':
            ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, self.node +"|pointer")
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR, self.node +"|pointer")

#___________________________________________________________________________________________________ isPes
    def isPes(self):
        return self.getName()[1] == 'P'

#___________________________________________________________________________________________________ isManus
    def isManus(self):
        return self.getName()[0] == 'M'

#___________________________________________________________________________________________________ isRight
    def isRight(self):
        return self.getName()[0] == 'R'

#___________________________________________________________________________________________________ isLeft
    def isLeft(self):
        return self.getName()[1] == 'L'

#___________________________________________________________________________________________________ getPrevTrack
    def getPrevTrack(self):
        connections = cmds.listConnections(self.node + '.' + TrackPropEnum.PREV_TRACK.name,
                                           s=True,
                                           p=True)
        if connections:
            for c in connections:
                if c.endswith('.message'):
                    node = c.split('.')[0]
                    return Track(node)
        return None

#___________________________________________________________________________________________________ getNext
    def getNextTrack(self):
        connections = cmds.listConnections(self.node + '.message', d=True, p=True)
        if connections:
            for c in connections:
                if c.endswith('.' + TrackPropEnum.PREV_TRACK.name):
                    node = c.split('.')[0]
                    return Track(node)
        return None

#___________________________________________________________________________________________________ link
    def link(self, prevTrack):
        self.unlink()
        p = prevTrack.node
        cmds.connectAttr(p + '.message', self.node + '.' + TrackPropEnum.PREV_TRACK.name, f=True)

#___________________________________________________________________________________________________ unlink
    def unlink(self):
        p = self.getPrevTrack()
        if not p:
            return
        cmds.disconnectAttr(p.node + '.message', self.node + '.' + TrackPropEnum.PREV_TRACK.name)

#___________________________________________________________________________________________________ setFocus
    def setCadenceCamFocus(self):
        if not cmds.objExists('CadenceCam'):
            self.initializeCadenceCam()
        height = cmds.xform('CadenceCam', query=True, translation=True)[1]
        cmds.move(self.getX(), height, self.getZ(), 'CadenceCam', absolute=True)

#___________________________________________________________________________________________________ createNode
    @classmethod
    def createNode(cls):
        r = 50
        a = 2.0*r
        y = (0, 1, 0)
        c = cmds.polyCylinder(r=r, h=5, sx=40, sy=1, sz=1, ax=y, rcp=0, cuv=2, ch=1, n='track0')[0]

        for item in Reflection.getReflectionList(TrackPropEnum):
            if item.type == 'string':
                cmds.addAttr(ln=item.name, dt=item.type)
            else:
                cmds.addAttr(ln=item.name, at=item.type)

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

        return c

#___________________________________________________________________________________________________ initializeCadenceCam
    @classmethod
    def initializeCadenceCam(cls):
        c = cmds.camera(orthographic=True,
                        nearClipPlane=1,
                        farClipPlane=100000,
                        orthographicWidth=300)
        cmds.rename(c[0], 'CadenceCam')
        cmds.rotate(-90, 180, 0)
        cmds.move(0, 100, 0, 'CadenceCam', absolute=True)

#___________________________________________________________________________________________________ incrementName
    @classmethod
    def incrementName(cls, name):
        prefix = name[:2]
        number = int(name[2:])
        return prefix + str(number + 1)

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return unicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % "%s [%s]" % (self.node, self.getName())

