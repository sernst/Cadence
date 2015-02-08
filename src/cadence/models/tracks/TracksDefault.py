# TracksDefault.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re
import math
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.number.NumericUtils import NumericUtils

import sqlalchemy as sqla
from pyaid.radix.Base64 import Base64
from pyaid.reflection.Reflection import Reflection
from pyaid.string.StringUtils import StringUtils
from pyglass.sqlalchemy.PyGlassModelsDefault import PyGlassModelsDefault
from pyglass.sqlalchemy.ConcretePyGlassModelsMeta import ConcretePyGlassModelsMeta
import six

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.analysis.shared.PositionValue2D import PositionValue2D
from cadence.enums.SourceFlagsEnum import SourceFlagsEnum
from cadence.enums.TrackPropEnum import TrackPropEnum

#___________________________________________________________________________________________________ TracksDefault
# noinspection PyAttributeOutsideInit
@six.add_metaclass(ConcretePyGlassModelsMeta)
class TracksDefault(PyGlassModelsDefault):

#===================================================================================================
#                                                                                       C L A S S

    __abstract__  = True

    # Used to break trackway specifier into separate type and number entries
    _TRACKWAY_PATTERN = re.compile('(?P<type>[A-Za-z]+)[\s\t]*(?P<number>[0-9]+)')

    _uid                 = sqla.Column(sqla.Unicode,     default='')
    _site                = sqla.Column(sqla.Unicode,     default='')
    _year                = sqla.Column(sqla.Unicode,     default='')
    _level               = sqla.Column(sqla.Unicode,     default='')
    _sector              = sqla.Column(sqla.Unicode,     default='')
    _trackwayType        = sqla.Column(sqla.Unicode,     default='')
    _trackwayNumber      = sqla.Column(sqla.Unicode,     default='')
    _number              = sqla.Column(sqla.Unicode,     default='')
    _snapshot            = sqla.Column(sqla.Unicode,     default='')
    _note                = sqla.Column(sqla.UnicodeText, default='')
    _next                = sqla.Column(sqla.Unicode,     default='')
    _left                = sqla.Column(sqla.Boolean,     default=True)
    _pes                 = sqla.Column(sqla.Boolean,     default=True)
    _hidden              = sqla.Column(sqla.Boolean,     default=False)
    _index               = sqla.Column(sqla.Integer,     default=0)
    _width               = sqla.Column(sqla.Float,       default=0.0)
    _length              = sqla.Column(sqla.Float,       default=0.0)
    _rotation            = sqla.Column(sqla.Float,       default=0.0)
    _x                   = sqla.Column(sqla.Float,       default=0.0)
    _z                   = sqla.Column(sqla.Float,       default=0.0)
    _lengthRatio         = sqla.Column(sqla.Float,       default=0.5)
    _widthMeasured       = sqla.Column(sqla.Float,       default=0.0)
    _widthUncertainty    = sqla.Column(sqla.Float,       default=3.0)
    _lengthMeasured      = sqla.Column(sqla.Float,       default=0.0)
    _lengthUncertainty   = sqla.Column(sqla.Float,       default=3.0)
    _depthMeasured       = sqla.Column(sqla.Float,       default=0.0)
    _depthUncertainty    = sqla.Column(sqla.Float,       default=0.5)
    _rotationMeasured    = sqla.Column(sqla.Float,       default=0.0)
    _rotationUncertainty = sqla.Column(sqla.Float,       default=5.0)

    _flags               = sqla.Column(sqla.Integer,     default=0)
    _sourceFlags         = sqla.Column(sqla.Integer,     default=0)
    _displayFlags        = sqla.Column(sqla.Integer,     default=0)
    _importFlags         = sqla.Column(sqla.Integer,     default=0)
    _analysisFlags       = sqla.Column(sqla.Integer,     default=0)

    # Entry is dead for deletion during cleanup/export
    _dead                = sqla.Column(sqla.Boolean,     default=False)

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        super(TracksDefault, self).__init__(**kwargs)
        self.uid = CadenceEnvironment.createUniqueId('track')

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: trackSeries
    @property
    def trackSeries(self):
        """ Used in analysis, this transient data stores a reference to the track series object
            that owns this track. """
        return self.fetchTransient('trackSeries')
    @trackSeries.setter
    def trackSeries(self, value):
        self.putTransient('trackSeries', value)

#___________________________________________________________________________________________________ GS: positionValue
    @property
    def positionValue(self):
        """ Returns a PositionValue2D instance for the position of this track using the 2D RHS
            adjustment of z -> x and x -> y """
        p2d = PositionValue2D()
        p2d.xFromUncertaintyValue(self.zValue)
        p2d.yFromUncertaintyValue(self.xValue)
        return p2d

