# trackImporter.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.data.TrackCsvImporter import TrackCsvImporter
from cadence.data.TrackLinkConnector import TrackLinkConnector
from cadence.models.tracks.Tracks_Track import Tracks_Track

PATH = '/Users/scott/Dropbox/A16/spreadsheets/BEB_S_500/BEB_500.csv'

session = Tracks_Track.MASTER.createSession()

importer = TrackCsvImporter(path=PATH)
print('IMPORTING: %s' % PATH)
importer.read(session=session)

session.commit()
session.close()
print('Track importing complete')

#---------------------------------------------------------------------------------------------------

model = Tracks_Track.MASTER
session = model.createSession()

tracks = session.query(model).filter(model.site == 'BEB').filter(model.level == '500').all()
print('LINKING: %s tracks' % len(tracks))

for track in tracks:
    print(track.fingerprint)

linker = TrackLinkConnector()
linker.run(tracks, session)

session.commit()
session.close()
print('Track linking complete')
