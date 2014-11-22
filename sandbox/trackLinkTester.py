from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.data.TrackLinkConnector import TrackLinkConnector
from cadence.models.tracks.Tracks_Track import Tracks_Track

linker = TrackLinkConnector()

session = Tracks_Track.MASTER.getSession()
linker.runAll(session)

print '--- RESULTS ---'
print linker.echoResult()

session.commit()
session.close()
