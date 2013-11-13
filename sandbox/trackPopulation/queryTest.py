from pyaid.file.FileUtils import FileUtils
from pyaid.json.JSON import JSON

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

# Set the path targets for database access outside of a PyGlass application
myDir = FileUtils.getDirectoryOf(__file__)
PyGlassEnvironment.initializeExplicitAppSettings(
    FileUtils.createPath(myDir, '..', '..', 'resources', isDir=True),
    FileUtils.createPath(myDir, '..', '..', 'resources', 'local', isDir=True) )

from cadence.models.tracks.Tracks_Track import Tracks_Track

model   = Tracks_Track.MASTER
session = model.createSession()
for value in session.query(model.trackway).distinct():
    print value

session.close()

print 'Operation Complete'
