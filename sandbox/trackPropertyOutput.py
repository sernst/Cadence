
from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.dict.DictUtils import DictUtils

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track

model   = Tracks_Track.MASTER
session = model.createSession()

result  = session.query(model).filter(model.uid == 'track1l2i9-11o-zTs69ewQDfdS').all()

for track in result:
    print('FINGERPRINT:', track.fingerprint)
    print('PREVIOUS:', track.getPreviousTrack())
    print(DictUtils.prettyPrint(track.toDict()))
