# trackwayPopulation.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Trackway import Tracks_Trackway

# THIS SECTION WAS NEEDED THE FIRST TIME TO POPULATE THE UPGRADED SITEMAPS TABLE
# from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap

# model = Tracks_SiteMap.MASTER
# session = model.createSession()

# for sm in session.query(model).all():
#     sm.name = Tracks_SiteMap.getNameFromFilename(sm.filename)
#     sm.level = Tracks_SiteMap.getLevelFromFilename(sm.filename)

# session.commit()
# session.close()

Tracks_Trackway.populateTrackwaysTable()
model = Tracks_Trackway.MASTER
session = model.createSession()

for trackway in session.query(model).all():
    print(trackway)


