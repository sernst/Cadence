# TrackExporterRemoteThread.py
# (C)2014
# Scott Ernst

from pyaid.ArgsUtils import ArgsUtils

from pyglass.threading.RemoteExecutionThread import RemoteExecutionThread

from cadence.data.TrackExporter import TrackExporter
from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ TrackExporterRemoteThread
class TrackExporterRemoteThread(RemoteExecutionThread):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, path, session =None, **kwargs):
        """Creates a new instance of TrackImporterRemoteThread."""
        self._pretty = ArgsUtils.extract('pretty', False, kwargs)
        self._gzipped = ArgsUtils.extract('compressed', True, kwargs)
        self._difference = ArgsUtils.extract('difference', True, kwargs)

        RemoteExecutionThread.__init__(self, parent, **kwargs)

        self._path = path
        self._session = session

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _runImpl
    def _runImpl(self):
        model   = Tracks_Track.MASTER
        session = self._session if self._session else model.createSession()

        try:
            exporter = TrackExporter(logger=self._log)
            self._log.write(u'<h1>Beginning Export...</h1>')
            exporter.write(
                session=session,
                path=self._path,
                pretty=self._pretty,
                gzipped=self._gzipped,
                difference=self._difference)
        except Exception, err:
            if not self._session:
                session.rollback()
                session.close()

            self._log.writeError(u'ERROR: Track Export Failed', err)
            return 1

        if not self._session:
            session.commit()
            session.close()

        return 0
