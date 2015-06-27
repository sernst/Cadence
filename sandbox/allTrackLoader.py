from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.analysis.Analysis_Track import Analysis_Track

trackModel = Tracks_Track.MASTER
session = trackModel.createSession()

asmModel = Analysis_Track.MASTER
aSession = asmModel.createSession()

for track in session.query(trackModel).all():
    written = False
    if track.width is None:
        track.width = 0.0
        written = True
    if track.length is None:
        track.length = 0.0
        written = True
    if track.lengthMeasured is None:
        track.lengthMeasured = 0.0
        written = True
    if track.widthMeasured is None:
        track.widthMeasured = 0.0
        written = True
    if track.rotation is None:
        track.rotation = 0.0
        written = True
    if track.rotationMeasured is None:
        track.rotationMeasured = 0.0
        written = True

    if written:
        print('[EDITED]: %s (%s)' % (track.fingerprint, track.uid))

session.commit()




