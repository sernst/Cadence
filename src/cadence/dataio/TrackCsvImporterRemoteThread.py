# TrackCsvImporterRemoteThread.py
# (C)2013
# Scott Ernst

from pyglass.threading.RemoteExecutionThread import RemoteExecutionThread


from cadence.dataio.TrackCsvImporter import TrackCsvImporter

#___________________________________________________________________________________________________ TrackCsvImporterRemoteThread
class TrackCsvImporterRemoteThread(RemoteExecutionThread):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, path, force =True, **kwargs):
        """Creates a new instance of TrackCsvImporterRemoteThread."""
        RemoteExecutionThread.__init__(self, parent, **kwargs)
        self._path  = path
        self._force = force

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _internalMethod
    def _runImpl(self):
        try:
            importer = TrackCsvImporter(self._path, logger=self._log)
            importer.read(force=self._force)
        except Exception, err:
            self._log.writeError('Track CSV Parsing Error', err)
            return 1

        return 0


