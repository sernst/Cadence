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

INDEXES = None
UID_BEGINS = None # ['track1l2hy-_w-']
#UIDS = ['track1l2ho-3u-jQx6utGDjsrF'] # ['track1l2ho-1Z-TgaGkq43cFzW', 'track1l2if-1vL-xokpNmp5Hc4j'] # ['track3e_dn-1KC-XU4Y20XnBqUV']
CSV_FILE = None #'/Users/scott/Python/Cadence/resources/local/analysis/StatusAnalyzer/Ignored-Track-Report.csv'

UIDS = [
    'track1l2i9-11g-wzN5bRckuC5Z',
    'track1l2i9-11i-pe56ota6vskb',
    'track1l2i9-11k-BC3c3VXEHBfW',
    'track1l2i9-11m-PUWPXFEwGDdF',
    'track1l2i9-11o-zTs69ewQDfdS',
    'track1l2iC-17o-cBhCL8Oz2yBq',
    'track1l2iC-18H-uPk3ZLiyOaMt',
    'track1l2iE-1CZ-IltYztRFVeR6',
    'track1l2iN-1Sy-5WeMYoYEYrIx',
    'track1l2iZ-1lc-TFCkyKcj9UTY',
    'track1l2ho-s-SxcRqPuMypyS',
    'track1l2ho-1T-G1zCMeqQuTJe',
    'track1l2ho-21-Bw61CLuaCcnb',
    'track1l2ho-25-wJhE2et0Vfxf',
    'track1l2ho-2u-StS13cUrzzXE',
    'track1l2ho-2w-Ay9OmiOz6vog',
    'track1l2ho-3s-XruGmQTarF5O',
    'track1l2ho-3u-jQx6utGDjsrF',
    'track1l2hp-3~-1B8Scqjeth4G',
    'track1l2hp-41-6SIVKzFHIpZ6',
    'track1l2hp-49-PyAmfjim2mb6',
    'track1l2hp-4F-z51FhDmLikrK',
    'track1l2hp-4H-NdIiivZNu1ID',
    'track1l2hp-5N-JzzdqUmAzjbg',
    'track1l2hp-5P-RXse6HJGEV0l',
    'track1l2hq-8a-pPapGBvlE55R',
    'track1l2hq-9g-CHgcVI0IWFYP',
    'track1l2if-1vJ-scpJzkhuBXiR',
    'track1l2if-1vN-KobAEJPFUZGW',
    'track1l2ir-2BJ-NxaejeLuiOEy',
    'track1l2iu-2FT-LAWMuskdjnQs',
    'track1l2iw-2I5-MRnK0i0ZIVbu'
]

trackModel = Tracks_Track.MASTER
session = trackModel.createSession()

asmModel = Analysis_Track.MASTER
aSession = asmModel.createSession()

#_______________________________________________________________________________
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

if UIDS:
    ordered = []
    missing = []
    for uid_entry in UIDS:
        not_found = True
        for track in tracks:
            if track.uid == uid_entry:
                ordered.append(track)
                not_found = False
                break

        if not_found:
            missing.append(uid_entry)
    tracks = ordered

    if missing:
        print('MISSING UIDS:')
        for not_found_uid in missing:
            print('  * {}'.format(not_found_uid))
        print('\n\n')

#_______________________________________________________________________________
# TRACK ITERATOR
for track in tracks:
    print(track.echoForVerification())
    print('        size: (%s, %s) | field (%s, %s)' % (
        track.width, track.length, track.widthMeasured, track.lengthMeasured))
    print('        hidden: %s | custom: %s' % (
        'Y' if track.hidden else 'N',
        'Y' if track.custom else 'N'))
    aTrack = track.getAnalysisPair(aSession)
    print('        curve[%s]: %s (%s)' % (
        aTrack.curveSegment,
        NumericUtils.roundToSigFigs(aTrack.segmentPosition, 4),
        NumericUtils.roundToSigFigs(aTrack.curvePosition, 4)))
    print('        snapshot: %s' % DictUtils.prettyPrint(track.snapshotData))
    print('        imports: %s' % track.echoImportFlags())
    print('        analysis: %s\n' % track.echoAnalysisFlags())

session.close()
aSession.close()
