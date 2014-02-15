# Track.py
# (C)2013-2014
# Kent A. Stevens and Scott Ernst

from pyaid.reflection.Reflection import Reflection

import nimble
from nimble import cmds

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.enum.TrackPropEnum import TrackPropEnumOps
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
    def __init__(self, node =None, uid = None, trackData =None):
        """ Creates a new instance of a Track.
            * node => String name of an existing Maya transform node representing the track
            * uid => Universal unique identifier string for the track within the database
                    and within Maya
            * trackData => A dictionary representation of the current track data either loaded
                    from disk or from the Track_Track model toDict() method """
        self.node       = node
        self._trackData = trackData
        self._uid       = trackData.get(
            'uid', uid if uid else CadenceEnvironment.createUniqueId(u'track'))

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: databaseId
    @property
    def databaseId(self):
        return self._trackData.get('id', None) if self._trackData else None

#___________________________________________________________________________________________________ GS: uid
    @property
    def uid(self):
        """ The universal unique identifier for this track within Maya, the database, and during
            computation. """
        uid = self._getTrackProp(TrackPropEnum.UID)
        return uid if uid else self._uid

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        """ Human-readable display name for the track based of its properties """
        number = unicode(int(self.number)) if self.number else u'-'
        return (u'L' if self.left else u'R') + (u'P' if self.pes else u'M') + number
    @name.setter
    def name(self, value):
        self.pes    = True if value[0] == u'P' else False
        self.left   = True if value[1] == u'L' else False
        self.number = value[2:]

#___________________________________________________________________________________________________ GS: trackData
    @property
    def trackData(self):
        """ Dictionary representation of the track as stored by the database and on disk if such
            an entry exists or None otherwise. """
        return self._trackData

#___________________________________________________________________________________________________ GS: propertyName
    @property
    def index(self):
        return self._getTrackProp(TrackPropEnum.INDEX, 0)
    @index.setter
    def index(self, value):
        self._setTrackProp(TrackPropEnum.INDEX, value)

#___________________________________________________________________________________________________ GS: comm
    @property
    def comm(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.COMM)
    @comm.setter
    def comm(self, value):
        self._setTrackProp(TrackPropEnum.COMM, value)

#___________________________________________________________________________________________________ GS: site
    @property
    def site(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.SITE)
    @site.setter
    def site(self, value):
        self._setTrackProp(TrackPropEnum.SITE, value)

#___________________________________________________________________________________________________ GS: year
    @property
    def year(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.YEAR)
    @year.setter
    def year(self, value):
        self._setTrackProp(TrackPropEnum.YEAR, value)

#___________________________________________________________________________________________________ GS: level
    @property
    def level(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.LEVEL)
    @level.setter
    def level(self, value):
        self._setTrackProp(TrackPropEnum.LEVEL, value)

#___________________________________________________________________________________________________ GS: sector
    @property
    def sector(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.SECTOR)
    @sector.setter
    def sector(self, value):
        self._setTrackProp(TrackPropEnum.SECTOR, value)

#___________________________________________________________________________________________________ GS: trackwayType
    @property
    def trackwayType(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.TRACKWAY_TYPE)
    @trackwayType.setter
    def trackwayType(self, value):
        self._setTrackProp(TrackPropEnum.TRACKWAY_TYPE, value)

#___________________________________________________________________________________________________ GS: trackwayNumber
    @property
    def trackwayNumber(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.TRACKWAY_NUMBER)
    @trackwayNumber.setter
    def trackwayNumber(self, value):
        self._setTrackProp(TrackPropEnum.TRACKWAY_NUMBER, value)

#___________________________________________________________________________________________________ GS: isLeft
    @property
    def left(self):
        """ True if the track was made by the left side of the track maker. """
        return self._getTrackProp(TrackPropEnum.LEFT)
    @left.setter
    def left(self, value):
        self._setTrackProp(TrackPropEnum.LEFT, value)
        if self.node is not None and value:
            self.colorTrack()

