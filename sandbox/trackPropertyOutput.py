
from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.dict.DictUtils import DictUtils

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track

model   = Tracks_Track.MASTER
session = model.createSession()

# result  = session.query(model).filter(model.next == 'track1l2i9-11m-PUWPXFEwGDdF').all()
result  = session.query(model).filter(model.i == 'track1l2hr-Ek-Kf3UpiZYHm2L').all()

for track in result:
    print(DictUtils.prettyPrint(track.toDict()))
