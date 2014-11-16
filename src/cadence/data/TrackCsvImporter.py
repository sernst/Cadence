# TrackCsvImporter.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re
import csv

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.reflection.Reflection import Reflection
from pyaid.string.StringUtils import StringUtils
from cadence.enums.ImportFlagsEnum import ImportFlagsEnum
from cadence.enums.SnapshotFlagsEnum import SnapshotFlagsEnum
from cadence.enums.TrackCsvColumnEnum import TrackCsvColumnEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore

#___________________________________________________________________________________________________ TrackCsvImporter
class TrackCsvImporter(object):
    """ Imports track data from CSV formatted spreadsheets into the local Cadence database. """

#===================================================================================================
#                                                                                       C L A S S

    # Used to break trackway specifier into separate type and number entries
    _TRACKWAY_PATTERN = re.compile('(?P<type>[^0-9\s\t]+)[\s\t]*(?P<number>[^\(\s\t]+)')

    _UNDERPRINT_IGNORE_TRACKWAY_STR = u':UTW'
    _OVERPRINT_IGNORE_TRACKWAY_STR = u':OTW'

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
                reader = csv.reader(
                    f,
                    delimiter=StringUtils.toStr2(','),
                    quotechar=StringUtils.toStr2('"'))
            except Exception as err:
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
                except Exception as err:
                    continue

                rowDict = dict()
                for column in Reflection.getReflectionList(TrackCsvColumnEnum):
                    value = row[column.index]
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

        removeAndSkip = False

        #-------------------------------------------------------------------------------------------
        # MISSING
        #       Try to determine if the missing value has been set for this row data. If so and it
        #       has been marked missing, skip the track during import to prevent importing tracks
        #       with no data.
        try:
            missingValue = csvRowData[TrackCsvColumnEnum.MISSING.name].strip()
            if missingValue:
                removeAndSkip = True
        except Exception as err:
            pass

        try:
            csvIndex = int(csvRowData[TrackCsvColumnEnum.INDEX.name])
        except Exception as err:
            self._writeError({
                'message':u'Missing spreadsheet index',
                'data':csvRowData })
            return False

        model = Tracks_TrackStore.MASTER
        ts = model()
        ts.importFlags = 0

        try:
            ts.site = csvRowData.get(TrackCsvColumnEnum.TRACKSITE.name).strip().upper()
        except Exception as err:
            self._writeError({
                'message':u'Missing track site',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            year = csvRowData.get(TrackCsvColumnEnum.MEASURED_DATE.name)
            if not year:
                year = u'2014'
            else:

                year = int(re.compile('[^0-9]+').sub(u'', year.strip().split('_')[-1]))
                if year > 2999:
                    # When multiple year entries combine into a single large number
                    year = int(StringUtils.toUnicode(year)[-4:])
                elif year < 2000:
                    # When two digit years (e.g. 09) are used instead of four digit years
                    year += 2000

                year = StringUtils.toUnicode(year)

            ts.year = year
        except Exception as err:
            self._writeError({
                'message':u'Missing cast date',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            ts.sector = csvRowData.get(TrackCsvColumnEnum.SECTOR.name).strip().upper()
        except Exception as err:
            self._writeError({
                'message':u'Missing sector',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            ts.level = csvRowData.get(TrackCsvColumnEnum.LEVEL.name)
        except Exception as err:
            self._writeError({
                'message':u'Missing level',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # TRACKWAY
        #       Parse the trackway entry into type and number values
        try:
            test = csvRowData.get(TrackCsvColumnEnum.TRACKWAY.name).strip().upper()
        except Exception as err:
            self._writeError({
                'message':u'Missing trackway',
                'data':csvRowData,
                'index':csvIndex })
            return False

        # If the trackway contains an ignore pattern then return without creating the track.
        # This is used for tracks in the record that are actually under-prints from a higher
        # level recorded in the spreadsheet only for catalog reference.
        testIndexes = [
            test.find(self._UNDERPRINT_IGNORE_TRACKWAY_STR),
            test.find(self._OVERPRINT_IGNORE_TRACKWAY_STR) ]

        testParensIndex = test.find('(')
        for testIndex in testIndexes:
            if testIndex != -1 and (testParensIndex == -1 or testParensIndex > testIndex):
                removeAndSkip = True
                break

        result = self._TRACKWAY_PATTERN.search(test)
        try:
            ts.trackwayType   = result.groupdict()['type'].upper().strip()
            ts.trackwayNumber = result.groupdict()['number'].upper().strip()
        except Exception as err:
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
        except Exception as err:
            self._writeError({
                'message':u'Missing track name',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # FIND EXISTING
        #       Use data set above to attempt to load the track database entry
        fingerprint = ts.fingerprint
        existingStore = ts.findExistingTracks(session)
        if existingStore and not isinstance(existingStore, Tracks_TrackStore):
            existingStore = existingStore[0]

        if (existingStore and existingStore.index != csvIndex) or fingerprint in self.fingerprints:
            if not existingStore:
                existingStore = self.fingerprints[fingerprint]

            self._writeError({
                'message':u'Ambiguous track entry [#%s -> #%s]' % (csvIndex, existingStore.index),
                'data':csvRowData,
                'existing':existingStore,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # REMOVE MISSING/SKIPPED
        #       If the track is missing or should be skipped for some reason remove any existing
        #       entries from the database, which may exist due to previous imports that handled
        #       the import process differently.
        if removeAndSkip:
            t = None
            if existingStore:
                t = existingStore.getMatchingTrack(session)
                session.delete(existingStore)

            if t is None:
                t = ts.getMatchingTrack(session)

            if t is not None:
                session.delete(t)

            if existingStore or t:
                self._logger.write(u'<div>REMOVED TRACK: "%s"</div>' % fingerprint)
            return False

        self.fingerprints[fingerprint] = ts

        if existingStore:
            ts = existingStore
        else:
            session.add(ts)
            session.flush()

        existing = ts.getMatchingTrack(session)
        if existing is None:
            model = Tracks_Track.MASTER
            t = model()
            t.uid = ts.uid
            t.fromDict(ts.toDiffDict(t.toDict()))
            session.add(t)
            session.flush()
        else:
            t = existing

        t.indx = csvIndex
        ts.index = csvIndex

        TCCE = TrackCsvColumnEnum
        IFE  = ImportFlagsEnum

        #-------------------------------------------------------------------------------------------
        # CSV PROPERTY CLEANUP
        #       Cleanup and format additional CSV values before saving the csv data to the track's
        #       snapshot.
        removeNonColumns = [
            TrackCsvColumnEnum.PRESERVED.name,
            TrackCsvColumnEnum.CAST.name,
            TrackCsvColumnEnum.OUTLINE_DRAWING.name]
        for columnName in removeNonColumns:
            if columnName in csvRowData:
                testValue = csvRowData[columnName].strip().upper()
                if testValue.startswith('NON'):
                    del csvRowData[columnName]

        # Create a snapshot that only includes a subset of properties that are flagged to be
        # included in the database snapshot entry
        snapshot = dict()
        for column in Reflection.getReflectionList(TrackCsvColumnEnum):
            # Exclude values that are marked in the enumeration as not to be included
            if not column.snapshot or column.name not in csvRowData:
                continue
            snapshot[column.name] = csvRowData[column.name]

        #-------------------------------------------------------------------------------------------
        # WIDTH
        #       Parse the width into a numerical value and assign appropriate default uncertainty
        try:
            ts.widthMeasured = 0.01*float(self._collapseManusPesProperty(
                ts, csvRowData,
                TCCE.PES_WIDTH, TCCE.PES_WIDTH_GUESS,
                TCCE.MANUS_WIDTH, TCCE.MANUS_WIDTH_GUESS,
                '0', IFE.HIGH_WIDTH_UNCERTAINTY, IFE.NO_WIDTH ))

            t.widthMeasured = ts.widthMeasured

            if (not existing and not existingStore) or t.widthUncertainty == 0:
                ts.widthUncertainty = 0.05 if (ts.importFlags & IFE.HIGH_WIDTH_UNCERTAINTY) else 0.03
                t.widthUncertainty = ts.widthUncertainty

        except Exception as err:
            print(Logger().echoError(u'WIDTH PARSE ERROR:', err))
            self._writeError({
                'message':u'Width parse error',
                'data':csvRowData,
                'error':err,
                'index':csvIndex })

            ts.widthMeasured = 0.0
            if not existingStore:
                ts.widthUncertainty = 0.05

        #-------------------------------------------------------------------------------------------
        # LENGTH
        #       Parse the length into a numerical value and assign appropriate default uncertainty
        try:
            ts.lengthMeasured = 0.01*float(self._collapseManusPesProperty(
                ts, csvRowData,
                TCCE.PES_LENGTH, TCCE.PES_LENGTH_GUESS,
                TCCE.MANUS_WIDTH, TCCE.MANUS_WIDTH_GUESS,
                '0', ImportFlagsEnum.HIGH_LENGTH_UNCERTAINTY, ImportFlagsEnum.NO_LENGTH ))

            t.lengthMeasured = ts.lengthMeasured

            if (not existing and not existingStore) or t.lengthUncertainty == 0:
                ts.lengthUncertainty = 0.05 if (ts.importFlags & IFE.HIGH_LENGTH_UNCERTAINTY) else 0.03
                t.lengthUncertainty = ts.lengthUncertainty

        except Exception as err:
            print(Logger().echoError(u'LENGTH PARSE ERROR:', err))
            self._writeError({
                'message':u'Length parse error',
                'data':csvRowData,
                'error':err,
                'index':csvIndex })

            ts.lengthMeasured = 0.0
            if not existingStore:
                ts.lengthUncertainty = 0.05

        #-------------------------------------------------------------------------------------------
        # DEPTH
        #       Parse the depth into a numerical value and assign appropriate default uncertainty
        try:
            ts.depthMeasured = 0.01*float(self._collapseManusPesProperty(
                ts, csvRowData,
                TCCE.PES_DEPTH, TCCE.PES_DEPTH_GUESS,
                TCCE.MANUS_DEPTH, TCCE.MANUS_DEPTH_GUESS,
                '0', IFE.HIGH_DEPTH_UNCERTAINTY, 0 ))

            t.depthMeasured = ts.depthMeasured

            if (not existing and not existingStore) or t.depthUncertainty == 0:
                ts.depthUncertainty = 0.05 if IFE.HIGH_DEPTH_UNCERTAINTY else 0.03
                t.depthUncertainty = ts.depthUncertainty

        except Exception as err:
            print(Logger().echoError(u'DEPTH PARSE ERROR:', err))
            ts.depthMeasured = 0.0

            if not existingStore:
                ts.depthUncertainty = 0.05


        #-------------------------------------------------------------------------------------------
        # ROTATION
        #       Parse the rotation into a numerical value and assign appropriate default uncertainty
        try:
            ts.rotationMeasured = float(self._collapseLimbProperty(
                ts, csvRowData,
                TCCE.LEFT_PES_ROTATION, TCCE.LEFT_PES_ROTATION_GUESS,
                TCCE.RIGHT_PES_ROTATION, TCCE.RIGHT_PES_ROTATION_GUESS,
                TCCE.LEFT_MANUS_ROTATION, TCCE.LEFT_MANUS_ROTATION_GUESS,
                TCCE.RIGHT_MANUS_ROTATION, TCCE.RIGHT_MANUS_ROTATION_GUESS,
                '0', IFE.HIGH_ROTATION_UNCERTAINTY, 0 ))

            t.rotationMeasured = ts.rotationMeasured

            if not existingStore and not existing:
                ts.rotationUncertainty = 10.0 if IFE.HIGH_ROTATION_UNCERTAINTY else 45.0
                t.rotationUncertainty = ts.rotationUncertainty

        except Exception as err:
            print(Logger().echoError(u'ROTATION PARSE ERROR:', err))
            self._writeError({
                'message':u'Rotation parse error',
                'error':err,
                'data':csvRowData,
                'index':csvIndex })

            ts.rotationMeasured  = 0.0
            if not existingStore:
                ts.rotationUncertainty = 45.0

        #-------------------------------------------------------------------------------------------
        # STRIDE
        try:
            strideLength = self._collapseManusPesProperty(
                ts, csvRowData,
                TCCE.PES_STRIDE, TCCE.PES_STRIDE_GUESS,
                TCCE.MANUS_STRIDE, TCCE.MANUS_STRIDE_GUESS,
                None, IFE.HIGH_STRIDE_UNCERTAINTY )

            strideFactor = self._collapseManusPesProperty(
                ts, csvRowData,
                TCCE.PES_STRIDE_FACTOR, None,
                TCCE.MANUS_STRIDE_FACTOR, None, 1.0)

            if strideLength:
                snapshot[SnapshotFlagsEnum.STRIDE_LENGTH] = 0.01*float(strideLength)*float(strideFactor)
        except Exception as err:
            print(Logger().echoError(u'STRIDE PARSE ERROR:', err))

        #-------------------------------------------------------------------------------------------
        # WIDTH ANGULATION PATTERN
        try:
            widthAngulation = self._collapseManusPesProperty(
                ts, csvRowData,
                TCCE.WIDTH_PES_ANGULATION_PATTERN, TCCE.WIDTH_PES_ANGULATION_PATTERN_GUESS,
                TCCE.WIDTH_MANUS_ANGULATION_PATTERN, TCCE.WIDTH_MANUS_ANGULATION_PATTERN_GUESS,
                None, IFE.HIGH_WIDTH_ANGULATION_UNCERTAINTY )

            if widthAngulation:
                snapshot[SnapshotFlagsEnum.WIDTH_ANGULATION_PATTERN] = 0.01*float(widthAngulation)
        except Exception as err:
            print(Logger().echoError(u'WIDTH ANGULATION PARSE ERROR:', err))

        #-------------------------------------------------------------------------------------------
        # PACE
        try:
            pace = self._collapseLimbProperty(
                ts, csvRowData,
                TCCE.LEFT_PES_PACE, TCCE.LEFT_PES_PACE_GUESS,
                TCCE.RIGHT_PES_PACE, TCCE.RIGHT_PES_PACE_GUESS,
                TCCE.LEFT_MANUS_PACE, TCCE.LEFT_MANUS_PACE_GUESS,
                TCCE.RIGHT_MANUS_PACE, TCCE.RIGHT_MANUS_PACE_GUESS,
                None, IFE.HIGH_PACE_UNCERTAINTY )

            if pace:
                snapshot[SnapshotFlagsEnum.PACE] = 0.01*float(pace)
        except Exception as err:
            print(Logger().echoError(u'PACE PARSE ERROR:', err))

        #-------------------------------------------------------------------------------------------
        # PACE ANGULATION PATTERN
        try:
            paceAngulation = self._collapseManusPesProperty(
                ts, csvRowData,
                TCCE.PES_PACE_ANGULATION, TCCE.PES_PACE_ANGULATION_GUESS,
                TCCE.MANUS_PACE_ANGULATION, TCCE.MANUS_PACE_ANGULATION_GUESS,
                None, IFE.HIGH_WIDTH_ANGULATION_UNCERTAINTY )

            if paceAngulation:
                snapshot[SnapshotFlagsEnum.PACE_ANGULATION_PATTERN] = float(paceAngulation)
        except Exception as err:
            print(Logger().echoError(u'PACE ANGULATION PARSE ERROR:', err))

        #-------------------------------------------------------------------------------------------
        # PROGRESSION
        try:
            progression = self._collapseLimbProperty(
                ts, csvRowData,
                TCCE.LEFT_PES_PROGRESSION, TCCE.LEFT_PES_PROGRESSION_GUESS,
                TCCE.RIGHT_PES_PROGRESSION, TCCE.RIGHT_PES_PROGRESSION_GUESS,
                TCCE.LEFT_MANUS_PROGRESSION, TCCE.LEFT_MANUS_PROGRESSION_GUESS,
                TCCE.RIGHT_MANUS_PROGRESSION, TCCE.RIGHT_MANUS_PROGRESSION_GUESS,
                None, IFE.HIGH_PROGRESSION_UNCERTAINTY )

            if progression:
                snapshot[SnapshotFlagsEnum.PROGRESSION] = 0.01*float(progression)
        except Exception as err:
            print(Logger().echoError(u'PROGRESSION PARSE ERROR:', err))

        #-------------------------------------------------------------------------------------------
        # GLENO-ACETABULAR DISTANCE
        try:
            gad = self._collapseGuessProperty(
                ts, csvRowData,
                TCCE.GLENO_ACETABULAR_DISTANCE, TCCE.GLENO_ACETABULAR_DISTANCE_GUESS,
                None, IFE.HIGH_GLENO_ACETABULAR_UNCERTAINTY )

            if gad:
                snapshot[SnapshotFlagsEnum.GLENO_ACETABULAR_LENGTH] = 0.01*float(gad)
        except Exception as err:
            print(Logger().echoError(u'GLENO-ACETABULAR DISTANCE PARSE ERROR:', err))

        # Save the snapshot
        try:
            ts.snapshot = JSON.asString(snapshot)
            t.snapshot = ts.snapshot
        except Exception as err:
            print('TrackStore:', ts)
            raise

        t.importFlags = ts.importFlags

        if existingStore:
            self.modified.append(ts)
        else:
            self.created.append(ts)

        return t

#___________________________________________________________________________________________________ _writeError
    def _writeError(self, data):
        """ Writes import error data to the logger, formatting it for human readable display. """
        source = {}

        if 'data' in data:
            for n,v in DictUtils.iter(data['data']):
                source[u' '.join(n.split(u'_')).title()] = v

        indexPrefix = u''
        if 'index' in data:
            indexPrefix = u' [INDEX: %s]:' % data.get('index', u'Unknown')

        result  = [
            u'IMPORT ERROR%s: %s' % (indexPrefix, data['message']),
            u'DATA: ' + DictUtils.prettyPrint(source)]

        if 'existing' in data:
            source = {}
            for n,v in DictUtils.iter(JSON.fromString(data['existing'].snapshot)):
                source[u' '.join(n.split(u'_')).title()] = v
            result.append(u'CONFLICT: ' + DictUtils.prettyPrint(source))

        if 'error' in data:
            self._logger.writeError(result, data['error'])
        else:
            self._logger.write(result)

#___________________________________________________________________________________________________ _getStrippedValue
    @classmethod
    def _getStrippedValue(cls, value):
        try:
            return value.strip()
        except Exception as err:
            return value

#___________________________________________________________________________________________________ _getStrippedRowData
    @classmethod
    def _getStrippedRowData(cls, source, trackCsvEnum):
        out = source.get(trackCsvEnum.name)
        try:
            return out.strip()
        except Exception as err:
            return out

#___________________________________________________________________________________________________ _collapseManusPesProperty
    @classmethod
    def _collapseManusPesProperty(
            cls, track, csvRowData, pesEnum, pesGuessEnum, manusEnum, manusGuessEnum,
            defaultValue, guessFlag =0, missingFlag =0
    ):

        if track.pes:
            return cls._collapseGuessProperty(
                track, csvRowData, pesEnum, pesGuessEnum, defaultValue, guessFlag, missingFlag)
        else:
            return cls._collapseGuessProperty(
                track, csvRowData, manusEnum, manusGuessEnum, defaultValue, guessFlag, missingFlag)

#___________________________________________________________________________________________________ _collapseLimbProperty
    @classmethod
    def _collapseLimbProperty(
            cls, track, csvRowData, lpEnum, lpGuessEnum, rpEnum, rpGuessEnum, lmEnum, lmGuessEnum,
            rmEnum, rmGuessEnum, defaultValue, guessFlag =0, missingFlag =0
    ):

        if track.pes and track.left:
            return cls._collapseGuessProperty(
                track, csvRowData, lpEnum, lpGuessEnum, defaultValue, guessFlag, missingFlag)
        elif track.pes and not track.left:
            return cls._collapseGuessProperty(
                track, csvRowData, rpEnum, rpGuessEnum, defaultValue, guessFlag, missingFlag)
        elif not track.pes and track.left:
            return cls._collapseGuessProperty(
                track, csvRowData, lmEnum, lmGuessEnum, defaultValue, guessFlag, missingFlag)
        elif not track.pes and not track.left:
            return cls._collapseGuessProperty(
                track, csvRowData, rmEnum, rmGuessEnum, defaultValue, guessFlag, missingFlag)
        else:
            return None

#___________________________________________________________________________________________________ _collapseGuessProperty
    @classmethod
    def _collapseGuessProperty(
            cls, track, csvRowData, regularPropertyEnum, guessPropertyEnum, defaultValue,
            guessFlag =0, missingFlag =0
    ):
        value = cls._getStrippedRowData(csvRowData, regularPropertyEnum)
        if guessPropertyEnum:
            valueGuess = cls._getStrippedRowData(csvRowData, guessPropertyEnum)
        else:
            valueGuess = None

        if not value:
            if not valueGuess:
                track.importFlags |= (missingFlag & guessFlag)
                return defaultValue

            track.importFlags |= guessFlag
            return valueGuess

        return value

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return StringUtils.toUnicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
