# TrackLinkageRemoteThread.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.threading.RemoteExecutionThread import RemoteExecutionThread

from cadence.data.TrackLinkConnector import TrackLinkConnector
from cadence.models.tracks.Tracks_Track import Tracks_Track

#_______________________________________________________________________________
class TrackLinkageRemoteThread(RemoteExecutionThread):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, parent, session =None, tracks =None, **kwargs):
        """Creates a new instance of TrackLinkageRemoteThread."""
        RemoteExecutionThread.__init__(self, parent, **kwargs)
        self._session = session
        self._tracks  = tracks

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _runImpl(self):
        model   = Tracks_Track.MASTER
        session = self._session if self._session else model.createSession()

        try:
            tlc = TrackLinkConnector(logger=self._log)
            self._log.write(u'<h1>Beginning Linkage Reset...</h1>')

            if self._tracks is not None:
                tlc.run(self._tracks, session)
            else:
                tlc.runAll(session)
        except Exception as err:
            if not self._session:
                session.close()

            self._log.writeError(u'Track linkage update failed', err)
            return 1

        if not self._session:
            session.commit()
            session.close()

        return 0
