# Track.py
# (C)2013
# Kent A. Stevens and Scott Ernst

import math

from pyaid.radix.Base64 import Base64
from pyaid.reflection.Reflection import Reflection

import nimble
from nimble import cmds

from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.config.TrackwayShaderConfig import TrackwayShaderConfig
from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.util.shading.ShadingUtils import ShadingUtils

#___________________________________________________________________________________________________ Track
class Track(object):
    """ A track object wraps a reference to a Maya node (it's string name). A track has properties
        that are stored in the node, as string attributes, or floats, or directly by the values of
        the transforms."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, node =None, trackUid =None, trackData =None):
        """ Creates a new instance of a Track.  Argument is the string name of the Maya node. """
        self.node     = node
        self.trackUid = trackUid

        self._trackData = trackData
        if self._trackData is not None:
            self.trackUid = self._trackData.get('id', trackUid)
            return
        elif trackUid is not None:
            self.loadData()

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        return self._getTrackAttr(TrackPropEnum.NAME)
    @name.setter
    def name(self, value):
        self._setTrackAttr(TrackPropEnum.NAME, value)
        if self.node is not None and value:
            self.colorTrack()

#___________________________________________________________________________________________________ GS: width
    @property
    def width(self):
        return self._getTrackAttr(TrackPropEnum.WIDTH, 'scaleX')
    @width.setter
    def width(self, value):
        self._setTrackAttr(TrackPropEnum.WIDTH, value, 'scaleX')

#___________________________________________________________________________________________________ GS: length
    @property
    def length(self):
        return self._getTrackAttr(TrackPropEnum.LENGTH, 'scaleZ')
    @length.setter
    def length(self, value):
        self._setTrackAttr(TrackPropEnum.LENGTH, value, 'scaleZ')

#___________________________________________________________________________________________________ GS: rotation
    @property
    def rotation(self):
        return self._getTrackAttr(TrackPropEnum.ROTATION, 'rotateY')
    @rotation.setter
    def rotation(self, value):
        self._setTrackAttr(TrackPropEnum.ROTATION, value, 'ry')

#___________________________________________________________________________________________________ GS: x
    @property
    def x(self):
        return self._getTrackAttr(TrackPropEnum.X, 'translateX')
    @x.setter
    def x(self, value):
        self._setTrackAttr(TrackPropEnum.X, value, 'translateX')

#___________________________________________________________________________________________________ GS: z
    @property
    def z(self):
        return self._getTrackAttr(TrackPropEnum.Z, 'translateZ')
    @z.setter
    def z(self, value):
        self._setTrackAttr(TrackPropEnum.Z, value, 'translateZ')

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ generateNode
    def generateNode(self):
        if self.node is not None:
            return

        self.node = self.createNode()
        self.setProperties(self._trackData)

#___________________________________________________________________________________________________ nodeHasAttribute
    def nodeHasAttribute(self, attribute):
        if self.node is None:
            return False
        return cmds.attributeQuery(attribute, node=self.node, exists=True)

#___________________________________________________________________________________________________ getProperty
    def getProperty(self, p):
        enum = self._getTrackPropEnum(p) if isinstance(p, basestring) else p
        name = enum.name

        if name == TrackPropEnum.NAME.name:
            return self.name
        elif name == TrackPropEnum.WIDTH.name:
            return self.width
        elif name == TrackPropEnum.LENGTH.name:
            return self.length
        elif name == TrackPropEnum.ROTATION.name:
            return self.rotation
        elif name == TrackPropEnum.X.name:
            return self.x
        elif name == TrackPropEnum.Z.name:
            return self.z

        return self._getTrackAttr(enum)

#___________________________________________________________________________________________________ setProperty
    def setProperty(self, p, value):
        if p == 'id':
            self.trackUid = p
            return

        enum = self._getTrackPropEnum(p) if isinstance(p, basestring) else p
        name = enum.name

        if name == TrackPropEnum.NAME.name:
            self.name = value
        elif name == TrackPropEnum.WIDTH.name:
            self.width = value
        elif name == TrackPropEnum.LENGTH.name:
            self.length = value
        elif name == TrackPropEnum.ROTATION.name:
            self.rotation = value
        elif name == TrackPropEnum.X.name:
            self.x = value
        elif name == TrackPropEnum.Z.name:
            self.z = value
        else:
            self._setTrackAttr(enum, value)

#___________________________________________________________________________________________________ getProperties
    def getProperties(self):
        if self.node is None:
            return self._trackData

        properties = Reflection.getReflectionList(TrackPropEnum)
        dictionary = dict(id=self.trackUid)
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

#___________________________________________________________________________________________________ colorTrack
    def colorTrack(self):
        if self.name[1] == 'M':
            ShadingUtils.applyShader(TrackwayShaderConfig.LIGHT_GRAY_COLOR, self.node)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.DARK_GRAY_COLOR, self.node)
        if self.name[0] == 'R':
            ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, self.node +"|pointer")
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR, self.node +"|pointer")

#___________________________________________________________________________________________________ isPes
    def isPes(self):
        return self.name[1] == 'P'

#___________________________________________________________________________________________________ isManus
    def isManus(self):
        return self.name[0] == 'M'

#___________________________________________________________________________________________________ isRight
    def isRight(self):
        return self.name[0] == 'R'

#___________________________________________________________________________________________________ isLeft
    def isLeft(self):
        return self.name[1] == 'L'

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
        self.setProperty(TrackPropEnum.PREV.name, prev.name)
        prev.setProperty(TrackPropEnum.NEXT.name, self.name)
        cmds.connectAttr(prev.node + '.message', self.node + '.prev', f=True)

#___________________________________________________________________________________________________ unlink
    def unlink(self):
        prev = self.getPrev()
        if not prev:
            return
        cmds.disconnectAttr(prev.node + '.message', self.node + '.prevTrack')
        self.setProperty(TrackPropEnum.PREV.name, '')
        prev.setProperty(TrackPropEnum.NEXT.name, '')

#___________________________________________________________________________________________________ setCadenceCamFocus
    def setCadenceCamFocus(self):
        if self.node is None:
            return

        if not cmds.objExists('CadenceCam'):
            self.initializeCadenceCam()
        height = cmds.xform('CadenceCam', query=True, translation=True)[1]
        cmds.move(self.x, height, self.z, 'CadenceCam', absolute=True)

#___________________________________________________________________________________________________ importData
    def importData(self, trackData):
        self._trackData = trackData
        self.saveData()

#___________________________________________________________________________________________________ loadData
    def loadData(self):
        if self.trackUid is None:
            return

        entry = self._getTrackEntry(self.trackUid)
        if entry is None:
            return

        self._trackData = entry.toDict()
        entry.session.close()

#___________________________________________________________________________________________________ saveData
    def saveData(self):
        props = self.getProperties()
        if self.trackUid is not None:
            entry = self._getTrackEntry(self.trackUid)
            entry.fromDict(props)
            entry.session.commit()
            entry.session.close()
            return

        model = Tracks_Track.MASTER
        entry = Tracks_Track()
        entry.fromDict(props)

        session = model.createSession()
        session.add(entry)
        session.flush()

        self.trackUid = Base64.to64(entry.i)
        entry.id = self.trackUid
        session.commit()
        session.close()

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

        bcmds = nimble.createCommandsBatch()

        for item in Reflection.getReflectionList(TrackPropEnum):
            if item.type == 'string':
                bcmds.addAttr(ln=item.name, dt=item.type)
            else:
                bcmds.addAttr(ln=item.name, at=item.type)
        bcmds.sendCommandBatch()

        p = cmds.polyPrism(l=4, w=a, ns=3, sh=1, sc=0, ax=y, cuv=3, ch=1, n='pointer')[0]

        bcmds = nimble.createCommandsBatch()

        bcmds.rotate(0.0, -90.0, 0.0)
        bcmds.scale(1.0/math.sqrt(3.0), 1.0, 1.0)
        bcmds.move(0, 5, a/6.0)

        bcmds.setAttr(p + '.overrideEnabled', 1)
        bcmds.setAttr(p + '.overrideDisplayType', 2)

        bcmds.parent(p, c)
        bcmds.select(c)
        bcmds.setAttr(c + '.translateY', l=1)
        bcmds.setAttr(c + '.rotateX',    l=1)
        bcmds.setAttr(c + '.rotateZ',    l=1)
        bcmds.setAttr(c + '.scaleY',     l=1)

        bcmds.sendCommandBatch()

        return c

#___________________________________________________________________________________________________ incrementName
    @classmethod
    def incrementName(cls, name):
        prefix = name[:2]
        number = int(name[2:])
        return prefix + str(number + 1)

#___________________________________________________________________________________________________ initializeCadenceCam
    @classmethod
    def initializeCadenceCam(cls):
        c = cmds.camera(
            orthographic=True,
            nearClipPlane=1,
            farClipPlane=100000,
            orthographicWidth=300)
        cmds.rename(c[0], 'CadenceCam')
        cmds.rotate(-90, 180, 0)
        cmds.move(0, 100, 0, 'CadenceCam', absolute=True)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getTrackAttr
    def _getTrackAttr(self, enum, mayaAttrName =None):
        if self.node is None:
            return self._trackData[enum.name]

        if mayaAttrName is None:
            mayaAttrName = enum.name

        if not self.nodeHasAttribute(mayaAttrName):
            return None

        return cmds.getAttr(self.node + '.' + mayaAttrName)

#___________________________________________________________________________________________________ _setTrackAttr
    def _setTrackAttr(self, enum, value, mayaAttrName =None):
        if self.node is None:
            self._trackData[enum.name] = value
            return

        if not self.nodeHasAttribute(enum.name):
            if enum.type == "string":
                cmds.addAttr(ln=enum.name, dt=enum.type)
            elif enum.type == "float":
                cmds.addAttr(ln=enum.name, at=enum.type)

        if mayaAttrName is None:
            mayaAttrName = enum.name

        propType = enum.type
        if propType == 'float':
            propType = None

        try:
            if propType is None:
                cmds.setAttr(self.node + '.' + mayaAttrName, value)
            else:
                cmds.setAttr(self.node + '.' + mayaAttrName, value, type=propType)
        except Exception, err:
            print 'ERROR: Track._setTrackAttr'
            print '\tNODE: ' + str(self.node)
            print '\tATTR: ' + str(mayaAttrName)
            print '\tTYPE: ' + str(propType)
            print '\tVALUE: ' + str(value) + ' | ' + str(type(value))
            raise

#___________________________________________________________________________________________________ _getTrackPropEnum
    @classmethod
    def _getTrackPropEnum(cls, name):
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.name == name:
                return enum
        return None

#___________________________________________________________________________________________________ _getTrackEntry
    @classmethod
    def _getTrackEntry(cls, trackUid):
        model   = Tracks_Track.MASTER
        session = model.createSession()
        result  = session.query(model).filter(model.id == trackUid).first()
        if result is None:
            session.close()
            return None
        return result

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
        return '[Track %s]' % self.name

