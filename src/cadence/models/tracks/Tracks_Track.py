# Tracks_Track.py
# (C)2013-2014
# Scott Ernst

import re
from pyaid.string.StringUtils import StringUtils

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText

from pyaid.reflection.Reflection import Reflection

import nimble
from nimble import cmds

# AS NEEDED: from cadence.data.Track import Track
from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.config.TrackwayShaderConfig import TrackwayShaderConfig
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.mayan.trackway import GetTrackNodeData
from cadence.mayan.trackway import UpdateTrackNode
from cadence.mayan.trackway import CreateTrackNode
from cadence.models.tracks.TracksDefault import TracksDefault
from cadence.util.shading.ShadingUtils import ShadingUtils

#___________________________________________________________________________________________________ Tracks_Track
class Tracks_Track(TracksDefault):
    """ Database model representation of a track with all the attributes and information for a
        specific track as well as a connectivity information for the track within its series. """

#===================================================================================================
#                                                                                       C L A S S

    # Used to break trackway specifier into separate type and number entries
    _TRACKWAY_PATTERN = re.compile('(?P<type>[A-Za-z]+)[\s\t]*(?P<number>[0-9]+)')

    __tablename__  = u'tracks'

    _uid                 = Column(Unicode,      default=u'')
    _community           = Column(Unicode,      default=u'')
    _site                = Column(Unicode,      default=u'')
    _year                = Column(Unicode,      default=u'')
    _level               = Column(Unicode,      default=u'')
    _sector              = Column(Unicode,      default=u'')
    _trackwayType        = Column(Unicode,      default=u'')
    _trackwayNumber      = Column(Float,        default=0.0)
    _left                = Column(Boolean,      default=True)
    _pes                 = Column(Boolean,      default=True)
    _number              = Column(Unicode,      default=u'')
    _index               = Column(Integer,      default=0)
    _snapshot            = Column(Unicode,      default=u'')
    _note                = Column(UnicodeText,  default=u'')
    _next                = Column(Unicode,      default=u'')
    _width               = Column(Float,        default=1.0)
    _length              = Column(Float,        default=1.0)
    _rotation            = Column(Float,        default=0.0)
    _x                   = Column(Float,        default=0.0)
    _z                   = Column(Float,        default=0.0)
    _widthUncertainty    = Column(Float,        default=5.0)
    _lengthUncertainty   = Column(Float,        default=5.0)
    _depthUncertainty    = Column(Float,        default=5.0)
    _rotationUncertainty = Column(Float,        default=5.0)
    _widthMeasured       = Column(Float,        default=0.0)
    _lengthMeasured      = Column(Float,        default=0.0)
    _depthMeasured       = Column(Float,        default=0.0)

    _flags               = Column(Integer,      default=0)
    _sourceFlags         = Column(Integer,      default=0)
    _displayFlags        = Column(Integer,      default=0)

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        super(Tracks_Track, self).__init__(**kwargs)
        self.uid = CadenceEnvironment.createUniqueId(u'track')

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: nodeName
    @property
    def nodeName(self):
        """ A cached value for the name of the Maya node representing this track if one exists,
            which is updated each time a create/update operation on the node occurs. Can be
            incorrect if the node was renamed between such operations. """
        return self.fetchTransient('nodeName')
    @nodeName.setter
    def nodeName(self, value):
        self.putTransient('nodeName', value)

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        """ Human-readable display name for the track based of its properties """
        number = unicode(int(self.number)) if self.number else u'-'
        return (u'L' if self.left else u'R') + (u'P' if self.pes else u'M') + number
    @name.setter
    def name(self, value):
        value = value.strip()

        if StringUtils.begins(value.upper(), [u'M', u'P']):
            self.left = value[1].upper() == u'L'
            self.pes  = value[0].upper() == u'P'
        else:
            self.left = value[0].upper() == u'L'
            self.pes  = value[1].upper() == u'P'
        self.number = value[2:].upper()

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getPreviousTrack
    def getPreviousTrack(self, session):
        """ Returns the previous track in the series if such a track exists """
        model  = self.__class__
        try:
            return session.query(self.__class__).filter(model.next == self.uid).first()
        except Exception, err:
            return None

#___________________________________________________________________________________________________ getNextTrack
    def getNextTrack(self, session):
        """ Returns the next track in the series if such a track exists """
        if self.next is None:
            return None
        return self.getByUid(self.next, session=session)

#___________________________________________________________________________________________________ createNode
    def createNode(self):
        """ Create an elliptical cylinder (disk) plus a superimposed triangular pointer to signify
            the position, dimensions, and rotation of a manus or pes print.  The cylinder has a
            diameter of one meter so that the scale in x and z equates to the width and length of
            the manus or pes in fractional meters (e.g., 0.5 = 50 cm).  The pointer is locked to
            not be non-selectable (reference) and the marker is prohibited from changing y
            (elevation) or rotation about either x or z.  The color of the cylinder indicates manus
            versus pes, and the color of the pointer on top of the cylinder indicates left versus
            right."""

        conn = nimble.getConnection()
        out  = conn.runPythonModule(CreateTrackNode, uid=self.uid, props=self.toMayaNodeDict())
        if not out.success:
            print 'CREATE NODE ERROR:', out.error
            return None

        self.nodeName = out.payload['node']

        return self.nodeName

