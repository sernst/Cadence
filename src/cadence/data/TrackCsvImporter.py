# TrackCsvImporter.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re
import pandas as pd

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.reflection.Reflection import Reflection
from pyaid.string.StringUtils import StringUtils
from cadence.enums.ImportFlagsEnum import ImportFlagsEnum
from cadence.enums.SnapshotDataEnum import SnapshotDataEnum
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

    _UNDERPRINT_IGNORE_TRACKWAY_STR = ':UTW'
    _OVERPRINT_IGNORE_TRACKWAY_STR = ':OTW'

#___________________________________________________________________________________________________ __init__
    def __init__(self, path =None, logger =None):
        """Creates a new instance of TrackCsvImporter."""
        self._path = path

        self.created  = []
        self.modified = []

        self.createdStore = []
        self.modifiedStore = []

        self.fingerprints = dict()
        self.remainingTracks = dict()
        self._logger  = logger
        if not logger:
            self._logger = Logger(self, printOut=True)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ read
    def read(self, session, analysisSession, path =None, compressed =False):
        """ Reads from the spreadsheet located at the absolute path argument and adds each row
            to the tracks in the database. """

        if path is not None:
            self._path = path
        if self._path is None:
            return False

        model = Tracks_Track.MASTER
        for existingTrack in session.query(model).all():
            self.remainingTracks[existingTrack.uid] = existingTrack.fingerprint

        try:
            data = pd.read_csv(self._path)
        except Exception as err:
            self._writeError({
                'message':'ERROR: Unable to read CSV file "%s"' % self._path,
                'error':err })
            return

        if data is None:
            self._writeError({
                'message':'ERROR: Failed to create CSV reader for file "%s"' % self._path })
            return

        for index, row in data.iterrows():
            # Skip any rows that don't start with the proper numeric index value, which
            # includes the header row (if it exists) with the column names
            try:
                index = int(row[0])
            except Exception:
                continue

            rowDict = dict()
            for column in Reflection.getReflectionList(TrackCsvColumnEnum):
                value = row[column.index]

                if value and not StringUtils.isTextType(value):
                    # Try to decode the value into a unicode string using common codecs
                    for codec in ['utf8', 'MacRoman', 'utf16']:
                        try:
                            decodedValue = value.decode(codec)
                            if decodedValue:
                                value = decodedValue
                                break
                        except Exception:
                            continue

                if value != '' or value is None:
                    rowDict[column.name] = value
                elif column == TrackCsvColumnEnum.MEASURED_DATE:
                    print('\n\n[ERROR Measure date]:', row)

            if TrackCsvColumnEnum.MEASURED_DATE.name not in rowDict:
                print('[ERROR Measure date]:', row)
            self.fromSpreadsheetEntry(rowDict, session)

        for uid, fingerprint in DictUtils.iter(self.remainingTracks):
            # Iterate through the list of remaining tracks, which are tracks not found by the
            # importer. If the track is marked as custom (meaning it is not managed by the importer)
            # it is ignored. Otherwise, the track is deleted from the database as a track that no
            # longer exists.

            track = Tracks_Track.MASTER.getByUid(uid, session)
            if track.custom:
                continue

            Tracks_Track.removeTrack(track, analysisSession)
            self._logger.write('[REMOVED]: No longer exists "%s" (%s)' % (
                track.fingerprint, track.uid))

        session.flush()

        for track in self.created:
            self._logger.write('[CREATED]: "%s" (%s)' % (track.fingerprint, track.uid))

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
        except Exception:
            pass

        try:
            csvIndex = int(csvRowData[TrackCsvColumnEnum.INDEX.name])
        except Exception:
            self._writeError({
                'message':'Missing spreadsheet index',
                'data':csvRowData })
            return False

        model = Tracks_TrackStore.MASTER
        ts = model()
        ts.importFlags = 0
        ts.index = csvIndex

        #-------------------------------------------------------------------------------------------
        # SITE
        try:
            ts.site = csvRowData.get(TrackCsvColumnEnum.TRACKSITE.name).strip().upper()
        except Exception:
            self._writeError({
                'message':'Missing track site',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # SECTOR
        try:
            ts.sector = csvRowData.get(TrackCsvColumnEnum.SECTOR.name).strip().upper()
        except Exception:
            self._writeError({
                'message':'Missing sector',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # LEVEL
        try:
            ts.level = csvRowData.get(TrackCsvColumnEnum.LEVEL.name)
        except Exception:
            self._writeError({
                'message':'Missing level',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # TRACKWAY
        #       Parse the trackway entry into type and number values. In the process illegal
        #       characters are removed to keep the format something that can be handled correctly
        #       within the database.
        try:
            test = csvRowData.get(TrackCsvColumnEnum.TRACKWAY.name).strip().upper()
        except Exception:
            self._writeError({
                'message':'Missing trackway',
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
                return False

        result = self._TRACKWAY_PATTERN.search(test)
        try:
            ts.trackwayType   = result.groupdict()['type'].upper().strip()
            ts.trackwayNumber = result.groupdict()['number'].upper().strip()
        except Exception:
            self._writeError({
                'message':'Invalid trackway value: %s' % test,
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
        except Exception:
            self._writeError({
                'message':'Missing track name',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # YEAR
        try:
            year = csvRowData.get(TrackCsvColumnEnum.MEASURED_DATE.name)

            if not year:
                year = '2014'
            else:

                try:
                    y = StringUtils.toText(year).split(';')[-1].strip().replace(
                        '/', '_').replace(
                        ' ', '').replace(
                        '-', '_').split('_')[-1]
                    year = int(re.compile('[^0-9]+').sub('', y))
                except Exception:
                    year = 2014

                if year > 2999:
                    # When multiple year entries combine into a single large number
                    year = int(StringUtils.toUnicode(year)[-4:])
                elif year < 2000:
                    # When two digit years (e.g. 09) are used instead of four digit years
                    year += 2000

                year = StringUtils.toUnicode(year)

            ts.year = year
        except Exception:
            self._writeError({
                'message':'Missing cast date',
                'data':csvRowData,
                'index':csvIndex })
            return False

        #-------------------------------------------------------------------------------------------
        # FIND EXISTING
        #       Use data set above to attempt to load the track database entry
        fingerprint = ts.fingerprint

        for uid, fp in DictUtils.iter(self.remainingTracks):
            # Remove the fingerprint from the list of fingerprints found in the database, which at
            # the end will leave only those fingerprints that exist in the database but were not
            # touched by the importer. These values can be used to identify tracks that should
            # have been "touched" but were not.
            if fp == fingerprint:
                del self.remainingTracks[uid]
                break

        existingStore = ts.findExistingTracks(session)
        if existingStore and not isinstance(existingStore, Tracks_TrackStore):
            existingStore = existingStore[0]

        if fingerprint in self.fingerprints:
            if not existingStore:
                existingStore = self.fingerprints[fingerprint]

            self._writeError({
                'message':'Ambiguous track entry "%s" [%s -> %s]' % (
                    fingerprint, csvIndex, existingStore.index),
                'data':csvRowData,
                'existing':existingStore,
                'index':csvIndex })
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
            t.fromDict(ts.toDiffDict(t.toDict(), invert=True))
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
                testValue = StringUtils.toText(csvRowData[columnName]).strip().upper()
                if testValue.startswith('NON'):
                    del csvRowData[columnName]

        # Create a snapshot that only includes a subset of properties that are flagged to be
        # included in the database snapshot entry
        snapshot = dict()
        for column in Reflection.getReflectionList(TrackCsvColumnEnum):
            # Include only values that are marked in the enumeration as to be included
            if not column.snapshot or column.name not in csvRowData:
                continue

            value = csvRowData.get(column.name)
            if value is None:
                continue
            elif not value is StringUtils.isStringType(value):
                value = StringUtils.toText(value)

            value = StringUtils.toText(value).strip()
            if value in ['-', b'\xd0'.decode(b'MacRoman')]:
                continue

            snapshot[column.name] = value

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
            print(Logger().echoError('WIDTH PARSE ERROR:', err))
            self._writeError({
                'message':'Width parse error',
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
                TCCE.MANUS_LENGTH, TCCE.MANUS_LENGTH_GUESS,
                '0', IFE.HIGH_LENGTH_UNCERTAINTY, IFE.NO_LENGTH ))

            t.lengthMeasured = ts.lengthMeasured

            if (not existing and not existingStore) or t.lengthUncertainty == 0:
                ts.lengthUncertainty = 0.05 if (ts.importFlags & IFE.HIGH_LENGTH_UNCERTAINTY) else 0.03
                t.lengthUncertainty = ts.lengthUncertainty

        except Exception as err:
            print(Logger().echoError('LENGTH PARSE ERROR:', err))
            self._writeError({
                'message':'Length parse error',
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
            print(Logger().echoError('DEPTH PARSE ERROR:', err))
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
            print(Logger().echoError('ROTATION PARSE ERROR:', err))
            self._writeError({
                'message':'Rotation parse error',
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
                snapshot[SnapshotDataEnum.STRIDE_LENGTH] = 0.01*float(strideLength)*float(strideFactor)
        except Exception as err:
            print(Logger().echoError('STRIDE PARSE ERROR:', err))

        #-------------------------------------------------------------------------------------------
        # WIDTH ANGULATION PATTERN
        try:
            widthAngulation = self._collapseManusPesProperty(
                ts, csvRowData,
                TCCE.WIDTH_PES_ANGULATION_PATTERN, TCCE.WIDTH_PES_ANGULATION_PATTERN_GUESS,
                TCCE.WIDTH_MANUS_ANGULATION_PATTERN, TCCE.WIDTH_MANUS_ANGULATION_PATTERN_GUESS,
                None, IFE.HIGH_WIDTH_ANGULATION_UNCERTAINTY )

            if widthAngulation:
                snapshot[SnapshotDataEnum.WIDTH_ANGULATION_PATTERN] = 0.01*float(widthAngulation)
        except Exception as err:
            print(Logger().echoError('WIDTH ANGULATION PARSE ERROR:', err))

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
                snapshot[SnapshotDataEnum.PACE] = 0.01*float(pace)
        except Exception as err:
            print(Logger().echoError('PACE PARSE ERROR:', err))

        #-------------------------------------------------------------------------------------------
        # PACE ANGULATION PATTERN
        try:
            paceAngulation = self._collapseManusPesProperty(
                ts, csvRowData,
                TCCE.PES_PACE_ANGULATION, TCCE.PES_PACE_ANGULATION_GUESS,
                TCCE.MANUS_PACE_ANGULATION, TCCE.MANUS_PACE_ANGULATION_GUESS,
                None, IFE.HIGH_WIDTH_ANGULATION_UNCERTAINTY )

            if paceAngulation:
                snapshot[SnapshotDataEnum.PACE_ANGULATION_PATTERN] = float(paceAngulation)
        except Exception as err:
            print(Logger().echoError('PACE ANGULATION PARSE ERROR:', err))

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
                snapshot[SnapshotDataEnum.PROGRESSION] = 0.01*float(progression)
        except Exception as err:
            print(Logger().echoError('PROGRESSION PARSE ERROR:', err))

        #-------------------------------------------------------------------------------------------
        # GLENO-ACETABULAR DISTANCE
        try:
            gad = self._collapseGuessProperty(
                ts, csvRowData,
                TCCE.GLENO_ACETABULAR_DISTANCE, TCCE.GLENO_ACETABULAR_DISTANCE_GUESS,
                None, IFE.HIGH_GLENO_ACETABULAR_UNCERTAINTY )

            if gad:
                snapshot[SnapshotDataEnum.GLENO_ACETABULAR_LENGTH] = 0.01*float(gad)
        except Exception as err:
            print(Logger().echoError('GLENO-ACETABULAR DISTANCE PARSE ERROR:', err))

        # Save the snapshot
        try:
            ts.snapshot = JSON.asString(snapshot)
            t.snapshot = ts.snapshot
        except Exception:
            raise

        if TrackCsvColumnEnum.MEASURED_BY.name not in snapshot:
            # Mark entries that have no field measurements with a flag for future reference
            ts.importFlags |= ImportFlagsEnum.NO_FIELD_MEASUREMENTS

        t.importFlags = ts.importFlags

        if existing:
            self.modified.append(t)
        else:
            self.created.append(t)

        if existingStore:
            self.modifiedStore.append(ts)
        else:
            self.createdStore.append(ts)

        return t

#___________________________________________________________________________________________________ _writeError
    def _writeError(self, data):
        """ Writes import error data to the logger, formatting it for human readable display. """
        source = {}

        if 'data' in data:
            for n,v in DictUtils.iter(data['data']):
                source[' '.join(n.split('_')).title()] = v

        indexPrefix = ''
        if 'index' in data:
            indexPrefix = ' [INDEX: %s]:' % data.get('index', 'Unknown')

        result  = [
            'IMPORT ERROR%s: %s' % (indexPrefix, data['message']),
            'DATA: ' + DictUtils.prettyPrint(source)]

        if 'existing' in data:
            source = {}
            snapshot = data['existing'].snapshot
            if snapshot:
                snapshot = JSON.fromString(snapshot)
            if snapshot:
                for n,v in DictUtils.iter(snapshot):
                    source[' '.join(n.split('_')).title()] = v
            result.append('CONFLICT: ' + DictUtils.prettyPrint(source))

        if 'error' in data:
            self._logger.writeError(result, data['error'])
        else:
            self._logger.write(result)

#___________________________________________________________________________________________________ _getStrippedValue
    @classmethod
    def _getStrippedValue(cls, value):
        try:
            return value.strip()
        except Exception:
            return value

#___________________________________________________________________________________________________ _getStrippedRowData
    @classmethod
    def _getStrippedRowData(cls, source, trackCsvEnum):
        out = source.get(trackCsvEnum.name)
        try:
            return out.strip()
        except Exception:
            return out

#___________________________________________________________________________________________________ _collapseManusPesProperty
    @classmethod
    def _collapseManusPesProperty(
            cls, track, csvRowData, pesEnum, pesGuessEnum, manusEnum, manusGuessEnum,
            defaultValue, guessFlag =0, missingFlag =0
    ):

        if track.pes:
            return cls._collapseGuessProperty(
                track=track,
                csvRowData=csvRowData,
                regularPropertyEnum=pesEnum,
                guessPropertyEnum=pesGuessEnum,
                defaultValue=defaultValue,
                guessFlag=guessFlag,
                missingFlag=missingFlag)
        else:
            return cls._collapseGuessProperty(
                track=track,
                csvRowData=csvRowData,
                regularPropertyEnum=manusEnum,
                guessPropertyEnum=manusGuessEnum,
                defaultValue=defaultValue,
                guessFlag=guessFlag,
                missingFlag=missingFlag)

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
