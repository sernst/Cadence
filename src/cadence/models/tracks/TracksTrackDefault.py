# TracksTrackDefault.py
# (C)2013-2015
# Scott Ernst

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import re

import sqlalchemy as sqla
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.number.Angle import Angle
from pyaid.number.NumericUtils import NumericUtils
from pyaid.number.PositionValue2D import PositionValue2D
from pyaid.radix.Base64 import Base64
from pyaid.reflection.Reflection import Reflection
from pyaid.string.StringUtils import StringUtils

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enums.AnalysisFlagsEnum import AnalysisFlagsEnum
from cadence.enums.ImportFlagsEnum import ImportFlagsEnum
from cadence.enums.SourceFlagsEnum import SourceFlagsEnum
from cadence.enums.SourceFlagsEnum import SourceFlagsEnumOps
from cadence.enums.TrackPropEnum import TrackPropEnum
from cadence.models.tracks.TracksDefault import TracksDefault


# noinspection PyAttributeOutsideInit
class TracksTrackDefault(TracksDefault):

    __abstract__  = True

    # Used to break trackway specifier into separate type and number entries
    _TRACKWAY_PATTERN = re.compile(
        '(?P<type>[A-Za-z]+)[\s\t]*(?P<number>[0-9]+)')

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

    # Tracks entered manually that do not exist in a source spreadsheet for
    # import. Such tracks are ignored by the import process.
    _custom = sqla.Column(sqla.Boolean, default=False)

    # The source of the track material. Allows us to enter tracks from multiple
    # source for comparison.
    _source = sqla.Column(sqla.Unicode, default='A16')

    # Index of the imported material within the source spreadsheet.
    _index = sqla.Column(sqla.Integer, default=0)

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

    def __init__(self, **kwargs):
        """

        :param kwargs:
        """

        super(TracksTrackDefault, self).__init__(**kwargs)
        self.uid = CadenceEnvironment.createUniqueId('track')

    @property
    def widthValue(self):
        return NumericUtils.toValueUncertainty(
            self.width, self.widthUncertainty)

    @property
    def lengthValue(self):
        return NumericUtils.toValueUncertainty(
            self.length, self.lengthUncertainty)

    #___________________________________________________________________________
    @property
    def trackSeries(self):
        """ Used in analysis, this transient data stores a reference to the
            track series object that owns this track.
        """
        return self.fetchTransient('trackSeries')
    @trackSeries.setter
    def trackSeries(self, value):
        self.putTransient('trackSeries', value)

    @property
    def positionValue(self):
        """
        Returns a PositionValue2D instance for the position of this track using
        the 2D RHS adjustment of z -> x and x -> y

        :return:
        """

        p2d = PositionValue2D()
        p2d.xFromUncertaintyValue(self.zValue)
        p2d.yFromUncertaintyValue(self.xValue)
        return p2d

    @property
    def positionValueRaw(self):
        """
        Returns a PositionValue2D instance for the position of this track using
        the raw values of the position and uncertainty with the 2D RHS
        adjustment of z -> x and x -> y

        :return:
        """

        return PositionValue2D(
            x=self.zValue.raw,
            xUnc=self.zValue.rawUncertainty,
            y=self.xValue.raw,
            yUnc=self.xValue.rawUncertainty
        )

    #___________________________________________________________________________
    @property
    def xValue(self):
        """ Returns the x value as an uncertainty named tuple in units of meters
        """
        r    = math.pi/180.0*float(self.rotation)
        rUnc = math.pi/180.0*float(self.rotationUncertainty)
        wUnc = self.widthUncertainty
        lUnc = self.lengthUncertainty
        xUnc = lUnc*abs(math.sin(r)) + wUnc*abs(math.cos(r)) \
            + rUnc*abs(lUnc*math.cos(r) - wUnc*math.sin(r))

        return NumericUtils.toValueUncertainty(0.01*float(self.x), xUnc)

    #___________________________________________________________________________
    @property
    def zValue(self):
        """ Returns the z value as an uncertainty named tuple in units of meters
        """
        r    = math.pi/180.0*float(self.rotation)
        rUnc = math.pi/180.0*float(self.rotationUncertainty)
        wUnc = self.widthUncertainty
        lUnc = self.lengthUncertainty
        zUnc = lUnc*abs(math.cos(r)) + wUnc*abs(math.sin(r)) \
            + rUnc*abs(wUnc*math.cos(r) - lUnc*math.sin(r))

        return NumericUtils.toValueUncertainty(0.01*float(self.z), zUnc)

    #___________________________________________________________________________
    @property
    def rotationAngle(self):
        """ Returns a Angle instance containing the rotation value and
            uncertainty information for the track based off the Cadence data
            values (not the measured ones).
        """
        return Angle(
            degrees=self.rotation,
            uncertaintyDegrees=self.rotationUncertainty)

    #___________________________________________________________________________
    @property
    def isComplete(self):
        return SourceFlagsEnumOps.get(
            self.sourceFlags,
            SourceFlagsEnum.COMPLETED)

    #___________________________________________________________________________
    @property
    def id(self):
        return Base64.to64(self.i)

    #___________________________________________________________________________
    @property
    def name(self):
        """ Human-readable display name for the track, based of its properties.
        """
        number = StringUtils.toUnicode(int(self.number)) if self.number else '*'
        return '%s%s%s' % (
            ('L' if self.left else 'R'),
            ('P' if self.pes else 'M'),
            number)
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

    #___________________________________________________________________________
    @property
    def shortFingerprint(self):
        return ''.join([
            'L' if getattr(self, TrackPropEnum.LEFT.name, False) else 'R',
            'P' if getattr(self, TrackPropEnum.PES.name, False) else 'M',
            StringUtils.toText(
                getattr(self, TrackPropEnum.NUMBER.name, '0'))
                .replace('-', 'N') ])

    #___________________________________________________________________________
    @property
    def fingerprint(self):
        """ String created from the uniquely identifying track properties. """
        TPE = TrackPropEnum
        return '-'.join([
            StringUtils.toText(getattr(self, TPE.SITE.name, '')),
            StringUtils.toText(getattr(self, TPE.LEVEL.name, '')),
            StringUtils.toText(getattr(self, TPE.YEAR.name, '')),
            StringUtils.toText(getattr(self, TPE.SECTOR.name, '')),
            StringUtils.toText(getattr(self, TPE.TRACKWAY_TYPE.name, '')),
            StringUtils.toText(getattr(self, TPE.TRACKWAY_NUMBER.name, '0')),
            'L' if getattr(self, TPE.LEFT.name, False) else 'R',
            'P' if getattr(self, TPE.PES.name, False) else 'M',
            StringUtils.toText(
                getattr(self, TPE.NUMBER.name, '0'))
                .replace('-', 'N') ])

    #___________________________________________________________________________
    @property
    def trackSeriesFingerprint(self):
        TPE = TrackPropEnum
        return '-'.join([
            self.trackwayFingerprint,
            'L' if getattr(self, TPE.LEFT.name, False) else 'R',
            'P' if getattr(self, TPE.PES.name, False) else 'M' ])

    #___________________________________________________________________________
    @property
    def trackwayFingerprint(self):
        TPE = TrackPropEnum
        out = '-'.join([
            StringUtils.toText(getattr(self, TPE.SITE.name, '')),
            StringUtils.toText(getattr(self, TPE.LEVEL.name, '')),
            StringUtils.toText(getattr(self, TPE.YEAR.name, '')),
            StringUtils.toText(getattr(self, TPE.SECTOR.name, '')),
            StringUtils.toText(getattr(self, TPE.TRACKWAY_TYPE.name, '')),
            StringUtils.toText(getattr(self, TPE.TRACKWAY_NUMBER.name, '0')) ])

        if out == 'TCH-1000-2014-12-S-13BIS':
            # Fix a naming ambiguity from the catalog
            out = 'TCH-1000-2006-12-S-13'
        return out

    #___________________________________________________________________________
    @property
    def sitemapDisplayLabel(self):
        """ Returns the display label used for annotating tracks on sitemap
            drawings (CadenceDrawing files)
        """
        return '%s%s-%s' % (
            getattr(self, TrackPropEnum.TRACKWAY_TYPE.name, ''),
            getattr(self, TrackPropEnum.TRACKWAY_NUMBER.name, '0'),
            self.name)

    #___________________________________________________________________________
    @property
    def snapshotData(self):
        try:
            out = JSON.fromString(self.snapshot)
            return out if out is not None else dict()
        except Exception:
            return dict()
    @snapshotData.setter
    def snapshotData(self, value):
        if not value:
            self.snapshot = ''
        else:
            self.snapshot = JSON.asString(value)

    #===========================================================================
    #                                                               P U B L I C

    #___________________________________________________________________________
    def hasAnalysisFlag(self, flag):
        return flag & self.analysisFlags

    #___________________________________________________________________________
    def hasImportFlag(self, flag):
        return flag & self.importFlags

    #___________________________________________________________________________
    def echoAnalysisFlags(self, separator =' | '):
        """echoAnalysisFlags doc..."""
        out = []
        enums = Reflection.getReflectionDict(AnalysisFlagsEnum)
        for key, value in DictUtils.iter(enums):
            if value & self.analysisFlags:
                out.append(key)
        return ('[%s]' % separator.join(out)) if out else '--'

    #___________________________________________________________________________
    def echoImportFlags(self, separator =' | '):
        """echoImportFlags doc..."""
        out = []
        d = Reflection.getReflectionDict(ImportFlagsEnum)
        for key, value in DictUtils.iter(d):
            if value & self.importFlags:
                out.append(key)
        return ('[%s]' % separator.join(out)) if out else '--'

    #___________________________________________________________________________
    def getPreviousTrack(self, session =None, getAll =False):
        """ Returns the previous track in the series if such a track exists.
            It is found by querying to find that other model instance whose
            'next' matches this uid. If getAll is True the result returns a
            list of all tracks with a next value matching this track's UID,
            which is useful in finding linkage branching errors.
        """
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

    def getNextTrack(self, session =None):
        """ Returns the next track in the series if such a track exists.
            Unlike getPreviousTrack, the next track's uid is explicitly stored
            in the attribute next, waiting to be used.  A query is still
            required to get the Track_track model instance for that uid.
        """
        if not session:
            session = self.mySession

        if self.next is None:
            return None
        return self.getByUid(self.next, session=session)

    def fromDict(self, data):
        """ Populates the track with the values specified by data dictionary
            argument. The keys of the data object should be valid names of the
            enumerated values in the TrackPropEnum class and the values valid
            entries for each key in the database class. This method can be used
            to load a track object from disk into a database model.
        """
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum == TrackPropEnum.UID:
                continue
            if enum.name in data:
                setattr(self, enum.name, data[enum.name])

    def toDict(self, uniqueOnly =False):
        """ Returns a dictionary containing the keys and current values of the
            track object with no dependency on a database session object.
        """
        out = dict(id=self.id, uid=self.uid)
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if uniqueOnly and not enum.unique:
                continue
            out[enum.name] = getattr(self, enum.name)
        return self._createDict(**out)

    def toMayaNodeDict(self):
        """ Creates a dictionary representation of those properties required
            for a Maya node.
        """
        TPE = TrackPropEnum
        out = dict()
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.maya:
                out[enum.maya] = getattr(self, enum.name)

        # load up the values of left and pes so that they can be used in
        # assigning shaders
        out[TPE.LEFT.name]   = getattr(self, TPE.LEFT.name)
        out[TPE.PES.name]    = getattr(self, TPE.PES.name)
        out[TPE.HIDDEN.name] = getattr(self, TPE.HIDDEN.name)

        # If the width (or length) attribute is still zero, initialize width
        # (or length) to the measured width (or length) from the spreadsheet.
        # But then, if a measured value for width or length is itself still
        # zero (usually due to poor quality track preservation), then assign
        # it a nominal (and visually obvious) small value of 10 cm in UI
        # display.
        if out[TPE.WIDTH.maya] == 0.0:
            w = getattr(self, TPE.WIDTH_MEASURED.name)
            out[TPE.WIDTH.maya] = 0.1 if w == 0.0 else w
        if out[TPE.LENGTH.maya] == 0.0:
            w = getattr(self, TPE.LENGTH_MEASURED.name)
            out[TPE.LENGTH.maya] = 0.1 if w == 0.0 else w
        return out

    def findExistingTracks(self, session =None):
        """ Searches the database for an existing track that matches the
            current values of the UID in this track instance and returns a
            result list of any duplicates found.
        """
        if not session:
            session = self.mySession
        model = self.__class__
        query = session.query(model)
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.unique:
                query = query.filter(
                    getattr(model, enum.name) == getattr(self, enum.name))
        return query.all()

    def equivalentProps(self, **kwargs):
        """ Iterates through the kwargs and checks whether or not the values
            for each kwarg property to see if it matches the value for this
            track instance.
        """
        for n,v in DictUtils.iter(kwargs):
            if getattr(self, n) != v:
                return False
        return True

    @classmethod
    def getByUid(cls, uid, session):
        """ Returns the Tracks_Track model instance for the given UID
            (universally unique id).
        """
        try:
            return session.query(cls).filter(cls.uid == uid).first()
        except Exception:
            return None

    @classmethod
    def getByProperties(cls, session, **kwargs):
        """ Loads based on the current values set for the track. This form of
            loading is useful when the uid is not available, e.g. when
            importing data from the spreadsheet.
        """
        query = session.query(cls)
        for key,value in DictUtils.iter(kwargs):
            query = query.filter(getattr(cls, key) == value)
        return query.all()

    @classmethod
    def getByName(cls, name, session, **kwargs):
        """ Returns the Tracks_Track model instance for the specified name
            (e.g., 'LM3').  Note that one filters on other properties as
            specified by the kwargs.
        """
        name = name.strip()

        if len(name) < 3:
            return None

        # confusingly, the name might be found in one of two formats, e.g.,
        # either LM3 or ML3
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

    def _createDict(self, **kwargs):
        kwargs['id'] = self.id
        return kwargs

    def __str__(self):
        return StringUtils.toStr2('<%s[%s] uid[%s] %s>' % (
            self.__class__.__name__,
            StringUtils.toUnicode(self.i),
            StringUtils.toUnicode(self.uid),
            StringUtils.toUnicode(self.fingerprint)))
