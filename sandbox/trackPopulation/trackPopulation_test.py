from pyaid.json.JSON import JSON

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks import Tracks_Track

# Load the json data for the tracks
items = JSON.fromFile('C:\\Users\\sernst\\Desktop\\test_with_all_tracks.json')

# For each item in the definition file, create a track entry in the database
for item in items:
    track = Tracks_Track.MASTER(trackData=item)
    track.saveData()

print 'Operation Complete!'