#___________________________________________________________________________________________________ GS: pes
    @property
    def pes(self):
        """ True if the track was made by the hindquarters of the track maker. """
        return self._getTrackProp(TrackPropEnum.PES)
    @pes.setter
    def pes(self, value):
        self._setTrackProp(TrackPropEnum.PES, value)
        if self.node is not None and value:
            self.colorTrack()

#___________________________________________________________________________________________________ GS: number
    @property
    def number(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.NUMBER)
    @number.setter
    def number(self, value):
        self._setTrackProp(TrackPropEnum.NUMBER, value)

#___________________________________________________________________________________________________ GS: note
    @property
    def note(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.NOTE)
    @note.setter
    def note(self, value):
        self._setTrackProp(TrackPropEnum.NOTE, value)

#___________________________________________________________________________________________________ GS: prev
    @property
    def prev(self):
        """ The universally unique identifier for the previous track within thr track series, or an
            empty value if no previous track exists. """
        return self._getTrackProp(TrackPropEnum.PREV)
    @prev.setter
    def prev(self, value):
        self._setTrackProp(TrackPropEnum.PREV, value)

#___________________________________________________________________________________________________ GS: next
    @property
    def next(self):
        """ The universally unique identifier for the next track within thr track series, or an
            empty value if no next track exists. """
        return self._getTrackProp(TrackPropEnum.NEXT)
    @next.setter
    def next(self, value):
        self._setTrackProp(TrackPropEnum.PREV, value)

#___________________________________________________________________________________________________ GS: snapshot
    @property
    def snapshot(self):
        """ A serialized JSON string containing track data from the spreadsheet source. """
        return self._getTrackProp(TrackPropEnum.SNAPSHOT)
    @snapshot.setter
    def snapshot(self, value):
        self._setTrackProp(TrackPropEnum.SNAPSHOT, value)

#___________________________________________________________________________________________________ GS: width
    @property
    def width(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.WIDTH, 'scaleX')
    @width.setter
    def width(self, value):
        self._setTrackProp(TrackPropEnum.WIDTH, value, 'scaleX')

#___________________________________________________________________________________________________ GS: length
    @property
    def length(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.LENGTH, 'scaleZ')
    @length.setter
    def length(self, value):
        self._setTrackProp(TrackPropEnum.LENGTH, value, 'scaleZ')

#___________________________________________________________________________________________________ GS: rotation
    @property
    def rotation(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.ROTATION, 'ry')
    @rotation.setter
    def rotation(self, value):
        self._setTrackProp(TrackPropEnum.ROTATION, value, 'ry')

#___________________________________________________________________________________________________ GS: x
    @property
    def x(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.X, 'translateX')
    @x.setter
    def x(self, value):
        self._setTrackProp(TrackPropEnum.X, value, 'translateX')

#___________________________________________________________________________________________________ GS: z
    @property
    def z(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.Z, 'translateZ')
    @z.setter
    def z(self, value):
        self._setTrackProp(TrackPropEnum.Z, value, 'translateZ')

#___________________________________________________________________________________________________ GS: widthUncertainty
    @property
    def widthUncertainty(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.WIDTH_UNCERTAINTY)
    @widthUncertainty.setter
    def widthUncertainty(self, value):
        self._setTrackProp(TrackPropEnum.WIDTH_UNCERTAINTY, value)

#___________________________________________________________________________________________________ GS: lengthUncertainty
    @property
    def lengthUncertainty(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.LENGTH_UNCERTAINTY)
    @lengthUncertainty.setter
    def lengthUncertainty(self, value):
        self._setTrackProp(TrackPropEnum.LENGTH_UNCERTAINTY, value)

#___________________________________________________________________________________________________ GS: depthUncertainty
    @property
    def depthUncertainty(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.DEPTH_UNCERTAINTY)
    @depthUncertainty.setter
    def depthUncertainty(self, value):
        self._setTrackProp(TrackPropEnum.DEPTH_UNCERTAINTY, value)

