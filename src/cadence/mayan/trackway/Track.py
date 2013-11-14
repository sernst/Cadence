# Track.py
# (C)2013
# Kent A. Stevens and Scott Ernst

import re

from pyaid.radix.Base64 import Base64
from pyaid.reflection.Reflection import Reflection
from pyaid.string.StringUtils import StringUtils

import nimble
from nimble import cmds

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enum.TrackCsvColumnEnum import TrackCsvColumnEnum
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

    _TRACKWAY_PATTERN = re.compile('(?P<type>[A-Za-z]+)[\s\t]*(?P<number>[0-9]+)')

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

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        number = self.number
        if not number:
            number = 0
        return (u'L' if self.left else u'R') + (u'P' if self.pes else u'M') + unicode(int(number))

#___________________________________________________________________________________________________ GS: trackData
    @property
    def trackData(self):
        return self._trackData

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

#___________________________________________________________________________________________________ GS: trackwayType
    @property
    def trackwayType(self):
        return self._getTrackAttr(TrackPropEnum.TRACKWAY_TYPE)
    @trackwayType.setter
    def trackwayType(self, value):
        self._setTrackAttr(TrackPropEnum.TRACKWAY_TYPE, value)

#___________________________________________________________________________________________________ GS: trackwayNumber
    @property
    def trackwayNumber(self):
        return self._getTrackAttr(TrackPropEnum.TRACKWAY_NUMBER)
    @trackwayNumber.setter
    def trackwayNumber(self, value):
        self._setTrackAttr(TrackPropEnum.TRACKWAY_NUMBER, value)

#___________________________________________________________________________________________________ GS: left
    @property
    def left(self):
        return self._getTrackAttr(TrackPropEnum.LEFT)
    @left.setter
    def left(self, value):
        self._setTrackAttr(TrackPropEnum.LEFT, value)
        if self.node is not None and value:
            self.colorTrack()

#___________________________________________________________________________________________________ GS: pes
    @property
    def pes(self):
        return self._getTrackAttr(TrackPropEnum.PES)
    @pes.setter
    def pes(self, value):
        self._setTrackAttr(TrackPropEnum.PES, value)
        if self.node is not None and value:
            self.colorTrack()

#___________________________________________________________________________________________________ GS: number
    @property
    def number(self):
        return self._getTrackAttr(TrackPropEnum.NUMBER)
    @number.setter
    def number(self, value):
        self._setTrackAttr(TrackPropEnum.NUMBER, value)

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
        """ The Unique Track ID (as created by the database) for the previous track within the
            track series in which this track resides."""

        if not self.node:
            return self._trackData.get(TrackPropEnum.PREV.name)

        node = self.previousTrackNode
        if node:
            return cmds.getAttr(node + '.' + TrackPropEnum.ID.name)
        return None
    @prev.setter
    def prev(self, value):
        self._setTrackAttr(TrackPropEnum.PREV, value)

#___________________________________________________________________________________________________ GS: previousTrackNode
    @property
    def previousTrackNode(self):
        if not self.node:
            return None

        connections = cmds.listConnections(self.node + '.prevTrack', s=True, p=True)
        if not connections:
            return None

        for c in connections:
            if c.endswith('.message'):
                node = c.split('.')[0]
                return node
        return None

#___________________________________________________________________________________________________ GS: previousTrack
    @property
    def previousTrack(self):
        if not self.node:
            prev = self.prev
            if prev:
                return Track(trackId=prev)
            return None

        node = self.previousTrackNode if self.node else None
        return Track(node=node)

#___________________________________________________________________________________________________ GS: nextTrackNode
    @property
    def nextTrackNode(self):
        if not self.node:
            return None

        connections = cmds.listConnections(self.node + '.message', d=True, p=True)
        if not connections:
            return None

        for c in connections:
            if c.endswith('.prevTrack'):
                node = c.split('.')[0]
                return node
        return None

