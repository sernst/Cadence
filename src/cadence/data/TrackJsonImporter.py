# TrackJsonImporter.py
# (C)2014
# Scott Ernst

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from cadence.enum.TrackPropEnum import TrackPropEnumOps
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.data.TrackExporter import TrackExporter

#___________________________________________________________________________________________________ TrackJsonImporter
from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore


class TrackJsonImporter(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, path =None, logger =None, verbose =True):
        """Creates a new instance of TrackJsonImporter."""

        self.verbose = verbose

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
    def read(self, session, path =None, compressed =False):
        """ Reads from the spreadsheet located at the absolute path argument and adds each row
            to the tracks in the database. """

        if path is not None:
            self._path = path
        if self._path is None:
            self._logger.write('ERROR: No path specified. Import aborted.')
            return False

        try:
            tracksData = JSON.fromFile(self._path, gzipped=compressed)
        except Exception, err:
            self._logger.writeError('ERROR: Unable to read JSON import file', err)
            return False

        for trackEntry in tracksData:
            if TrackExporter.DELETED_IDENTIFIER in trackEntry:
                self._deleteTrackEntry(trackEntry, session)
            else:
                self._parseTrackEntry(trackEntry, session)

        return True

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _deleteTrackEntry
    def _deleteTrackEntry(self, data, session):
        model = Tracks_Track.MASTER

        track = model.getByUid(data['uid'], session)
        if track is None:
            return True

        session.delete(track)
        return True

#___________________________________________________________________________________________________ _parseTrackEntry
    def _parseTrackEntry(self, data, session):
        """Doc..."""
        model = Tracks_Track.MASTER
        storageModel = Tracks_TrackStore.MASTER
        tracks = None
        trackStores = None

        # If a UID is present in the data use that to retrieve the track instance
        if TrackPropEnum.UID.name in data:
            uid = data[TrackPropEnum.UID.name]
            tracks = model.getByUid(uid, session)
            tracks = [tracks] if tracks else None

            trackStores = storageModel.getByUid(uid, session)
            trackStores = [trackStores] if trackStores else None

        # If no UID or no track with the specified UID exists attempt to find the track by its
        # uniquely identifying properties
        if tracks is None:
            tracks = self._getTrackByProps(data, session, model)
        if trackStores is None:
            trackStores = self._getTrackByProps(data, session, storageModel)

        if not tracks or not trackStores:
            self._logger.write(
                u'WARNING: Missing track for data:\n    ' + DictUtils.prettyPrint(data))
            self._missing.append(data)
            return

        if len(tracks) > 1 or len(trackStores) > 1:
            msg = [u'WARNING: Ambiguous track data: ' + DictUtils.prettyPrint(data)]
            for r in tracks:
                msg.append('    ' + DictUtils.prettyPrint(r.toDict(uniqueOnly=True)))
            self._logger.write('\n'.join(msg))
            self._unresolvable.append(data)
            return

        tracks[0].fromDict(data)
        trackStores[0].fromDict(data)

        displayData = DictUtils.clone(data)
        if 'uid' in displayData:
            del displayData['uid']

        logEntry = (u'<div style="background-color:#FFFFFF;">'
             + u'<span style="font-size:18px;color:#333333;font-weight:bold;">UPDATED:</span> '
             + u'<span style="color:#AA3333;">[uid: %s]</span> '
             + u'<span style="color:#33AA33;">[fingerprint: %s]</span>') % (
                trackStores[0].uid,
                trackStores[0].fingerprint)

        if self.verbose:
            logEntry += u'\n\t* %s</div>' % DictUtils.prettyPrint(displayData, u'\n\t* ')

        self._logger.write(logEntry)

#___________________________________________________________________________________________________ _getTrackByProps
    def _getTrackByProps(self, data, session, model):
        searchData = dict()

        for name,value in data.iteritems():
            enum = TrackPropEnumOps.getTrackPropEnumByName(name)
            if not enum:
                continue
            if enum.unique:
                searchData[name] = value

        return model.getByProperties(session, **searchData)

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
