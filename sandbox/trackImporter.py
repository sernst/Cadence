# trackImporter.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
from cadence.data.TrackCsvImporter import TrackCsvImporter
from cadence.data.TrackLinkConnector import TrackLinkConnector
from cadence.models.analysis.Analysis_Track import Analysis_Track
from cadence.models.tracks.Tracks_Track import Tracks_Track

####################################################################################################
# INITIALIZATION VARIABLES

PATH = '/Users/scott/Dropbox/A16/spreadsheets/BEB_S_500/BEB_500.csv'

#---------------------------------------------------------------------------------------------------
# IMPORT TRACKS
#       Imports the tracks from the spreadsheet into the database

session = Tracks_Track.MASTER.createSession()
analysisSession = Analysis_Track.createSession()

importer = TrackCsvImporter(path=PATH)
print('IMPORTING: %s' % PATH)
importer.read(session=session, analysisSession=analysisSession)

trackUids = []
for track in importer.created + importer.modified:
    trackUids.append(track.uid)

session.commit()
session.close()
print('Track importing complete')

#---------------------------------------------------------------------------------------------------
# LINK IMPORTED TRACKS
#       Creates track links in both the tracks and trackStore tables

print('LINKING: %s tracks' % len(trackUids))
for model in [Tracks_Track.MASTER, Tracks_TrackStore.MASTER]:
    session = model.createSession()
    tracks = session.query(model).filter(model.uid.in_(trackUids))
    linker = TrackLinkConnector()
    linker.run(tracks, session)

    session.commit()
    session.close()

print('Track linking complete')
