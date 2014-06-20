# TrackCsvImporter.py
# (C)2013-2014
# Scott Ernst

import re
import csv

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.reflection.Reflection import Reflection
from pyaid.string.StringUtils import StringUtils

from cadence.enum.TrackCsvColumnEnum import TrackCsvColumnEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore

#___________________________________________________________________________________________________ TrackCsvImporter
class TrackCsvImporter(object):
    """ Imports track data from CSV formatted spreadsheets into the local Cadence database. """

#===================================================================================================
#                                                                                       C L A S S

    # Used to break trackway specifier into separate type and number entries
    _TRACKWAY_PATTERN = re.compile('(?P<type>[^0-9\s\t]+)[\s\t]*(?P<number>[^\(\s\t]+)')

#___________________________________________________________________________________________________ __init__
    def __init__(self, path =None, logger =None):
        """Creates a new instance of TrackCsvImporter."""
        self._path    = path
        self.created  = []
        self.modified = []
        self.fingerprints = dict()
        self._logger  = logger
        if not logger:
            self._logger = Logger(self, printOut=True)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ read
    def read(self, session, path =None, compressed =False):
        """ Reads from the spreadsheet located at the absolute path argument and adds each row
            to the tracks in the database. """

        if path is not None:
            self._path = path
        if self._path is None:
            return False

        with open(self._path, 'rU') as f:
            try:
                reader = csv.reader(f, delimiter=',', quotechar='"')
            except Exception, err:
                self._writeError({
                    'message':u'ERROR: Unable to read CSV file "%s"' % self._path,
                    'error':err })
                return

            if reader is None:
                self._writeError({
                    'message':u'ERROR: Failed to create CSV reader for file "%s"' % self._path })
                return

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

                    if not isinstance(value, unicode):
                        value = StringUtils.strToUnicode(value)

                    if value != u'' or value is None:
                        rowDict[column.name] = value

                self.fromSpreadsheetEntry(rowDict, session)

        session.flush()

        return True