#___________________________________________________________________________________________________ GS: next
    @property
    def next(self):
        if not self.node:
            if not self._trackId:
                return None

            model   = Tracks_Track.MASTER
            session = model.createSession()
            result  = session.query(model).filter(model.prev == self._trackId).first()
            return result.id if result else None

        node = self.nextTrackNode
        if node:
            return cmds.getAttr(node + '.' + TrackPropEnum.ID.name)
        return None

#___________________________________________________________________________________________________ GS: nextTrack
    @property
    def nextTrack(self):
        if not self.node:
            n = self.next
            if n:
                return Track(trackId=n)
            return None

        node = self.nextTrackNode if self.node else None
        return Track(node=node)

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
        """ The Base-64 unique identifier of the track within the database if a database record
            exists, otherwise an empty string."""

        out = self._getTrackAttr(TrackPropEnum.ID)
        if out is None:
            return u''
        return None

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
        self._setTrackAttr(TrackPropEnum.LENGTH_UNCERTAINTY, value)

#___________________________________________________________________________________________________ GS: depthUncertainty
    @property
    def depthUncertainty(self):
        return self._getTrackAttr(TrackPropEnum.DEPTH_UNCERTAINTY)
    @depthUncertainty.setter
    def depthUncertainty(self, value):
        self._setTrackAttr(TrackPropEnum.DEPTH_UNCERTAINTY, value)

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

#___________________________________________________________________________________________________ GS: length
    @property
    def depthMeasured(self):
        return self._getTrackAttr(TrackPropEnum.DEPTH_MEASURED)
    @depthMeasured.setter
    def depthMeasured(self, value):
        self._setTrackAttr(TrackPropEnum.DEPTH_MEASURED, value)


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
        """ Create an elliptical cylinder (disk) plus a superimposed triangular pointer to signify
            the position, dimensions, and rotation of a manus or pes print.  The cylinder has a
            diameter of one meter so that the scale in x and z equates to the width and length of
            the manus or pes in fractional meters (e.g., 0.5 = 50 cm).  The pointer is locked to
            not be non-selectable (reference) and the marker is prohibited from changing y
            (elevation) or rotation about either x or z.  The color of the cylinder indicates manus
            versus pes, and the color of the pointer on top of the cylinder indicates left versus
            right."""

        trackProps = []
        for enum in Reflection.getReflectionList(TrackPropEnum):
            trackProps.append({'name':enum.name, 'type':enum.type, 'intrinsic':enum.intrinsic})

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

        if enum.name == TrackPropEnum.WIDTH.name:
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
        # Outside of Maya return track data directly
        if self.node is None:
            return self._trackData

        propEnums = Reflection.getReflectionList(TrackPropEnum)
        props     = dict()
        for enum in propEnums:
            name = enum.name

            # Handle the track ID as a special case so that it is current when the database entry
            # is created
            if name == TrackPropEnum.ID.name:
                props[name] = self._trackId
                continue

            value = self.getProperty(name)
            if value is not None:
                props[name] = value

        return props

#___________________________________________________________________________________________________ setProperties
    def setProperties(self, properties):
        for prop,value in properties.iteritems():
            self.setProperty(prop, value)

#___________________________________________________________________________________________________ colorTrack
    def colorTrack(self):
        if self.pes:
            ShadingUtils.applyShader(TrackwayShaderConfig.DARK_GRAY_COLOR, self.node)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.LIGHT_GRAY_COLOR, self.node)

        if self.left:
            ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR, self.node + '|pointer')
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, self.node + '|pointer')

#___________________________________________________________________________________________________ isPes
    def isPes(self):
        return self.pes

#___________________________________________________________________________________________________ isManus
    def isManus(self):
        return not self.pes

#___________________________________________________________________________________________________ isRight
    def isRight(self):
        return not self.left

#___________________________________________________________________________________________________ isLeft
    def isLeft(self):
        return self.left

