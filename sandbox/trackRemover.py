# trackRemover.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os

import pandas as pd
from pyaid.string.StringUtils import StringUtils

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
from cadence.models.analysis.Analysis_Track import Analysis_Track

#---------------------------------------------------------------------------------------------------
# SOURCE FILE
#       Specify the path to a csv file containing a 'UID' column. Each entry in that column
#       represents a track that will be deleted from the database using this script.
CSV_FILE = '/Users/scott/Python/Cadence/resources/local/analysis/StatusAnalyzer/Corrupt-Track-Report.csv'

if not CSV_FILE or not os.path.exists(CSV_FILE):
    sys.exit(1)

tracksModel = Tracks_Track.MASTER
storeModel = Tracks_TrackStore.MASTER
tracksSession = tracksModel.createSession()

analysisModel = Analysis_Track.MASTER
analysisSession = analysisModel.createSession()

data = pd.read_csv(CSV_FILE)

def removeTrack(track):
    analysisTrack = track.getAnalysisPair(analysisSession)
    if analysisTrack:
        analysisSession.delete(analysisTrack)

    for store in tracksSession.query(storeModel).filter(storeModel.uid == track.uid).all():
        tracksSession.delete(store)

    tracksSession.delete(track)

for index, row in data.iterrows():
    uid = StringUtils.toText(row.UID)
    tracks = Tracks_Track.removeTracksByUid(uid, tracksSession, analysisSession)
    for track in tracks:
        print('[REMOVED]: %s (%s)' % (track.fingerprint, track.uid))

tracksSession.commit()
analysisSession.commit()

print('Removal Operation Complete')