#___________________________________________________________________________________________________ GS: xValue
    @property
    def xValue(self):
        """ Returns the x value as an uncertainty named tuple in units of meters """
        r    = math.pi/180.0*float(self.rotation)
        rUnc = math.pi/180.0*float(self.rotationUncertainty)
        wUnc = self.widthUncertainty
        lUnc = self.lengthUncertainty
        xUnc = lUnc*abs(math.sin(r)) + wUnc*abs(math.cos(r)) \
            + rUnc*abs(lUnc*math.cos(r) - wUnc*math.sin(r))

        return NumericUtils.toValueUncertainty(0.01*float(self.x), xUnc)

#___________________________________________________________________________________________________ GS: zValue
    @property
    def zValue(self):
        """ Returns the z value as an uncertainty named tuple in units of meters """
        r    = math.pi/180.0*float(self.rotation)
        rUnc = math.pi/180.0*float(self.rotationUncertainty)
        wUnc = self.widthUncertainty
        lUnc = self.lengthUncertainty
        zUnc = lUnc*abs(math.cos(r)) + wUnc*abs(math.sin(r)) \
            + rUnc*abs(wUnc*math.cos(r) - lUnc*math.sin(r))

        return NumericUtils.toValueUncertainty(0.01*float(self.z), zUnc)

#___________________________________________________________________________________________________ GS: isComplete
    @property
    def isComplete(self):
        return SourceFlagsEnum.get(self.sourceFlags, SourceFlagsEnum.COMPLETED)

#___________________________________________________________________________________________________ GS: id
    @property
    def id(self):
        return Base64.to64(self.i)

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        """ Human-readable display name for the track, based of its properties. """
        number = StringUtils.toUnicode(int(self.number)) if self.number else '-'
        return ('L' if self.left else 'R') + ('P' if self.pes else 'M') + number
    @name.setter
    def name(self, value):
        value = value.strip()

        if StringUtils.begins(value.upper(), ['M', 'P']):
            self.left = value[1].upper() == 'L'
            self.pes  = value[0].upper() == 'P'
        else:
            self.left = value[0].upper() == 'L'
            self.pes  = value[1].upper() == 'P'
        self.number = value[2:].upper()

#___________________________________________________________________________________________________ GS: fingerprint
    @property
    def fingerprint(self):
        """ String created from the uniquely identifying track properties. """
        return '%s-%s' % (
            self.trackSeriesFingerprint,
            getattr(self, TrackPropEnum.NUMBER.name, '0') )

#___________________________________________________________________________________________________ GS: trackSeriesFingerprint
    @property
    def trackSeriesFingerprint(self):
        return '-'.join([
            self.trackwayFingerprint,
            'L' if getattr(self, TrackPropEnum.LEFT.name, False) else 'R',
            'P' if getattr(self, TrackPropEnum.PES.name, False) else 'M' ])

#___________________________________________________________________________________________________ GS: trackwayFingerprint
    @property
    def trackwayFingerprint(self):
        return '-'.join([
            getattr(self, TrackPropEnum.SITE.name, ''),
            getattr(self, TrackPropEnum.LEVEL.name, ''),
            getattr(self, TrackPropEnum.YEAR.name, ''),
            getattr(self, TrackPropEnum.SECTOR.name, ''),
            getattr(self, TrackPropEnum.TRACKWAY_TYPE.name, ''),
            getattr(self, TrackPropEnum.TRACKWAY_NUMBER.name, '0') ])

#___________________________________________________________________________________________________ GS: snapshotData
    @property
    def snapshotData(self):
        try:
            return JSON.fromString(self.snapshot)
        except Exception:
            return None
    @snapshotData.setter
    def snapshotData(self, value):
        if not value:
            self.snapshot = ''
        else:
            self.snapshot = JSON.asString(value)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getPreviousTrack
    def getPreviousTrack(self, session =None, getAll =False):
        """ Returns the previous track in the series if such a track exists.  It is found by
            querying to find that other model instance whose 'next' matches this uid. If getAll
            is True the result returns a list of all tracks with a next value matching this
            track's UID, which is useful in finding linkage branching errors. """
        if not session:
            session = self.mySession
        model = self.__class__

        try:
            query = session.query(model).filter(model.next == self.uid)
            if getAll:
                return query.all()
            return query.first()
        except Exception:
            return None

#___________________________________________________________________________________________________ getNextTrack
    def getNextTrack(self, session =None):
        """ Returns the next track in the series if such a track exists.  Unlike getPreviousTrack,
            the next track's uid is explicitly stored in the attribute next, waiting to be used.  A
            query is still required to get the Track_track model instance for that uid. """
        if not session:
            session = self.mySession

        if self.next is None:
            return None
        return self.getByUid(self.next, session=session)

