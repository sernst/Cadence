# Track.py
# (C)2013
# Kent A. Stevens

import math

from pyaid.reflection.Reflection import Reflection

from nimble import cmds

from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.config.TrackwayShaderConfig import TrackwayShaderConfig
from cadence.util.shading.ShadingUtils import ShadingUtils

#___________________________________________________________________________________________________ Track
class Track(object):
    """ A track object wraps a reference to a Maya node (it's string name). A track has properties
    that are stored in the node, as string attributes, or floats, or directly by the values of the
    transforms."""
#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, node):
        """Creates a new instance of a Track.  Argument is the string name of the Maya node."""
        self.node  = node

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ updateProperties


#___________________________________________________________________________________________________ nodeHasAttribute
    def nodeHasAttribute(self, attribute):
        return cmds.attributeQuery(attribute, node=self.node, exists=True)

#___________________________________________________________________________________________________ _getTrackPropEnum
    def _getTrackPropEnum(self, name):
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.name == name:
                return enum
        return None

#___________________________________________________________________________________________________ getProperty
    def getProperty(self, p):
        enum = self._getTrackPropEnum(p) if isinstance(p, basestring) else p

        name = enum.name
        if name == TrackPropEnum.NAME.name:
            return self.getName()
        elif name == TrackPropEnum.WIDTH.name:
            return self.getWidth()
        elif name == TrackPropEnum.LENGTH.name:
            return self.getLength()
        elif name == TrackPropEnum.ROTATION.name:
            return self.getRotation()
        elif name == TrackPropEnum.X.name:
            return self.getX()
        elif name == TrackPropEnum.Z.name:
            return self.getZ()
        if not self.nodeHasAttribute(name):
            return None
        else:
            return cmds.getAttr(self.node + '.' + name)

#___________________________________________________________________________________________________ setProperty
    def setProperty(self, p, value):
        enum = self._getTrackPropEnum(p) if isinstance(p, basestring) else p

        name = enum.name
        type = enum.type
        if name == TrackPropEnum.NAME.name:
            self.setName(value)
        elif name == TrackPropEnum.WIDTH.name:
            self.setWidth(value)
        elif name == TrackPropEnum.LENGTH.name:
            self.setLength(value)
        elif name == TrackPropEnum.ROTATION.name:
            self.setRotation(value)
        elif name == TrackPropEnum.X.name:
            self.setX(value)
        elif name == TrackPropEnum.Z.name:
            self.setZ(value)
        elif type == "string":
            if not self.nodeHasAttribute(name):
                cmds.addAttr(ln=name, dt=type)
            cmds.setAttr(self.node + '.' + name, value, type="string")
        elif type == "float":
            if not self.nodeHasAttribute(name):
                cmds.addAttr(ln=name, at=type)
            cmds.setAttr(self.node + '.' + enum.name, value)

#___________________________________________________________________________________________________ getProperties
    def getProperties(self):
        properties = Reflection.getReflectionList(TrackPropEnum)
        dictionary = dict()
        for p in properties:
            name = p.name
            value = self.getProperty(p.name)
            if value is not None:
                dictionary[name] = value
            print "in getProperties, name = %s, value = %s" % (name, value)
        return dictionary
#___________________________________________________________________________________________________ setProperties
    def setProperties(self, dictionary):
        for prop,value in dictionary.iteritems():
            self.setProperty(prop, value)

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

#___________________________________________________________________________________________________ getPrev
    def getPrev(self):
        connections = cmds.listConnections(self.node + '.prevTrack', s=True, p=True)
        if connections:
            for c in connections:
                if c.endswith('.message'):
                    node = c.split('.')[0]
                    return Track(node)
        return None

#___________________________________________________________________________________________________ getNext
    def getNext(self):
        connections = cmds.listConnections(self.node + '.message', d=True, p=True)
        if connections:
            for c in connections:
                if c.endswith('.prevTrack'):
                    node = c.split('.')[0]
                    return Track(node)
        return None

#___________________________________________________________________________________________________ link
    def link(self, prev):
        self.unlink()
        self.setProperty(TrackPropEnum.PREV.name, prev.getName())
        prev.setProperty(TrackPropEnum.NEXT.name, self.getName())
        cmds.connectAttr(prev.node + '.message', self.node + '.prev', f=True)

#___________________________________________________________________________________________________ unlink
    def unlink(self):
        prev = self.getPrev()
        if not prev:
            return
        cmds.disconnectAttr(prev.node + '.message', self.node + '.prevTrack')
        self.setProperty(TrackPropEnum.PREV.name, '')
        prev.setProperty(TrackPropEnum.NEXT.name, '')

#___________________________________________________________________________________________________ createNode
    @classmethod
    def createNode(cls):
        """Create an elliptical cylinder (disk) plus a superimposed triangular pointer to signify
        the position, dimensions, and rotation of a manus or pes print.  The cylinder has a
        diameter of one meter so that the scale in x and z equates to the width and length of the
        manus or pes in fractional meters (e.g., 0.5 = 50 cm).  The pointer is locked to not be
        non-selectable (reference) and the marker is prohibited from changing y (elevation) or
        rotation about either x or z.  The color of the cylinder indicates manus versus pes, and
        the color of the pointer on top of the cylinder indicates left versus right."""
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

#___________________________________________________________________________________________________ setCadenceCamFocus
    def setCadenceCamFocus(self):
        if not cmds.objExists('CadenceCam'):
            self.initializeCadenceCam()
        height = cmds.xform('CadenceCam', query=True, translation=True)[1]
        cmds.move(self.getX(), height, self.getZ(), 'CadenceCam', absolute=True)

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
        return '%s' % self.getName()