#___________________________________________________________________________________________________ GS: rotationUncertainty
    @property
    def rotationUncertainty(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.ROTATION_UNCERTAINTY)
    @rotationUncertainty.setter
    def rotationUncertainty(self, value):
        self._setTrackProp(TrackPropEnum.ROTATION_UNCERTAINTY, value)

#___________________________________________________________________________________________________ GS: widthMeasured
    @property
    def widthMeasured(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.WIDTH_MEASURED)
    @widthMeasured.setter
    def widthMeasured(self, value):
        self._setTrackProp(TrackPropEnum.WIDTH_MEASURED, value)

#___________________________________________________________________________________________________ GS: lengthMeasured
    @property
    def lengthMeasured(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.LENGTH_MEASURED)
    @lengthMeasured.setter
    def lengthMeasured(self, value):
        self._setTrackProp(TrackPropEnum.LENGTH_MEASURED, value)

#___________________________________________________________________________________________________ GS: length
    @property
    def depthMeasured(self):
        """ TODO: Kent... """
        return self._getTrackProp(TrackPropEnum.DEPTH_MEASURED)
    @depthMeasured.setter
    def depthMeasured(self, value):
        self._setTrackProp(TrackPropEnum.DEPTH_MEASURED, value)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ GS: createPreviousTrack
    def createPreviousTrack(self):
        """ Creates and returns a Track instance for the previous track entry if one exists or
            None if this is the first track in the series. """
        p = self.prev
        return Track(uid=p) if p else None

#___________________________________________________________________________________________________ GS: createNextTrack
    def createNextTrack(self):
        """ Creates and returns a Track instance for the next track entry if one exists or
            None if this is the last track in the series. """
        n = self.next
        return Track(uid=n) if n else None

#___________________________________________________________________________________________________ generateNode
    def generateNode(self):
        """ Creates a node for this track instance based on the existing track data """
        if self.node is not None:
            return
        self.node = self.createNode()
        self.setProperties(self._trackData)

#___________________________________________________________________________________________________ nodeHasAttribute
    def nodeHasAttribute(self, attribute):
        """ Checks the Maya node associated with this track for the specified attribute and returns
            True if found or False if not or no node exists. """
        if self.node is None:
            return False
        return cmds.hasAttr(self.node + '.' + attribute)

#___________________________________________________________________________________________________ getProperty
    def getProperty(self, p):
        """ Returns the value of a track property based on its name or enumeration. The p argument
            can be either a TrackPropEnum enumerated value or the name of a TrackPropEnum value. """

        enum = TrackPropEnumOps.getTrackPropEnumByName(p) if isinstance(p, basestring) else p

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
        return self._getTrackProp(enum)

#___________________________________________________________________________________________________ setProperty
    def setProperty(self, p, value):
        """ Sets the value of a track property based on its name or enumeration and value. The
            p argument can be either a TrackPropEnum enumerated value or the name of a
            TrackPropEnum value. """

        enum = TrackPropEnumOps.getTrackPropEnumByName(p) if isinstance(p, basestring) else p

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
            self._setTrackProp(enum, value)

#___________________________________________________________________________________________________ getProperties
    def getProperties(self):
        """ Returns a dictionary containing the various properties of the track data. """

        # Outside of Maya return track data directly
        if self.node is None:
            return self._trackData

        propEnums = Reflection.getReflectionList(TrackPropEnum)
        props     = dict()
        for enum in propEnums:
            name  = enum.name
            value = self.getProperty(name)
            if value is not None:
                props[name] = value

        return props

#___________________________________________________________________________________________________ setProperties
    def setProperties(self, properties):
        """ Sets the value of each track property in the properties dictionary. """
        for prop,value in properties.iteritems():
            self.setProperty(prop, value)

#___________________________________________________________________________________________________ colorTrack
    def colorTrack(self):
        """ TODO: Kent... """

        if self.pes:
            ShadingUtils.applyShader(TrackwayShaderConfig.DARK_GRAY_COLOR, self.node)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.LIGHT_GRAY_COLOR, self.node)

        if self.left:
            ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR, self.node + '|pointer')
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, self.node + '|pointer')