#___________________________________________________________________________________________________ link
    def link(self, prevTrack):
        """ sets the (string-type) prev and next attributes to reference the name of self and
            the name of some previousTrack, and also connects the current node's (message-type)
            prev attribute to previousTrack's node."""

        # Break existing next/prev link if present
        self.unlink()
        self.prev = prevTrack.id
        cmds.connectAttr(prevTrack.node + '.message', self.node + '.prevTrack', f=True)

#___________________________________________________________________________________________________ unlink
    def unlink(self):
        p = self.previousTrack
        if p is None:
            return
        cmds.disconnectAttr(p.node + '.message', self.node + '.prevTrack')
        self.prev = u''

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
            return False

        entry = self._getTrackEntry(self._trackId)
        if entry is None:
            return False

        if self._trackData:
            self._trackData = dict(entry.toDict().items() + self._trackData.items())
        else:
            self._trackData =  entry.toDict()
        entry.session.close()
        return True

#___________________________________________________________________________________________________ findAndLoadData
    def findAndLoadData(self):
        if self._trackId is not None:
            return self.loadData()

        model   = Tracks_Track.MASTER
        session = model.createSession()
        query   = session.query(model)

        if self.pes is not None:
            query = query.filter(model.pes == self.pes)
        if self.left is not None:
            query = query.filter(model.left == self.left)
        if self.number is not None:
            query = query.filter(model.number == self.number)
        if self.trackwayNumber is not None:
            query = query.filter(model.trackwayNumber == self.trackwayNumber)
        if self.trackwayType:
            query = query.filter(model.trackwayType == self.trackwayType)
        if self.level is not None:
            query = query.filter(model.level == self.level)
        if self.year is not None:
            query = query.filter(model.year == self.year)
        if self.site is not None:
            query = query.filter(model.site == self.site)
        if self.sector is not None:
            query = query.filter(model.sector == self.sector)

        result = query.all()
        if not result:
            session.close()
            return False

        if len(result) > 1:
            print 'ERROR: Ambiguous track definition. Unable to load'
            session.close()
            return False

        entry = result[0]
        if self._trackData:
            self._trackData = dict(entry.toDict().items() + self._trackData.items())
        else:
            self._trackData =  entry.toDict()
        session.close()
        return True

#___________________________________________________________________________________________________ saveData
    def saveData(self, session =None):
        props = self.getProperties()
        model = Tracks_Track.MASTER

        # Update or create the database entry from the property data
        if self._trackId is not None:
            entry = self._getTrackEntry(self._trackId, session=session)
            s     = entry.session
            entry.fromDict(props)
        else:
            entry = Tracks_Track()
            entry.fromDict(props)

            s = model.createSession() if session is None else session
            s.add(entry)
            s.flush()

            self._trackId = Base64.to64(entry.i)
            entry.id = self._trackId

        # If the previous track has not been saved to the database, save it as well to populate
        # the prev id value
        if not entry.prev:
            track = self.previousTrack
            if track:
                if not track.id:
                    track.saveData(session=s)
                    entry.prev = track.id

        s.commit()
        if session is None:
            s.close()

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

