from __future__ import print_function, absolute_import, unicode_literals, division

import sqlalchemy as sqla

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.analysis.Analysis_Track import Analysis_Track

UID_BEGINS = ['track1l2hy-_w-']
UIDS = []

trackModel = Tracks_Track.MASTER
session = trackModel.createSession()

asmModel = Analysis_Track.MASTER
aSession = asmModel.createSession()

#___________________________________________________________________________________________________
# TRACK QUERY
query = session.query(trackModel)
if UID_BEGINS:
    # OR together the UID_BEGINS using the startswith query modifier for each entry
    query = query.filter(sqla.or_(*[trackModel.uid.startswith(start) for start in UID_BEGINS]))

if UIDS:
    query = query.filter(trackModel.uid.in_(UIDS))
tracks = query.all()

#___________________________________________________________________________________________________
# TRACK ITERATOR
for track in tracks:
    print(track.echoForVerification())
    at = track.getAnalysisPair(aSession)

session.close()
aSession.close()
