import os

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeCreatePathAppSettings(os.path.abspath(os.curdir), '..', isDir=True)

from cadence.data.TrackLinkConnector import TrackLinkConnector
from cadence.models.tracks.Tracks_Track import Tracks_Track

linker = TrackLinkConnector()

session = Tracks_Track.MASTER.getSession()
linker.runAll(session)

print '--- RESULTS ---'
print linker.echoResult()

session.commit()
session.close()
