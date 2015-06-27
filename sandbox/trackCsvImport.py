# trackCsvImport
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.data.TrackCsvImporter import TrackCsvImporter
from cadence.models.analysis.Analysis_Track import Analysis_Track
from cadence.models.tracks.Tracks_Track import Tracks_Track

PATH = '/Users/scott/Dropbox/a16/spreadsheets/BEB_S_500/BEB_500.csv'

session = Tracks_Track.createSession()
aSession = Analysis_Track.createSession()

importer = TrackCsvImporter(path=PATH)
importer.read(session, aSession)

for t in importer.created:
    print('[CREATED]: %s (%s)' % (t.fingerprint, t.uid))

print('%s Tracks Created' % len(importer.created))
print('%s Tracks Modified' % len(importer.modified))

session.commit()
aSession.commit()
