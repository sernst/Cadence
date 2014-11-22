from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track

model   = Tracks_Track.MASTER
session = model.getSession()
for value in session.query(model.trackway).distinct():
    print value

session.close()

print 'Operation Complete'
