# Track.py
# (C)2013
# Kent A. Stevens and Scott Ernst

from pyaid.radix.Base64 import Base64
from pyaid.reflection.Reflection import Reflection

import nimble
from nimble import cmds

from cadence.CadenceEnvironment import CadenceEnvironment
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
    def __init__(self, node =None, trackId =None, trackData =None):
        """ Creates a new instance of a Track.  Argument is the string name of the Maya node. """
        self.node       = node
        self._trackId   = trackId
        self._trackData = trackData

        if self._trackData is not None:
            self._trackId = self._trackData.get('id', trackId)
        elif trackId is not None:
            self.loadData()

#===================================================================================================
#                                                                                   G E T / S E T
#___________________________________________________________________________________________________ GS: comm
    @property
    def comm(self):
        return self._getTrackAttr(TrackPropEnum.COMM)
    @comm.setter
    def comm(self, value):
        self._setTrackAttr(TrackPropEnum.COMM, value)

#___________________________________________________________________________________________________ GS: site
    @property
    def site(self):
        return self._getTrackAttr(TrackPropEnum.SITE)
    @site.setter
    def site(self, value):
        self._setTrackAttr(TrackPropEnum.SITE, value)

#___________________________________________________________________________________________________ GS: year
    @property
    def year(self):
        return self._getTrackAttr(TrackPropEnum.YEAR)
    @year.setter
    def year(self, value):
        self._setTrackAttr(TrackPropEnum.YEAR, value)

#___________________________________________________________________________________________________ GS: level
    @property
    def level(self):
        return self._getTrackAttr(TrackPropEnum.LEVEL)
    @level.setter
    def level(self, value):
        self._setTrackAttr(TrackPropEnum.LEVEL, value)

#___________________________________________________________________________________________________ GS: sector
    @property
    def sector(self):
        return self._getTrackAttr(TrackPropEnum.SECTOR)
    @sector.setter
    def sector(self, value):
        self._setTrackAttr(TrackPropEnum.SECTOR, value)

#___________________________________________________________________________________________________ GS: trackway
    @property
    def trackway(self):
        return self._getTrackAttr(TrackPropEnum.TRACKWAY)
    @trackway.setter
    def trackway(self, value):
        self._setTrackAttr(TrackPropEnum.TRACKWAY, value)

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        return self._getTrackAttr(TrackPropEnum.NAME)
    @name.setter
    def name(self, value):
        self._setTrackAttr(TrackPropEnum.NAME, value)
        if self.node is not None and value:
            self.colorTrack()

#___________________________________________________________________________________________________ GS: note
    @property
    def note(self):
        return self._getTrackAttr(TrackPropEnum.NOTE)
    @note.setter
    def note(self, value):
        self._setTrackAttr(TrackPropEnum.NOTE, value)

#___________________________________________________________________________________________________ GS: prev
    @property
    def prev(self):
        connections = cmds.listConnections(self.node + '.prevTrack', s=True, p=True)
        if connections:
            for c in connections:
                if c.endswith('.message'):
                    node = c.split('.')[0]
                    return Track(node)
        return None
    @prev.setter
    def prev(self, value):
        self._setTrackAttr(TrackPropEnum.PREV, value)

#___________________________________________________________________________________________________ GS: next
    @property
    def next(self):
        connections = cmds.listConnections(self.node + '.message', d=True, p=True)
        if connections:
            for c in connections:
                if c.endswith('.prevTrack'):
                    node = c.split('.')[0]
                    return Track(node)
    @next.setter
    def next(self, value):
        self._setTrackAttr(TrackPropEnum.NEXT, value)

#___________________________________________________________________________________________________ GS: snapshot
    @property
    def snapshot(self):
        return self._getTrackAttr(TrackPropEnum.SNAPSHOT)
    @snapshot.setter
    def snapshot(self, value):
        self._setTrackAttr(TrackPropEnum.SNAPSHOT, value)

#___________________________________________________________________________________________________ GS: index
    @property
    def index(self):
        return self._getTrackAttr(TrackPropEnum.INDEX)
    @index.setter
    def index(self, value):
        self._setTrackAttr(TrackPropEnum.INDEX, value)

#___________________________________________________________________________________________________ GS: id
    @property
    def id(self):
        return self._getTrackAttr(TrackPropEnum.ID)

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
        return self._getTrackAttr(TrackPropEnum.ROTATION, 'ry')
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

#___________________________________________________________________________________________________ GS: widthUncertainty
    @property
    def widthUncertainty(self):
        return self._getTrackAttr(TrackPropEnum.WIDTH_UNCERTAINTY)
    @widthUncertainty.setter
    def widthUncertainty(self, value):
        self._setTrackAttr(TrackPropEnum.WIDTH_UNCERTAINTY, value)

#___________________________________________________________________________________________________ GS: lengthUncertainty
    @property
    def lengthUncertainty(self):
        return self._getTrackAttr(TrackPropEnum.LENGTH_UNCERTAINTY)
    @lengthUncertainty.setter
    def lengthUncertainty(self, value):
        self._setTrackAttr(TrackPropEnum.WIDTH_UNCERTAINTY, value)