#___________________________________________________________________________________________________ setCadenceCamFocus
    def setCadenceCamFocus(self):
        """ TODO: Kent... """
        if self.node is None:
            return

        if not cmds.objExists('CadenceCam'):
            self.initializeCadenceCam()
        height = cmds.xform('CadenceCam', query=True, translation=True)[1]
        cmds.move(self.x, height, self.z, 'CadenceCam', absolute=True)

#___________________________________________________________________________________________________ refreshNodeLink
    def refreshNodeLink(self):
        """ Tries to find the Maya node with the given uid and assigns the result to the node
            property of the track. Can be used even if a node name already exists to heal after
            potential name changes. """

        try:
            conn   = nimble.getConnection()
            result = conn.runPythonScriptFile(
                CadenceEnvironment.getResourceScriptPath('findTrackNode.py'))

            self.node = result.payload.get('node')
        except Exception, err:
            self.node = None
        return self.node

#___________________________________________________________________________________________________ load
    def load(self):
        """ Loads the Track from the database or Maya depending on how the instance was
            constructed. """
        if self.uid is None:
            return False

        if CadenceEnvironment.NIMBLE_IS_ACTIVE:
            self.refreshNodeLink()
            if self.node:
                return True

        entry = Tracks_Track.getByUid(self._uid)
        if entry is None:
            return False

        self._trackData =  entry.toDict()
        entry.session.close()
        return True

#___________________________________________________________________________________________________ loadFromValues
    def loadFromValues(self):
        """ Loads based on the current values set for the track. This form of loading is useful
            when the uid is not available, e.g. when importing data from the spreadsheet. """
        if self.uid is not None and self.load():
            return True

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

#___________________________________________________________________________________________________ save
    def save(self, session =None):
        props = self.getProperties()
        model = Tracks_Track.MASTER
        entry = None

        # Update or create the database entry from the property data
        if self._uid is not None:
            entry = Tracks_Track.getByUid(self._uid, session=session)

        if entry is None:
            entry = Tracks_Track()
            entry.fromDict(props)
            entry.uid = self._uid

            s = model.createSession() if session is None else session
            s.add(entry)
            s.flush()
        else:
            s = entry.session
            entry.fromDict(props)

        s.commit()
        if session is None:
            s.close()

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

#___________________________________________________________________________________________________ _getTrackProp
    def _getTrackProp(self, enum, mayaAttrName =None, defaultValue =None):
        """ Retrieves the track property defined by the specified TrackPropEnum. """

        if self.node is None:
            return self._trackData.get(enum.name, defaultValue)

        if mayaAttrName is None:
            mayaAttrName = enum.name

        if not self.nodeHasAttribute(mayaAttrName):
            return None

        return cmds.getAttr(self.node + '.' + mayaAttrName)

#___________________________________________________________________________________________________ _setTrackProp
    def _setTrackProp(self, enum, value, mayaAttrName =None):
        """ Sets the track property defined by the specified TrackPropEnum and value. """

        if self.node is None:
            self._trackData[enum.name] = value
            return

        if mayaAttrName is None:
            mayaAttrName = enum.name
        if not self.nodeHasAttribute(mayaAttrName):
            if enum.type == 'string':
                cmds.addAttr(self.node, ln=mayaAttrName, dt=enum.type)
            else:
                cmds.addAttr(self.node, ln=mayaAttrName, at=enum.type)
        propType = enum.type
        if propType in ['float', 'bool', 'long']:
            propType = None
        try:
            if propType is None:
                cmds.setAttr(self.node + '.' + mayaAttrName, value)
            else:
                cmds.setAttr(self.node + '.' + mayaAttrName, value, type=propType)
        except Exception, err:
            print 'ERROR: Track._setTrackProp'
            print '  NODE: ' + str(self.node)
            print '  ATTR: ' + str(mayaAttrName)
            print '  TYPE: ' + str(propType)
            print '  VALUE: ' + str(value) + ' | ' + str(type(value))
            print '  ERROR: ', err
            raise

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
        print self.name
        return '[%s(%s) "%s"]' % (self.__class__.__name__, self.name, self.uid)

