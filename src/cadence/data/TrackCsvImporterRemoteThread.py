# TrackCsvImporterRemoteThread.py
# (C)2013
# Scott Ernst

from pyglass.threading.RemoteExecutionThread import RemoteExecutionThread

from cadence.data.TrackCsvImporter import TrackCsvImporter

#___________________________________________________________________________________________________ TrackCsvImporterRemoteThread
class TrackCsvImporterRemoteThread(RemoteExecutionThread):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, path, **kwargs):
        """Creates a new instance of TrackCsvImporterRemoteThread."""
        RemoteExecutionThread.__init__(self, parent, **kwargs)
        self._path = path


#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _internalMethod
    def _runImpl(self):
        try:
            importer = TrackCsvImporter(self._path)
            importer.read()
        except Exception, err:
            self._log.writeError('Track CSV Parsing Error', err)
            return 1

        return 0


