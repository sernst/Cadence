# TrackJsonImporter.py
# (C)2014
# Scott Ernst

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.reflection.Reflection import Reflection
from cadence.enum.TrackPropEnum import TrackPropEnumOps
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ TrackJsonImporter
class TrackJsonImporter(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, path =None, logger =None):
        """Creates a new instance of TrackJsonImporter."""
        self._path          = path
        self._modified      = []
        self._missing       = []
        self._unresolvable  = []
        self._logger = logger
        if not logger:
            self._logger = Logger(self, printOut=True)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ read
    def read(self, session, path =None, gzipped =False):
        """ Reads from the spreadsheet located at the absolute path argument and adds each row
            to the tracks in the database. """

        if path is not None:
            self._path = path
        if self._path is None:
            self._logger.write('ERROR: No path specified. Import aborted.')
            return False

        try:
            tracksData = JSON.fromFile(self._path, gzipped=gzipped)
        except Exception, err:
            self._logger.writeError('ERROR: Unable to read JSON import file', err)
            return False

        for trackEntry in tracksData:
            self._parseTrackEntry(trackEntry, session)

        return True

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _parseTrackEntry
    def _parseTrackEntry(self, data, session):
        """Doc..."""
        searchData = dict()
        for name,value in data.iteritems():
            enum = TrackPropEnumOps.getTrackPropEnumByName(name)
            if not enum:
                continue
            if enum.unique:
                searchData[name] = value

        result = Tracks_Track.MASTER.getByProperties(session, **searchData)
        if not result:
            self._logger.write(
                'WARNING: Missing track for data: ' + DictUtils.prettyPrint(searchData))
            self._missing.append(data)
            return

        if len(result) > 1:
            self._logger.write(
                'WARNING: Ambiguous track data: ' + DictUtils.prettyPrint(searchData))
            for r in result:
                print '    ', DictUtils.prettyPrint(r.toDict(uniqueOnly=True))
            self._unresolvable.append(data)
            return

        track = result[0]
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum in data:
                setattr(track, enum.name, data[enum.name])

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
        return '<%s>' % self.__class__.__name__
