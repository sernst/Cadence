# Tracks_Track.py
# (C)2013
# Scott Ernst

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText

from pyaid.ArgsUtils import ArgsUtils

from cadence.enum.TrackPropEnum import TrackPropEnum
# AS NEEDED: from cadence.mayan.trackway.Track import Track
from cadence.models.tracks.TracksDefault import TracksDefault

#___________________________________________________________________________________________________ Tracks_Track
class Tracks_Track(TracksDefault):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    __tablename__  = u'tracks'

    _community           = Column(Unicode, default=u'')
    _site                = Column(Unicode, default=u'')
    _year                = Column(Unicode, default=u'')
    _level               = Column(Unicode, default=u'')
    _sector              = Column(Unicode, default=u'')
    _trackwayType        = Column(Unicode, default=u'')
    _trackwayNumber      = Column(Float, default=0.0)
    _left                = Column(Boolean, default=True)
    _pes                 = Column(Boolean, default=True)
    _number              = Column(Float, default=0.0)

    _prev                = Column(Unicode, default=u'')
    _next                = Column(Unicode, default=u'')
    _snapshot            = Column(Unicode, default=u'')
    _index               = Column(Unicode, default=u'')
    _note                = Column(UnicodeText, default=u'')
    _width               = Column(Float, default=0.0)
    _length              = Column(Float, default=0.0)
    _rotation            = Column(Float, default=0.0)
    _x                   = Column(Float, default=0.0)
    _z                   = Column(Float, default=0.0)
    _widthUncertainty    = Column(Float, default=5.0)
    _lengthUncertainty   = Column(Float, default=5.0)
    _depthUncertainty    = Column(Float, default=5.0)
    _rotationUncertainty = Column(Float, default=5.0)
    _widthMeasured       = Column(Float, default=0.0)
    _lengthMeasured      = Column(Float, default=0.0)
    _depthMeasured       = Column(Float, default=0.0)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ createTrack
    def createTrack(self, node =None):
        from cadence.mayan.trackway.Track import Track
        return Track(node=node, trackId=self.id, trackData=self.toDict())

#___________________________________________________________________________________________________ fromDict
    def fromDict(self, data):
        TPE     = TrackPropEnum
        argsGet = ArgsUtils.get

        self.community           = argsGet(TPE.COMM.name, self.community, data)
        self.site                = argsGet(TPE.SITE.name, self.site, data)
        self.year                = argsGet(TPE.YEAR.name, self.year, data)
        self.level               = argsGet(TPE.LEVEL.name, self.level, data)
        self.sector              = argsGet(TPE.SECTOR.name, self.sector, data)
        self.trackwayNumber      = argsGet(TPE.TRACKWAY_NUMBER.name, self.trackwayNumber, data)
        self.trackwayType        = argsGet(TPE.TRACKWAY_TYPE.name, self.trackwayType, data)
        self.left                = argsGet(TPE.LEFT.name, self.left, data)
        self.pes                 = argsGet(TPE.PES.name, self.pes, data)
        self.number              = argsGet(TPE.NUMBER.name, self.number, data)
        self.note                = argsGet(TPE.NOTE.name, self.note, data)
        self.prev                = argsGet(TPE.PREV.name, self.prev, data)
        self.next                = argsGet(TPE.NEXT.name, self.next, data)
        self.snapshot            = argsGet(TPE.SNAPSHOT.name, self.snapshot, data)
        self.index               = argsGet(TPE.INDEX.name, self.index, data)
        self.width               = argsGet(TPE.WIDTH.name, self.width, data)
        self.rotation            = argsGet(TPE.ROTATION.name, self.rotation, data)
        self.length              = argsGet(TPE.LENGTH.name, self.length, data)
        self.x                   = argsGet(TPE.X.name, self.x, data)
        self.z                   = argsGet(TPE.Z.name, self.z, data)
        self.widthUncertainty    = argsGet(TPE.WIDTH_UNCERTAINTY.name, self.widthUncertainty, data)
        self.lengthUncertainty   = argsGet(TPE.LENGTH_UNCERTAINTY.name, self.lengthUncertainty, data)
        self.rotationUncertainty = argsGet(TPE.ROTATION_UNCERTAINTY.name, self.rotationUncertainty, data)
        self.depthUncertainty    = argsGet(TPE.DEPTH_UNCERTAINTY.name, self.rotationUncertainty, data)
        self.widthMeasured       = argsGet(TPE.WIDTH_UNCERTAINTY.name, self.widthMeasured, data)
        self.lengthMeasured      = argsGet(TPE.LENGTH_UNCERTAINTY.name, self.lengthMeasured, data)
        self.depthMeasured       = argsGet(TPE.DEPTH_UNCERTAINTY.name, self.lengthMeasured, data)

#___________________________________________________________________________________________________ toDict
    def toDict(self):
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
            TPE.NUMBER.name:self.trackwayNumber,
            TPE.NOTE.name:self.note,
            TPE.PREV.name:self.prev,
            TPE.NEXT.name:self.next,
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
            TPE.DEPTH_MEASURED.name:self.depthMeasured })