#___________________________________________________________________________________________________ updateNode
    def updateNode(self):
        """ Sends values to Maya node representation of the track to synchronize the values in the
            model and the node. """
        conn = nimble.getConnection()
        result = conn.runPythonModule(UpdateTrackNode, uid=self.uid, props=self.toMayaNodeDict())
        if not result.success:
            return False

        self.nodeName = result.payload.get('node')
        return True

#___________________________________________________________________________________________________ updateFromNode
    def updateFromNode(self):
        """ Retrieves Maya values from the node representation of the track and updates this
            model instance with those values. """

        conn = nimble.getConnection()
        result = conn.runPythonModule(GetTrackNodeData, uid=self.uid, node=self.nodeName)
        if result.payload.get('error'):
            print 'NODE ERROR:', result.payload.get('message')
            return False

        self.nodeName = result.payload.get('node')

        if self.nodeName:
            self.fromDict(result.payload.get('props'))
            return True

        return False

#___________________________________________________________________________________________________ fromDict
    def fromDict(self, data):
        """ Populates the track with the values specified by data dictionary argument. The keys of
            the data object should be valid names of the enumerated values in the TrackPropEnum
            class and the values valid entries for each key in the database class.

            This method can be used to load a track object from disk into a database model. """
        for key,value in data.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        """ Returns a dictionary containing the keys and current values of the the track object
            with no dependency on a database session object. """
        out = dict()
        for enum in Reflection.getReflectionList(TrackPropEnum):
            out[enum.name] = getattr(self, enum.name)
        return self._createDict(**out)

#___________________________________________________________________________________________________ toMayaNodeDict
    def toMayaNodeDict(self):
        """ Creates a dictionary representation of the properties that can be controlled directly
            within the Maya scene. """
        out = dict()
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.maya:
                out[enum.maya] = getattr(self, enum.name)
        return out

#___________________________________________________________________________________________________ colorTrack
    def colorTrack(self):
        """ TODO: Kent... """
        if not self.nodeName:
            return False

        if self.pes:
            ShadingUtils.applyShader(TrackwayShaderConfig.DARK_GRAY_COLOR, self.nodeName)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.LIGHT_GRAY_COLOR, self.nodeName)

        if self.left:
            ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR, self.nodeName + '|pointer')
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, self.nodeName + '|pointer')

        return True

#___________________________________________________________________________________________________ setCadenceCamFocus
    def setCadenceCamFocus(self):
        """ TODO: Kent... """
        if self.nodeName is None:
            return

        if not cmds.objExists('CadenceCam'):
            self.initializeCadenceCam()
        height = cmds.xform('CadenceCam', query=True, translation=True)[1]
        cmds.move(self.x, height, self.z, 'CadenceCam', absolute=True)

#___________________________________________________________________________________________________ findExistingTracks
    def findExistingTracks(self, session):
        """ Searches the database for an existing track that matches the current values of the
            unique properties in this track instance and returns a result list of any duplicates
            found. """

        query = session.query(self.__class__)
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.unique:
                query = query.filter(getattr(self.__class__, enum.name) == getattr(self, enum.name))

        return query.all()

#___________________________________________________________________________________________________ getByUid
    @classmethod
    def getByUid(cls, uid, session):
        """ Returns the Tracks_Track model instance for the specified track universally unique id. """
        return session.query(cls).filter(cls.uid == uid).first()

#___________________________________________________________________________________________________ getByProperties
    @classmethod
    def getByProperties(cls, session, **kwargs):
        """ Loads based on the current values set for the track. This form of loading is useful
            when the uid is not available, e.g. when importing data from the spreadsheet. """

        s     = cls.createSession() if session is None else session
        query = s.query(cls)

        for key,value in kwargs.iteritems():
            query = query.filter(getattr(cls, key) == value)

        return query.all()

#___________________________________________________________________________________________________ incrementName
    @classmethod
    def incrementName(cls, name):
        """ TODO: Kent... """
        prefix = name[:2]
        number = int(name[2:])
        return prefix + str(number + 1)

#___________________________________________________________________________________________________ initializeCadenceCam
    @classmethod
    def initializeCadenceCam(cls):
        """ TODO: Kent... """
        c = cmds.camera(
            orthographic=True,
            nearClipPlane=1,
            farClipPlane=100000,
            orthographicWidth=500)
        cmds.rename(c[0], 'CadenceCam')
        cmds.rotate(-90, 180, 0)
        cmds.move(0, 100, 0, 'CadenceCam', absolute=True)
