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

INDEXES = [307, 313]
UID_BEGINS = None # ['track1l2hy-_w-']
UIDS = None # ['track3e_dn-1KC-XU4Y20XnBqUV']
CSV_FILE = None #'/Users/scott/Python/Cadence/resources/local/analysis/StatusAnalyzer/Ignored-Track-Report.csv'

trackModel = Tracks_Track.MASTER
session = trackModel.createSession()

asmModel = Analysis_Track.MASTER
aSession = asmModel.createSession()

#___________________________________________________________________________________________________
# TRACK QUERY
query = session.query(trackModel)
if INDEXES:
    query = query.filter(trackModel.i.in_(INDEXES))

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
    print('        size: (%s, %s) | field (%s, %s)' % (
        track.width, track.length, track.widthMeasured, track.lengthMeasured))
    aTrack = track.getAnalysisPair(aSession)
    print('        curve[%s]: %s (%s)' % (
        aTrack.curveSegment,
        NumericUtils.roundToSigFigs(aTrack.segmentPosition, 4),
        NumericUtils.roundToSigFigs(aTrack.curvePosition, 4)))
    print('        snapshot: %s' % DictUtils.prettyPrint(track.snapshotData))
    print('        imports: %s\n' % track.echoImportFlags())

session.close()
aSession.close()
