# TrackCsvImporter.py
# (C)2013-2014
# Scott Ernst

import re
import csv

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.reflection.Reflection import Reflection
from cadence.data.TrackLinkConnector import TrackLinkConnector

from cadence.enum.TrackCsvColumnEnum import TrackCsvColumnEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ TrackCsvImporter
from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore


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

        linker = TrackLinkConnector()
        linker.run(self.created, session)

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

        ts = Tracks_TrackStore.MASTER()

        try:
            ts.site  = csvRowData.get(TrackCsvColumnEnum.TRACKSITE.name).strip().upper()
        except Exception, err:
            self._writeError({
                'message':u'Missing track site',
                'data':csvRowData,
                'index':csvIndex })
            return False

        try:
            #ts.year = csvRowData.get(TrackCsvColumnEnum.CAST_DATE.name).strip().split('_')[-1]
            pass
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

        ts.index     = csvIndex
        ts.snapshot  = JSON.asString(csvRowData)

        if ts.pes:
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
            ts.widthMeasured     = float(wide if wide else wideGuess)
            ts.widthUncertainty  = 5.0 if wideGuess else 4.0
        except Exception, err:
            ts.widthMeasured    = 0.0
            ts.widthUncertainty = 5.0

        try:
            ts.lengthMeasured    = float(long if longVal else longGuess)
            ts.lengthUncertainty = 5.0 if longGuess else 4.0
        except Exception, err:
            ts.lengthMeasured    = 0.0
            ts.lengthUncertainty = 5.0

        try:
            ts.depthMeasured     = float(deep if deep else deepGuess)
            ts.depthUncertainty  = 5.0 if deepGuess else 4.0
        except Exception, err:
            ts.depthMeasured    = 0.0
            ts.depthUncertainty = 5.0

        t = ts.getMatchingTrack(session)
        if t is None:
            t     = Tracks_Track()
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
