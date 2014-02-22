# TrackImporterRemoteThread.py
# (C)2013-2014
# Scott Ernst

from pyglass.threading.RemoteExecutionThread import RemoteExecutionThread

from cadence.data.TrackCsvImporter import TrackCsvImporter
from cadence.data.TrackJsonImporter import TrackJsonImporter
from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ TrackImporterRemoteThread
class TrackImporterRemoteThread(RemoteExecutionThread):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    CSV  = 'csv'
    JSON = 'json'

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, path, importType, session =None, **kwargs):
        """Creates a new instance of TrackImporterRemoteThread."""
        RemoteExecutionThread.__init__(self, parent, **kwargs)
        self._path       = path
        self._session    = session
        self._importType = importType

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _internalMethod
    def _runImpl(self):
        model   = Tracks_Track.MASTER
        session = self._session if self._session else model.createSession()

        try:
            if self._importType == self.CSV:
                importer = TrackCsvImporter(self._path, logger=self._log)
            else:
                importer = TrackJsonImporter(self._path, logger=self._log)
            importer.read(session)
        except Exception, err:
            self._log.writeError('Track CSV Parsing Error', err)
            return 1

        if not self._session:
            session.commit()
            session.close()

        return 0
