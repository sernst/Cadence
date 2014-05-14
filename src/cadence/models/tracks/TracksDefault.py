# TracksDefault.py
# (C)2013-2014
# Scott Ernst

import re

import sqlalchemy as sqla

from pyaid.radix.Base64 import Base64
from pyaid.reflection.Reflection import Reflection
from pyaid.string.StringUtils import StringUtils

from pyglass.sqlalchemy.PyGlassModelsDefault import PyGlassModelsDefault
from pyglass.sqlalchemy.ConcretePyGlassModelsMeta import ConcretePyGlassModelsMeta

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enum.TrackPropEnum import TrackPropEnum

#___________________________________________________________________________________________________ TracksDefault
class TracksDefault(PyGlassModelsDefault):

#===================================================================================================
#                                                                                       C L A S S

    __metaclass__ = ConcretePyGlassModelsMeta
    __abstract__  = True

    # Used to break trackway specifier into separate type and number entries
    _TRACKWAY_PATTERN = re.compile('(?P<type>[A-Za-z]+)[\s\t]*(?P<number>[0-9]+)')

    _uid                 = sqla.Column(sqla.Unicode,      default=u'')
    _community           = sqla.Column(sqla.Unicode,      default=u'')
    _site                = sqla.Column(sqla.Unicode,      default=u'')
    _year                = sqla.Column(sqla.Unicode,      default=u'')
    _level               = sqla.Column(sqla.Unicode,      default=u'')
    _sector              = sqla.Column(sqla.Unicode,      default=u'')
    _trackwayType        = sqla.Column(sqla.Unicode,      default=u'')
    _trackwayNumber      = sqla.Column(sqla.Unicode,      default=u'')
    _number              = sqla.Column(sqla.Unicode,      default=u'')
    _snapshot            = sqla.Column(sqla.Unicode,      default=u'')
    _note                = sqla.Column(sqla.UnicodeText,  default=u'')
    _next                = sqla.Column(sqla.Unicode,      default=u'')
    _left                = sqla.Column(sqla.Boolean,      default=True)
    _pes                 = sqla.Column(sqla.Boolean,      default=True)
    _index               = sqla.Column(sqla.Integer,      default=0)
    _width               = sqla.Column(sqla.Float,        default=1.0)
    _length              = sqla.Column(sqla.Float,        default=1.0)
    _rotation            = sqla.Column(sqla.Float,        default=0.0)
    _x                   = sqla.Column(sqla.Float,        default=0.0)
    _z                   = sqla.Column(sqla.Float,        default=0.0)
    _forwardLengthRatio  = sqla.Column(sqla.Float,        default=0.5)
    _widthMeasured       = sqla.Column(sqla.Float,        default=0.0)
    _widthUncertainty    = sqla.Column(sqla.Float,        default=5.0)
    _lengthMeasured      = sqla.Column(sqla.Float,        default=0.0)
    _lengthUncertainty   = sqla.Column(sqla.Float,        default=5.0)
    _depthMeasured       = sqla.Column(sqla.Float,        default=0.0)
    _depthUncertainty    = sqla.Column(sqla.Float,        default=5.0)
    _rotationMeasured    = sqla.Column(sqla.Float,        default=0.0)
    _rotationUncertainty = sqla.Column(sqla.Float,        default=5.0)

    _flags               = sqla.Column(sqla.Integer,      default=0)
    _sourceFlags         = sqla.Column(sqla.Integer,      default=0)
    _displayFlags        = sqla.Column(sqla.Integer,      default=0)

    # Entry is dead for deletion during cleanup/export
    _dead                = sqla.Column(sqla.Boolean,      default=False)

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        super(TracksDefault, self).__init__(**kwargs)
        self.uid = CadenceEnvironment.createUniqueId(u'track')

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: id
    @property
    def id(self):
        return Base64.to64(self.i)

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        """ Human-readable display name for the track, based of its properties. """
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

#___________________________________________________________________________________________________ GS: fingerprint
    @property
    def fingerprint(self):
        out = []
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.unique:
                out.append(unicode(getattr(self, enum.name)))
        return u'|'.join(out)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getPreviousTrack
    def getPreviousTrack(self, session):
        """ Returns the previous track in the series if such a track exists """
        model = self.__class__
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

#___________________________________________________________________________________________________ fromDict
    def fromDict(self, data):
        """ Populates the track with the values specified by data dictionary argument. The keys of
            the data object should be valid names of the enumerated values in the TrackPropEnum
            class and the values valid entries for each key in the database class.

            This method can be used to load a track object from disk into a database model. """
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum == TrackPropEnum.UID:
                continue

            if enum.name in data:
                setattr(self, enum.name, data[enum.name])

#___________________________________________________________________________________________________ toDict
    def toDict(self, uniqueOnly =False):
        """ Returns a dictionary containing the keys and current values of the track object
            with no dependency on a database session object. """
        out = dict(id=self.id)
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if uniqueOnly and not enum.unique:
                continue
            out[enum.name] = getattr(self, enum.name)
        return self._createDict(**out)

#___________________________________________________________________________________________________ toMayaNodeDict
    def toMayaNodeDict(self):
        """ Creates a dictionary representation of those properties that can be controlled directly
            within the Maya scene. """
        out = dict()
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.maya:
                out[enum.maya] = getattr(self, enum.name)
        return out

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
        """ Returns the Tracks_Track model instance for the given UID (universally unique id). """
        return session.query(cls).filter(cls.uid == uid).first()

#___________________________________________________________________________________________________ getByProperties
    @classmethod
    def getByProperties(cls, session, **kwargs):
        """ Loads based on the current values set for the track. This form of loading is useful
            when the uid is not available, e.g. when importing data from the spreadsheet. """

        query = session.query(cls)

        for key,value in kwargs.iteritems():
            query = query.filter(getattr(cls, key) == value)

        return query.all()

#___________________________________________________________________________________________________ getByName
    @classmethod
    def getByName(cls, name, session, **kwargs):
        """ Returns the Tracks_Track model instance for the specified name (e.g., 'LM3').  Note
            that one filters on other properties as specified by the kwargs. """
        name = name.strip()

        if StringUtils.begins(name.upper(), [u'M', u'P']):
            left = name[1].upper() == u'L'
            pes  = name[0].upper() == u'P'
        else:
            left = name[0].upper() == u'L'
            pes  = name[1].upper() == u'P'
        number = name[2:].upper()
        kwargs[TrackPropEnum.LEFT.name]   = left
        kwargs[TrackPropEnum.PES.name]    = pes
        kwargs[TrackPropEnum.NUMBER.name] = number
        results = cls.getByProperties(session, **kwargs)
        return results

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _createDict
    def _createDict(self, **kwargs):
        kwargs['id'] = self.id
        return kwargs
