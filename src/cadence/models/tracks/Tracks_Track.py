# Tracks_Track.py
# (C)2013
# Scott Ernst

from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText

from pyaid.ArgsUtils import ArgsUtils

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
    _trackway            = Column(Unicode, default=u'')
    _name                = Column(Unicode, default=u'')
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
    _widthUncertainty    = Column(Float, default=0.0)
    _lengthUncertainty   = Column(Float, default=0.0)
    _rotationUncertainty = Column(Float, default=0.0)
    _widthMeasured       = Column(Float, default=0.0)
    _lengthMeasured      = Column(Float, default=0.0)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ createTrack
    def createTrack(self, node =None):
        from cadence.mayan.trackway.Track import Track
        return Track(node=node, trackUid=self.id, trackData=self.toDict())

#___________________________________________________________________________________________________ fromDict
    def fromDict(self, data):
        argsGet = ArgsUtils.get

        self.community           = argsGet('community', self.community, data)
        self.site                = argsGet('site', self.site, data)
        self.year                = argsGet('year', self.year, data)
        self.level               = argsGet('level', self.level, data)
        self.sector              = argsGet('sector', self.sector, data)
        self.trackway            = argsGet('trackway', self.trackway, data)
        self.name                = argsGet('name', self.name, data)
        self.note                = argsGet('note', self.note, data)
        self.prev                = argsGet('prev', self.prev, data)
        self.next                = argsGet('next', self.next, data)
        self.snapshot            = argsGet('snapshot', self.snapshot, data)
        self.index               = argsGet('index', self.index, data)
        self.width               = argsGet('width', self.width, data)
        self.rotation            = argsGet('rotation', self.rotation, data)
        self.length              = argsGet('length', self.length, data)
        self.x                   = argsGet('x', self.x, data)
        self.z                   = argsGet('z', self.z, data)
        self.widthUncertainty    = argsGet('widthUncertainty', self.widthUncertainty, data)
        self.lengthUncertainty   = argsGet('lengthUncertainty', self.lengthUncertainty, data)
        self.rotationUncertainty = argsGet('rotationUncertainty', self.rotationUncertainty, data)
        self.widthMeasured       = argsGet('widthMeasured', self.widthMeasured, data)
        self.lengthMeasured      = argsGet('lengthMeasured', self.lengthMeasured, data)

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        return self._createDict(
            community=self.community,
            site=self.site,
            year=self.year,
            level=self.level,
            sector=self.sector,
            trackway=self.trackway,
            name=self.name,
            note=self.note,
            prev=self.prev,
            next=self.next,
            snapshot=self.snapshot,
            index=self.index,
            width=self.width,
            length=self.length,
            rotation=self.rotation,
            x=self.x,
            z=self.z,
            widthUncertainty=self.widthUncertainty,
            lengthUncertainty=self.lengthUncertainty,
            rotationUncertainty=self.rotationUncertainty,
            widthMeasured=self.widthMeasured,
            lengthMeasured=self.lengthMeasured )
