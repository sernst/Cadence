from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.dict.DictUtils import DictUtils
from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

import sqlalchemy as sqla
import pandas as pd

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.analysis.Analysis_Track import Analysis_Track

UID_BEGINS = [] # ['track1l2hy-_w-']
UIDS = None #['track1l2iC-17g-9gTsoGaV1jCg']
CSV_FILE = '/Users/scott/Python/Cadence/resources/local/analysis/StatusAnalyzer/Ignored-Track-Report.csv'

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

if UIDS is None:
    UIDS = []

if CSV_FILE:
    # Loads all of the CSV files
    df = pd.read_csv(CSV_FILE)
    UIDS.extend([StringUtils.toText(item) for item in list(df.UID)])

if UIDS:
    query = query.filter(trackModel.uid.in_(UIDS))

tracks = query.all()

#___________________________________________________________________________________________________
# TRACK ITERATOR
for track in tracks:
    print(track.echoForVerification())
    print('        size: (%s, %s)' % (track.width, track.length))
    aTrack = track.getAnalysisPair(aSession)
    print('        curve[%s]: %s (%s)' % (
        aTrack.curveSegment,
        NumericUtils.roundToSigFigs(aTrack.segmentPosition, 4),
        NumericUtils.roundToSigFigs(aTrack.curvePosition, 4)))
    print('        snapshot: %s\n' % DictUtils.prettyPrint(track.snapshotData))

session.close()
aSession.close()
