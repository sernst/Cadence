from pyaid.file.FileUtils import FileUtils
from pyaid.json.JSON import JSON

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

# Set the path targets for database access outside of a PyGlass application
myDir = FileUtils.getDirectoryOf(__file__)
PyGlassEnvironment.initializeExplicitAppSettings(
    FileUtils.createPath(myDir, '..', '..', 'resources', isDir=True),
    FileUtils.createPath(myDir, '..', '..', 'resources', 'local', isDir=True) )

from cadence.mayan.trackway.Track import Track

# Load the json data for the tracks
items = JSON.fromFile('C:\\Users\\sernst\\Desktop\\test_with_all_tracks.json')

# For each item in the definition file, create a track entry in the database
for item in items:
    track = Track(trackData=item)
    track.saveData()

print 'Operation Complete!'