#___________________________________________________________________________________________________ fromSpreadsheetEntry
    @classmethod
    def fromSpreadsheetEntry(cls, csvRow, force =True):
        csvIndex    = csvRow[TrackCsvColumnEnum.INDEX]
        t           = Track(trackData=dict())
        t.site      = csvRow[TrackCsvColumnEnum.TRACKSITE]
        t.year      = csvRow[TrackCsvColumnEnum.CAST_DATE].split('_')[-1]
        t.sector    = csvRow[TrackCsvColumnEnum.SECTOR]
        t.level     = csvRow[TrackCsvColumnEnum.LEVEL]

        #-------------------------------------------------------------------------------------------
        # TRACKWAY
        #       Parse the trackway entry into type and number values
        test   = csvRow[TrackCsvColumnEnum.TRACKWAY].strip()
        result = cls._TRACKWAY_PATTERN.search(test)
        try:
            t.trackwayType   = result.groupdict()['type']
            t.trackwayNumber = float(result.groupdict()['number'])
        except Exception, err:
            print 'ERROR: Invalid trackway value "%s" at index: %s' % (test, csvIndex)
            print '    RESULT:', result, '->', result.groupdict() if result else 'N/A'
            raise

        #-------------------------------------------------------------------------------------------
        # NAME
        #       Parse the name value into left, pes, and number attributes
        name = csvRow[TrackCsvColumnEnum.TRACK_NAME].strip()
        if StringUtils.begins(name.upper(), [u'M', u'P']):
            t.left = name[1].upper() == u'L'
            t.pes  = name[0].upper() == u'P'
        else:
            t.left = name[0].upper() == u'L'
            t.pes  = name[1].upper() == u'P'
        t.number = float(re.compile('[^0-9]+').sub(u'', name[2:]))

        #-------------------------------------------------------------------------------------------
        # FIND EXISTING
        #       Use data set above to attempt to load the track database entry
        if t.findAndLoadData() and not force:
            if csvIndex != t.index:
                print 'Ambiguous Track Entry [%s != %s]' % (csvIndex, t.index)
            return t

        t.index = csvIndex

        if t.isManus():
            wide      = csvRow[TrackCsvColumnEnum.MANUS_WIDTH]
            wideGuess = csvRow[TrackCsvColumnEnum.MANUS_WIDTH_GUESS]
            longVal   = csvRow[TrackCsvColumnEnum.MANUS_LENGTH]
            longGuess = csvRow[TrackCsvColumnEnum.MANUS_LENGTH_GUESS]
            deep      = csvRow[TrackCsvColumnEnum.MANUS_DEPTH]
            deepGuess = csvRow[TrackCsvColumnEnum.MANUS_DEPTH_GUESS]
        else:
            wide      = csvRow[TrackCsvColumnEnum.PES_WIDTH]
            wideGuess = csvRow[TrackCsvColumnEnum.PES_WIDTH_GUESS]
            longVal   = csvRow[TrackCsvColumnEnum.PES_LENGTH]
            longGuess = csvRow[TrackCsvColumnEnum.PES_LENGTH_GUESS]
            deep      = csvRow[TrackCsvColumnEnum.PES_DEPTH]
            deepGuess = csvRow[TrackCsvColumnEnum.PES_DEPTH_GUESS]

        try:
            t.widthMeasured     = float(wide if wide else wideGuess)
            t.widthUncertainty  = 5.0 if wideGuess else 4.0
        except Exception, err:
            t.widthMeasured    = 0.0
            t.widthUncertainty = 5.0

        try:
            t.lengthMeasured    = float(long if longVal else longGuess)
            t.lengthUncertainty = 5.0 if longGuess else 4.0
        except Exception, err:
            t.lengthMeasured    = 0.0
            t.lengthUncertainty = 5.0

        try:
            t.depthMeasured     = float(deep if deep else deepGuess)
            t.depthUncertainty  = 5.0 if deepGuess else 4.0
        except Exception, err:
            t.depthMeasured    = 0.0
            t.depthUncertainty = 5.0

        # Save csv value changes to the database
        t.saveData()

        return t

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
            if enum.type == 'string':
                cmds.addAttr(self.node, ln=mayaAttrName, dt=enum.type)
            elif enum.type == 'float':
                cmds.addAttr(self.node, ln=mayaAttrName, at=enum.type)
            elif enum.type == 'bool':
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
            print '  NODE: ' + str(self.node)
            print '  ATTR: ' + str(mayaAttrName)
            print '  TYPE: ' + str(propType)
            print '  VALUE: ' + str(value) + ' | ' + str(type(value))
            print '  ERROR: ', err
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
    def _getTrackEntry(cls, trackId, session =None):
        model  = Tracks_Track.MASTER
        s      = model.createSession() if session is None else session
        result = s.query(model).filter(model.id == trackId).first()
        if result is None:
            if session is None:
                s.close()
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
        return '[%s(%s) "%s"]' % (self.__class__.__name__, self.name, self._trackId)