#___________________________________________________________________________________________________ fromSpreadsheetEntry
    def fromSpreadsheetEntry(self, csvRowData, session):
        """ From the spreadsheet data dictionary representing raw track data, this method creates
            a track entry in the database. """

        #-------------------------------------------------------------------------------------------
        # MISSING
        #       Try to determine if the missing value has been set for this row data. If so and it
        #       has been marked missing, skip the track during import to prevent importing tracks
        #       with no data.
        try:
            missingValue = csvRowData[TrackCsvColumnEnum.MISSING.name].strip()
            if missingValue:
                return False
        except Exception, err:
            pass

        try:
            csvIndex = int(csvRowData[TrackCsvColumnEnum.INDEX.name])
        except Exception, err:
            self._writeError({
                'message':u'Missing spreadsheet index',
                'data':csvRowData })
            return False

        model = Tracks_TrackStore.MASTER
        ts = model()

        try:
            ts.site  = csvRowData.get(TrackCsvColumnEnum.TRACKSITE.name).strip().upper()
        except Exception, err:
            self._writeError({
                'message':u'Missing track site',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            year = csvRowData.get(TrackCsvColumnEnum.CAST_DATE.name)
            if not year:
                year = u'2014'
            else:

                year = int(re.compile('[^0-9]+').sub(u'', year.strip().split('_')[-1]))
                if year > 2999:
                    # When multiple year entries combine into a single large number
                    year = int(unicode(year)[-4:])
                elif year < 2000:
                    # When two digit years (e.g. 09) are used instead of four digit years
                    year += 2000

                year = unicode(year)

            ts.year = year
        except Exception, err:
            self._writeError({
                'message':u'Missing cast date',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            ts.sector = csvRowData.get(TrackCsvColumnEnum.SECTOR.name).strip().upper()
        except Exception, err:
            self._writeError({
                'message':u'Missing sector',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            ts.level = csvRowData.get(TrackCsvColumnEnum.LEVEL.name)
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
            ts.trackwayType   = result.groupdict()['type'].upper().strip()
            ts.trackwayNumber = result.groupdict()['number'].upper().strip()
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
            ts.name = csvRowData.get(TrackCsvColumnEnum.TRACK_NAME.name).strip()
        except Exception, err:
            self._writeError({
                'message':u'Missing track name',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # MEASUREMENTS
        #       Parse the length, width, and depth measurements. If any are missing then assign
        #       zero values as the default, which will be adjusted later in Maya
        if ts.pes:
            wide      = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.PES_WIDTH)
            wideGuess = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.PES_WIDTH_GUESS)
            longVal   = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.PES_LENGTH)
            longGuess = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.PES_LENGTH_GUESS)
            deep      = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.PES_DEPTH)
            deepGuess = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.PES_DEPTH_GUESS)
        else:
            wide      = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.MANUS_WIDTH)
            wideGuess = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.MANUS_WIDTH_GUESS)
            longVal   = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.MANUS_LENGTH)
            longGuess = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.MANUS_LENGTH_GUESS)
            deep      = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.MANUS_DEPTH)
            deepGuess = self._getStrippedRowData(csvRowData, TrackCsvColumnEnum.MANUS_DEPTH_GUESS)

        if not wide and not wideGuess:
            wide = 0
            wideGuess = 0

        if not longVal and not longGuess:
            longVal = 0
            longGuess = 0

        if not deep and not deepGuess:
            deep = 0
            deepGuess = 0

        #-------------------------------------------------------------------------------------------
        # SKIP
        #       Redundant tracks are skipped. This has been disabled to keep the database record
        #       aligned with the original spreadsheet. Skipping will be handled internally instead
        #       of at import time.
        ##doSkip = ts.equivalentProps(
        ##    site=u'BEB', level=u'515', trackwayType=u'S', trackwayNumber=u'3', year=u'2006')
        ##if doSkip and (ts.number == u'1' or (ts.number == u'2' and ts.left and ts.pes)):
        ##    self._logger.write(u'SKIPPED: ' + DictUtils.prettyPrint(ts.toDict()))
        ##    return False

        #-------------------------------------------------------------------------------------------
        # FIND EXISTING
        #       Use data set above to attempt to load the track database entry
        fingerprint = ts.fingerprint
        existing    = ts.findExistingTracks(session)
        if existing or fingerprint in self.fingerprints:
            if not existing:
                existing = self.fingerprints[fingerprint]

            self._writeError({
                'message':u'Ambiguous track entry [#%s -> #%s]' % (csvIndex, existing.index),
                'data':csvRowData,
                'existing':existing,
                'index':csvIndex })
            return False
        self.fingerprints[fingerprint] = ts

        if existing:
            ts = existing[0]
        else:
            session.add(ts)
            session.flush()

        ts.index = csvIndex
        ts.snapshot = JSON.asString(csvRowData)

        #-------------------------------------------------------------------------------------------
        # WIDTH
        #       Parse the width into a numerical value and assign appropriate default uncertainty
        try:
            ts.widthMeasured     = 0.01*float(wide if wide else wideGuess)
            ts.widthUncertainty  = 0.05 if wideGuess else 0.03
        except Exception, err:
            self._writeError({
                'message':u'Width parse error: ' + unicode(wide if wide else wideGuess),
                'data':csvRowData,
                'index':csvIndex })
            ts.widthMeasured    = 0.0
            ts.widthUncertainty = 0.05

        #-------------------------------------------------------------------------------------------
        # LENGTH
        #       Parse the length into a numerical value and assign appropriate default uncertainty
        try:
            ts.lengthMeasured    = 0.01*float(longVal if longVal else longGuess)
            ts.lengthUncertainty = 0.05 if longGuess else 0.05
        except Exception, err:
            self._writeError({
                'message':u'Length parse error: ' + unicode(longVal if longVal else longGuess),
                'data':csvRowData,
                'index':csvIndex })
            ts.lengthMeasured    = 0.0
            ts.lengthUncertainty = 0.05

        #-------------------------------------------------------------------------------------------
        # DEPTH
        #       Parse the depth into a numerical value and assign appropriate default uncertainty
        try:
            ts.depthMeasured     = 0.01*float(deep if deep else deepGuess)
            ts.depthUncertainty  = 0.05 if deepGuess else 0.03
        except Exception, err:
            ts.depthMeasured    = 0.0
            ts.depthUncertainty = 0.05

        t = ts.getMatchingTrack(session)
        if t is None:
            model = Tracks_Track.MASTER
            t = model()
            t.uid = ts.uid
            t.fromDict(ts.toDict())
            session.add(t)
            session.flush()
            self.created.append(t)
        else:
            t.fromDict(ts.toDiffDict(t.toDict()))
            self.modified.append(ts)

        return t

#___________________________________________________________________________________________________ _writeError
    def _writeError(self, data):
        """ Writes import error data to the logger, formatting it for human readable display. """
        source = {}

        if 'data' in data:
            for n,v in data['data'].iteritems():
                source[u' '.join(n.split(u'_')).title()] = v

        indexPrefix = u''
        if 'index' in data:
            indexPrefix = u' [INDEX: %s]:' % data.get('index', u'Unknown')

        result  = [
            u'IMPORT ERROR%s: %s' % (indexPrefix, data['message']),
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

#___________________________________________________________________________________________________ _getStrippedRowData
    @classmethod
    def _getStrippedRowData(cls, source, trackCsvEnum):
        out = source.get(trackCsvEnum.name)
        try:
            return out.strip()
        except Exception, err:
            return out

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
