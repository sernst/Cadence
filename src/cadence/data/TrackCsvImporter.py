# TrackCsvImporter.py
# (C)2013-2014
# Scott Ernst

import re
import csv

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.reflection.Reflection import Reflection

from cadence.enum.TrackCsvColumnEnum import TrackCsvColumnEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ TrackCsvImporter
class TrackCsvImporter(object):
    """ Imports track data from CSV formatted spreadsheets into the local Cadence database. """

#===================================================================================================
#                                                                                       C L A S S

    # Used to break trackway specifier into separate type and number entries
    _TRACKWAY_PATTERN = re.compile('(?P<type>[A-Za-z]+)[\s\t]*(?P<number>[0-9]+)')

#___________________________________________________________________________________________________ __init__
    def __init__(self, path =None, logger =None):
        """Creates a new instance of TrackCsvImporter."""
        self._path    = path
        self.created  = []
        self.modified = []
        self._logger  = logger
        if not logger:
            self._logger = Logger(self, printOut=True)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ read
    def read(self, session, path =None):
        """ Reads from the spreadsheet located at the absolute path argument and adds each row
            to the tracks in the database. """

        if path is not None:
            self._path = path
        if self._path is None:
            return False

        with open(self._path, 'rU') as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            for row in reader:
                # Skip any rows that don't start with the proper numeric index value, which
                # includes the header row (if it exists) with the column names
                try:
                    index = int(row[0])
                except Exception, err:
                    continue

                rowDict = dict()
                for column in Reflection.getReflectionList(TrackCsvColumnEnum):
                    value = row[column.index]
                    if value != u'' or value is None:
                        rowDict[column.name] = value

                self.fromSpreadsheetEntry(rowDict, session)

        session.flush()
        return True

#___________________________________________________________________________________________________ fromSpreadsheetEntry
    def fromSpreadsheetEntry(self, csvRowData, session):
        """ From the spreadsheet data dictionary representing raw track data, this method creates
            a track entry in the database. """

        try:
            csvIndex = int(csvRowData[TrackCsvColumnEnum.INDEX.name])
        except Exception, err:
            self._writeError({
                'message':u'Missing spreadsheet index',
                'data':csvRowData })
            return False

        t = Tracks_Track.MASTER()

        try:
            t.site  = csvRowData.get(TrackCsvColumnEnum.TRACKSITE.name).strip()
        except Exception, err:
            self._writeError({
                'message':u'Missing track site',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            t.year = csvRowData.get(TrackCsvColumnEnum.CAST_DATE.name).strip().split('_')[-1]
        except Exception, err:
            self._writeError({
                'message':u'Missing cast date',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            t.sector = csvRowData.get(TrackCsvColumnEnum.SECTOR.name)
        except Exception, err:
            self._writeError({
                'message':u'Missing sector',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            t.level = csvRowData.get(TrackCsvColumnEnum.LEVEL.name)
        except Exception, err:
            self._writeError({
                'message':u'Missing level',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # TRACKWAY
        #       Parse the trackway entry into type and number values
        try:
            test = csvRowData.get(TrackCsvColumnEnum.TRACKWAY.name).strip()
        except Exception, err:
            self._writeError({
                'message':u'Missing trackway',
                'data':csvRowData,
                'index':csvIndex })
            return False

        result = self._TRACKWAY_PATTERN.search(test)
        try:
            t.trackwayType   = result.groupdict()['type']
            t.trackwayNumber = float(result.groupdict()['number'])
        except Exception, err:
            self._writeError({
                'message':u'Invalid trackway value: %s' % test,
                'data':csvRowData,
                'result':result,
                'match':result.groupdict() if result else 'N/A',
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # NAME
        #       Parse the name value into left, pes, and number attributes
        try:
            t.name = csvRowData.get(TrackCsvColumnEnum.TRACK_NAME.name).strip()
        except Exception, err:
            self._writeError({
                'message':u'Missing track name',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # FIND EXISTING
        #       Use data set above to attempt to load the track database entry
        existing = t.findExistingTracks(session)
        if existing:
            t = existing[0]
            self.modified.append(t)
        else:
            session.add(t)
            session.flush()
            self.created.append(t)

        t.index     = csvIndex
        t.snapshot  = JSON.asString(csvRowData)

        if t.pes:
            wide      = csvRowData.get(TrackCsvColumnEnum.PES_WIDTH.name)
            wideGuess = csvRowData.get(TrackCsvColumnEnum.PES_WIDTH_GUESS.name)
            longVal   = csvRowData.get(TrackCsvColumnEnum.PES_LENGTH.name)
            longGuess = csvRowData.get(TrackCsvColumnEnum.PES_LENGTH_GUESS.name)
            deep      = csvRowData.get(TrackCsvColumnEnum.PES_DEPTH.name)
            deepGuess = csvRowData.get(TrackCsvColumnEnum.PES_DEPTH_GUESS.name)
        else:
            wide      = csvRowData.get(TrackCsvColumnEnum.MANUS_WIDTH.name)
            wideGuess = csvRowData.get(TrackCsvColumnEnum.MANUS_WIDTH_GUESS.name)
            longVal   = csvRowData.get(TrackCsvColumnEnum.MANUS_LENGTH.name)
            longGuess = csvRowData.get(TrackCsvColumnEnum.MANUS_LENGTH_GUESS.name)
            deep      = csvRowData.get(TrackCsvColumnEnum.MANUS_DEPTH.name)
            deepGuess = csvRowData.get(TrackCsvColumnEnum.MANUS_DEPTH_GUESS.name)

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

        return t

#___________________________________________________________________________________________________ _writeError
    def _writeError(self, data):
        """ Writes import error data to the logger, formatting it for human readable display. """
        source = {}
        for n,v in data['data'].iteritems():
            source[u' '.join(n.split(u'_')).title()] = v

        result  = [
            u'IMPORT ERROR [INDEX: %s]: %s' % (data.get('index', u'Unknown'), data['message']),
            u'DATA: ' + DictUtils.prettyPrint(source)]

        if 'existing' in data:
            source = {}
            for n,v in JSON.fromString(data['existing'].snapshot).iteritems():
                source[u' '.join(n.split(u'_')).title()] = v
            result.append(u'CONFLICT: ' + DictUtils.prettyPrint(source))

        if 'error' in data:
            self._logger.writeError(result, data['error'])
        else:
            self._logger.write(result)

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
