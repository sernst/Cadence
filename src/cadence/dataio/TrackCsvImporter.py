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

from cadence.data.Track import Track
from cadence.enum.TrackCsvColumnEnum import TrackCsvColumnEnum

#___________________________________________________________________________________________________ TrackCsvImporter
class TrackCsvImporter(object):
    """ Importing data from the """

#===================================================================================================
#                                                                                       C L A S S

    # Used to break trackway specifier into separate type and number entries
    _TRACKWAY_PATTERN = re.compile('(?P<type>[A-Za-z]+)[\s\t]*(?P<number>[0-9]+)')

#___________________________________________________________________________________________________ __init__
    def __init__(self, path =None, logger =None):
        """Creates a new instance of TrackCsvImporter."""
        self._path   = path
        self._tracks = []
        self._logger = logger
        if not logger:
            self._logger = Logger(self, printOut=True)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ read
    def read(self, path =None, force =True):
        """Doc..."""
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

                result  = self.fromSpreadsheetEntry(rowDict, force=force)
                if  isinstance(result, Track):
                    self._tracks.append(result)
                    continue

                self._writeError(result)

#___________________________________________________________________________________________________ fromSpreadsheetEntry
    @classmethod
    def fromSpreadsheetEntry(cls, csvRowData, force =True):
        try:
            csvIndex = int(csvRowData[TrackCsvColumnEnum.INDEX.name])
        except Exception, err:
            return {
                'message':u'Missing spreadsheet index',
                'data':csvRowData }

        t = Track(trackData=dict())

        try:
            t.site  = csvRowData.get(TrackCsvColumnEnum.TRACKSITE.name)
        except Exception, err:
            return {
                'message':u'Missing track site',
                'data':csvRowData,
                'index':csvIndex }

        try:
            t.year = csvRowData.get(TrackCsvColumnEnum.CAST_DATE.name).split('_')[-1]
        except Exception, err:
            return {
                'message':u'Missing cast date',
                'data':csvRowData,
                'index':csvIndex }

        try:
            t.sector = csvRowData.get(TrackCsvColumnEnum.SECTOR.name)
        except Exception, err:
            return {
                'message':u'Missing sector',
                'data':csvRowData,
                'index':csvIndex }

        try:
            t.level = csvRowData.get(TrackCsvColumnEnum.LEVEL.name)
        except Exception, err:
            return {
                'message':u'Missing level',
                'data':csvRowData,
                'index':csvIndex }

        #-------------------------------------------------------------------------------------------
        # TRACKWAY
        #       Parse the trackway entry into type and number values
        try:
            test = csvRowData.get(TrackCsvColumnEnum.TRACKWAY.name).strip()
        except Exception, err:
            return {
                'message':u'Missing trackway',
                'data':csvRowData,
                'index':csvIndex }

        result = cls._TRACKWAY_PATTERN.search(test)
        try:
            t.trackwayType   = result.groupdict()['type']
            t.trackwayNumber = float(result.groupdict()['number'])
        except Exception, err:
            return {
                'message':u'Invalid trackway value: %s' % test,
                'data':csvRowData,
                'result':result,
                'match':result.groupdict() if result else 'N/A',
                'index':csvIndex }

        #-------------------------------------------------------------------------------------------
        # NAME
        #       Parse the name value into left, pes, and number attributes
        try:
            name = csvRowData.get(TrackCsvColumnEnum.TRACK_NAME.name).strip()
        except Exception, err:
            return {
                'message':u'Missing track name',
                'data':csvRowData,
                'index':csvIndex }

        if StringUtils.begins(name.upper(), [u'M', u'P']):
            t.left = name[1].upper() == u'L'
            t.pes  = name[0].upper() == u'P'
        else:
            t.left = name[0].upper() == u'L'
            t.pes  = name[1].upper() == u'P'
        t.number = float(re.compile('[^0-9]+').sub(u'', name[2:]))

        #-------------------------------------------------------------------------------------------
        # FIND EXISTING
        #       Use data set above to attempt to load the track database entry
        if t.loadFromValues() and not force:
            if csvIndex != t.index:
                return {
                    'message':u'Ambiguous track data [%s, %s]:' % (csvIndex, t.index),
                    'data':csvRowData,
                    'existing':t,
                    'index':csvIndex }

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

        # Save csv value changes to the database
        t.save()

        return t

#___________________________________________________________________________________________________ _writeError
    def _writeError(self, data):
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