#___________________________________________________________________________________________________ fromDict
    def fromDict(self, data):
        """ Populates the track with the values specified by data dictionary argument. The keys of
            the data object should be valid names of the enumerated values in the TrackPropEnum
            class and the values valid entries for each key in the database class. This method can
            be used to load a track object from disk into a database model. """

        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum == TrackPropEnum.UID:
                continue
            if enum.name in data:
                setattr(self, enum.name, data[enum.name])

#___________________________________________________________________________________________________ toDict
    def toDict(self, uniqueOnly =False):
        """ Returns a dictionary containing the keys and current values of the track object
            with no dependency on a database session object. """

        out = dict(id=self.id, uid=self.uid)
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if uniqueOnly and not enum.unique:
                continue
            out[enum.name] = getattr(self, enum.name)
        return self._createDict(**out)

#___________________________________________________________________________________________________ toMayaNodeDict
    def toMayaNodeDict(self):
        """ Creates a dictionary representation of those properties required for a Maya node. """
        out = dict()
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.maya:
                out[enum.maya] = getattr(self, enum.name)

        # load up the values of left and pes so that they can be used in assigning shaders
        out[TrackPropEnum.LEFT.name]   = getattr(self, TrackPropEnum.LEFT.name)
        out[TrackPropEnum.PES.name]    = getattr(self, TrackPropEnum.PES.name)
        out[TrackPropEnum.HIDDEN.name] = getattr(self, TrackPropEnum.HIDDEN.name)

        # If the width (or length) attribute is still zero, initialize width (or length) to the
        # measured width (or length) from the spreadsheet. But then, if a measured value for
        # width or length is itself still zero (usually due to poor quality track preservation),
        # then assign it a nominal (and visually obvious) small value of 10 cm in UI display.
        if out[TrackPropEnum.WIDTH.maya] == 0.0:
            w = getattr(self, TrackPropEnum.WIDTH_MEASURED.name)
            out[TrackPropEnum.WIDTH.maya] = 0.1 if w == 0.0 else w
        if out[TrackPropEnum.LENGTH.maya] == 0.0:
            w = getattr(self, TrackPropEnum.LENGTH_MEASURED.name)
            out[TrackPropEnum.LENGTH.maya] = 0.1 if w == 0.0 else w
        return out

#___________________________________________________________________________________________________ findExistingTracks
    def findExistingTracks(self, session =None):
        """ Searches the database for an existing track that matches the current values of the UID
            in this track instance and returns a result list of any duplicates found. """
        if not session:
            session = self.mySession
        model = self.__class__
        query = session.query(model)
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.unique:
                query = query.filter(getattr(model, enum.name) == getattr(self, enum.name))
        return query.all()

#___________________________________________________________________________________________________ equivalentProps
    def equivalentProps(self, **kwargs):
        """ Iterates through the kwargs and checks whether or not the values for each kwarg
            property to see if it matches the value for this track instance. """
        for n,v in DictUtils.iter(kwargs):
            if getattr(self, n) != v:
                return False
        return True

#___________________________________________________________________________________________________ getByUid
    @classmethod
    def getByUid(cls, uid, session):
        """ Returns the Tracks_Track model instance for the given UID (universally unique id). """
        try:
            return session.query(cls).filter(cls.uid == uid).first()
        except Exception:
            return None

#___________________________________________________________________________________________________ getByProperties
    @classmethod
    def getByProperties(cls, session, **kwargs):
        """ Loads based on the current values set for the track. This form of loading is useful
            when the uid is not available, e.g. when importing data from the spreadsheet. """
        query = session.query(cls)
        for key,value in DictUtils.iter(kwargs):
            query = query.filter(getattr(cls, key) == value)
        return query.all()

#___________________________________________________________________________________________________ getByName
    @classmethod
    def getByName(cls, name, session, **kwargs):
        """ Returns the Tracks_Track model instance for the specified name (e.g., 'LM3').  Note
            that one filters on other properties as specified by the kwargs. """
        name = name.strip()

        if len(name) < 3:
            return None

        # confusingly, the name might be found in one of two formats, e.g., either LM3 or ML3
        if StringUtils.begins(name.upper(), ['M', 'P']):
            left = name[1].upper() == 'L'
            pes  = name[0].upper() == 'P'
        else:
            left = name[0].upper() == 'L'
            pes  = name[1].upper() == 'P'
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

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __unicode__
    def __str__(self):
        return StringUtils.toStr2('<%s[%s] uid[%s] %s>' % (
            self.__class__.__name__,
            StringUtils.toUnicode(self.i),
            StringUtils.toUnicode(self.uid),
            StringUtils.toUnicode(self.fingerprint)))
