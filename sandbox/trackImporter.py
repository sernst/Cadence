# trackImporter.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
from cadence.data.TrackLinkConnector import TrackLinkConnector
from cadence.models.analysis.Analysis_Track import Analysis_Track
from cadence.models.tracks.Tracks_Track import Tracks_Track

####################################################################################################
# INITIALIZATION VARIABLES

model = Tracks_Track.MASTER
session = model.createSession()
analysisSession = Analysis_Track.createSession()

tracks = session.query(model).filter(model.site == 'SCR').filter(model.level == '1030').all()
linker = TrackLinkConnector()
linker.run(tracks, session)

model = Tracks_TrackStore.MASTER
trackStores = session.query(model).filter(model.site == 'SCR').filter(model.level == '1030').all()
linker = TrackLinkConnector()
linker.run(trackStores, session)

for track in tracks:
    print('[LINKED]: %s' % track.fingerprint)

session.commit()
session.close()

print('Track linking complete')
