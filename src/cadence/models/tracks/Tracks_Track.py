# Tracks_Track.py
# (C)2013-2014
# Scott Ernst

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from pyaid.ArgsUtils import ArgsUtils

# AS NEEDED: from cadence.data.Track import Track
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.models.tracks.TracksDefault import TracksDefault

#___________________________________________________________________________________________________ Tracks_Track
class Tracks_Track(TracksDefault):
    """ Database model representation of a track with all the attributes and information for a
        specific track as well as a connectivity information for the track within its series. """

#===================================================================================================
#                                                                                       C L A S S

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
    _number              = Column(Float,        default=0.0)
    _index               = Column(Integer,      default=0)
    _snapshot            = Column(Unicode,      default=u'')
    _note                = Column(UnicodeText,  default=u'')
    _prev                = Column(Unicode,      default=u'')
    _next                = Column(Unicode,      default=u'')
    _width               = Column(Float,        default=0.0)
    _length              = Column(Float,        default=0.0)
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

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ createTrack
    def createTrack(self, node =None):
        """ Creates a Track operator instance for this database entry. If a node is specified, it
            is the string name of a Maya node representation of the track, which links the database
            and Maya node through the Track created operator instance. """
        from cadence.data.Track import Track
        return Track(node=node, trackData=self.toDict())

#___________________________________________________________________________________________________ fromDict
    def fromDict(self, data):
        """ Populates the track with the values specified by data dictionary argument. The keys of
            the data object should be valid names of the enumerated values in the TrackPropEnum
            class and the values valid entries for each key in the database class.

            This method can be used to load a track object from disk into a database model. """
        TPE     = TrackPropEnum
        argsGet = ArgsUtils.get

        self.uid                 = argsGet(TPE.UID.name,                    self.uid, data)
        self.community           = argsGet(TPE.COMM.name,                   self.community, data)
        self.site                = argsGet(TPE.SITE.name,                   self.site, data)
        self.year                = argsGet(TPE.YEAR.name,                   self.year, data)
        self.level               = argsGet(TPE.LEVEL.name,                  self.level, data)
        self.sector              = argsGet(TPE.SECTOR.name,                 self.sector, data)
        self.trackwayNumber      = argsGet(TPE.TRACKWAY_NUMBER.name,        self.trackwayNumber, data)
        self.trackwayType        = argsGet(TPE.TRACKWAY_TYPE.name,          self.trackwayType, data)
        self.left                = argsGet(TPE.LEFT.name,                   self.left, data)
        self.pes                 = argsGet(TPE.PES.name,                    self.pes, data)
        self.prev                = argsGet(TPE.PREV.name,                   self.prev, data)
        self.next                = argsGet(TPE.PREV.name,                   self.next, data)
        self.number              = argsGet(TPE.NUMBER.name,                 self.number, data)
        self.note                = argsGet(TPE.NOTE.name,                   self.note, data)
        self.snapshot            = argsGet(TPE.SNAPSHOT.name,               self.snapshot, data)
        self.index               = argsGet(TPE.INDEX.name,                  self.index, data)
        self.width               = argsGet(TPE.WIDTH.name,                  self.width, data)
        self.rotation            = argsGet(TPE.ROTATION.name,               self.rotation, data)
        self.length              = argsGet(TPE.LENGTH.name,                 self.length, data)
        self.x                   = argsGet(TPE.X.name,                      self.x, data)
        self.z                   = argsGet(TPE.Z.name,                      self.z, data)
        self.widthUncertainty    = argsGet(TPE.WIDTH_UNCERTAINTY.name,      self.widthUncertainty, data)
        self.lengthUncertainty   = argsGet(TPE.LENGTH_UNCERTAINTY.name,     self.lengthUncertainty, data)
        self.rotationUncertainty = argsGet(TPE.ROTATION_UNCERTAINTY.name,   self.rotationUncertainty, data)
        self.depthUncertainty    = argsGet(TPE.DEPTH_UNCERTAINTY.name,      self.rotationUncertainty, data)
        self.widthMeasured       = argsGet(TPE.WIDTH_UNCERTAINTY.name,      self.widthMeasured, data)
        self.lengthMeasured      = argsGet(TPE.LENGTH_UNCERTAINTY.name,     self.lengthMeasured, data)
        self.depthMeasured       = argsGet(TPE.DEPTH_UNCERTAINTY.name,      self.lengthMeasured, data)
        self.flags               = argsGet(TPE.FLAGS.name,                  self.flags, data)
        self.sourceFlags         = argsGet(TPE.SOURCE_FLAGS.name,           self.sourceFlags, data)
        self.displayFlags        = argsGet(TPE.DISPLAY_FLAGS.name,          self.displayFlags, data)

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        """ Returns a dictionary containing the keys and current values of the the track object
            with no dependency on a database session object. """
        TPE = TrackPropEnum
        return self._createDict(**{
            TPE.COMM.name:self.community,
            TPE.SITE.name:self.site,
            TPE.YEAR.name:self.year,
            TPE.LEVEL.name:self.level,
            TPE.SECTOR.name:self.sector,
            TPE.TRACKWAY_TYPE.name:self.trackwayType,
            TPE.TRACKWAY_NUMBER.name:self.trackwayNumber,
            TPE.LEFT.name:self.left,
            TPE.PES.name:self.pes,
            TPE.PREV.name:self.prev,
            TPE.NUMBER.name:self.trackwayNumber,
            TPE.NOTE.name:self.note,
            TPE.SNAPSHOT.name:self.snapshot,
            TPE.INDEX.name:self.index,
            TPE.WIDTH.name:self.width,
            TPE.LENGTH.name:self.length,
            TPE.ROTATION.name:self.rotation,
            TPE.X.name:self.x,
            TPE.Z.name:self.z,
            TPE.WIDTH_UNCERTAINTY.name:self.widthUncertainty,
            TPE.LENGTH_UNCERTAINTY.name:self.lengthUncertainty,
            TPE.ROTATION_UNCERTAINTY.name:self.rotationUncertainty,
            TPE.DEPTH_UNCERTAINTY.name:self.depthUncertainty,
            TPE.WIDTH_MEASURED.name:self.widthMeasured,
            TPE.LENGTH_MEASURED.name:self.lengthMeasured,
            TPE.DEPTH_MEASURED.name:self.depthMeasured,
            TPE.FLAGS.name:self.flags,
            TPE.SOURCE_FLAGS.name:self.sourceFlags,
            TPE.DISPLAY_FLAGS.name:self.displayFlags })

#___________________________________________________________________________________________________ getByUid
    @classmethod
    def getByUid(cls, uid, session =None):
        """ Returns the Tracks_Track model instance for the specified track universally unique id. """

        model  = Tracks_Track.MASTER
        s      = model.createSession() if session is None else session
        result = s.query(model).filter(model.uid == uid).first()
        if result is None:
            if session is None:
                s.close()
            return None

        return result