#___________________________________________________________________________________________________ GS: widthMeasured
    @property
    def widthMeasured(self):
        return self._getTrackAttr(TrackPropEnum.WIDTH_MEASURED)
    @widthMeasured.setter
    def widthMeasured(self, value):
        self._setTrackAttr(TrackPropEnum.WIDTH_MEASURED, value)

#___________________________________________________________________________________________________ GS: lengthMeasured
    @property
    def lengthMeasured(self):
        return self._getTrackAttr(TrackPropEnum.LENGTH_MEASURED)
    @lengthMeasured.setter
    def lengthMeasured(self, value):
        self._setTrackAttr(TrackPropEnum.LENGTH_MEASURED, value)


#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ generateNode
    def generateNode(self):
        if self.node is not None:
            return
        self.node = self.createNode()
        self.setProperties(self._trackData)

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

        trackProps = []
        for enum in Reflection.getReflectionList(TrackPropEnum):
            trackProps.append({'name':enum.name, 'type':enum.type})

        path = CadenceEnvironment.getResourceScriptPath('createTrackNode.py', isFile=True)
        conn = nimble.getConnection()
        out  = conn.runPythonScriptFile(path, trackProps=trackProps)
        if not out.success:
            print 'CREATE NODE ERROR:', out.error

        return out.result['name']

#___________________________________________________________________________________________________ nodeHasAttribute
    def nodeHasAttribute(self, attribute):
        if self.node is None:
            return False
        return cmds.attributeQuery(attribute, node=self.node, exists=True)

#___________________________________________________________________________________________________ getProperty
    def getProperty(self, p):
        enum = self._getTrackPropEnum(p) if isinstance(p, basestring) else p

        if enum.name == TrackPropEnum.WIDTH.name:
            return self.width
        elif enum.name == TrackPropEnum.LENGTH.name:
            return self.length
        elif enum.name == TrackPropEnum.ROTATION.name:
            return self.rotation
        elif enum.name == TrackPropEnum.X.name:
            return self.x
        elif enum.name == TrackPropEnum.Z.name:
            return self.z
        return self._getTrackAttr(enum)

#___________________________________________________________________________________________________ setProperty
    def setProperty(self, p, value):
        if p == TrackPropEnum.ID.name:
            return

        enum = self._getTrackPropEnum(p) if isinstance(p, basestring) else p

        if enum.name == TrackPropEnum.NAME.name:
            self.name = value
        elif enum.name == TrackPropEnum.WIDTH.name:
            self.width = value
        elif enum.name == TrackPropEnum.LENGTH.name:
            self.length = value
        elif enum.name == TrackPropEnum.ROTATION.name:
            self.rotation = value
        elif enum.name == TrackPropEnum.X.name:
            self.x = value
        elif enum.name == TrackPropEnum.Z.name:
            self.z = value
        else:
            self._setTrackAttr(enum, value)

#___________________________________________________________________________________________________ getProperties
    def getProperties(self):
        if self.node is None:
            return self._trackData

        properties = Reflection.getReflectionList(TrackPropEnum)
        dictionary = dict()
        for p in properties:
            name = p.name
            if name == TrackPropEnum.ID.name:
                dictionary[p.name] = self._trackId
                continue

            value = self.getProperty(name)
            if value is not None:
                dictionary[name] = value

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

#___________________________________________________________________________________________________ link
    def link(self, prevTrack):
        """ sets the (string-type) prev and next attributes to reference the name of self and
        the name of some previousTrack, and also connects the current node's (message-type) prev
        attribute to previousTrack's node """
        self.unlink()  # break current next/prev link if present
        prevTrack.next = self.name
        self.prev = prevTrack.name
        cmds.connectAttr(prevTrack.node + '.message', self.node + '.prevTrack', f=True)

#___________________________________________________________________________________________________ unlink
    def unlink(self):
        p = self.prev
        if p is None:
            return
        cmds.disconnectAttr(p.node + '.message', self.node + '.prevTrack')
        if p.nodeHasAttribute(TrackPropEnum.NEXT.name):
            p.next = "" # uses empty string rather than None since this is a node attribute
        self.prev = ''

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
        if self._trackId is None:
            return

        entry = self._getTrackEntry(self._trackId)
        if entry is None:
            return

        self._trackData = entry.toDict()
        entry.session.close()

#___________________________________________________________________________________________________ saveData
    def saveData(self):
        props = self.getProperties()
        if self._trackId is not None:
            entry = self._getTrackEntry(self._trackId)
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

        self._trackId = Base64.to64(entry.i)
        entry.id = self._trackId
        session.commit()
        session.close()
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
            orthographicWidth=500)
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

        if mayaAttrName is None:
            mayaAttrName = enum.name

        if not self.nodeHasAttribute(mayaAttrName):
            if enum.type == "string":
                cmds.addAttr(self.node, ln=mayaAttrName, dt=enum.type)
            elif enum.type == "float":
                cmds.addAttr(self.node, ln=mayaAttrName, at=enum.type)
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
    def _getTrackEntry(cls, trackId):
        model   = Tracks_Track.MASTER
        session = model.createSession()
        result  = session.query(model).filter(model.id == trackId).first()
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
        return '%s' % self.name

