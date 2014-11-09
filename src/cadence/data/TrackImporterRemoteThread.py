# TrackImporterRemoteThread.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.ArgsUtils import ArgsUtils
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
        self._compressed = ArgsUtils.extract('compressed', False, kwargs)

        RemoteExecutionThread.__init__(self, parent, **kwargs)
        self._path       = path
        self._session    = session
        self._importType = importType
        self._verbose    = ArgsUtils.get('verbose', True, kwargs)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _runImpl
    def _runImpl(self):
        model   = Tracks_Track.MASTER
        session = self._session if self._session else model.createSession()

        try:
            if self._importType == self.CSV:
                importer = TrackCsvImporter(self._path, logger=self._log)
            else:
                importer = TrackJsonImporter(self._path, logger=self._log, verbose=self._verbose)

            self._log.write(u'<h1>Beginning Import...</h1>')
            importer.read(session, compressed=self._compressed)
        except Exception as err:
            if not self._session:
                session.rollback()
                session.close()

            self._log.writeError(u'ERROR: Track Importing Error', err)
            return 1

        if self._session is None:
            session.commit()
            session.close()

        return 0
