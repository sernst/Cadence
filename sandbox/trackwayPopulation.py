# trackwayPopulation.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sqlalchemy as sqla
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Trackway import Tracks_Trackway
from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap

#---------------------------------------------------------------------------------------------------
# SITEMAP TABLE UPDATE
#       All sitemaps must have their name and level fields set for the trackway population script
#       to work. Since the name and level fields were not part of the original sitemap table
#       structure this section populates any values that haven't been updated to include these
#       values since the migration to the new table structure.

model = Tracks_SiteMap.MASTER
session = model.createSession()

for sm in session.query(model).filter(sqla.or_(model.name == '', model.level == '')).all():
    sm.name = Tracks_SiteMap.getNameFromFilename(sm.filename)
    sm.level = Tracks_SiteMap.getLevelFromFilename(sm.filename)

session.commit()
session.close()

#---------------------------------------------------------------------------------------------------
# TRACKWAY POPULATION
#       All existing trackway entries are removed from the table and new ones created for any
#       trackway found by searching for distinct track series using Tracks_Track.next field to
#       iterate over track series

Tracks_Trackway.populateTrackwaysTable()
model = Tracks_Trackway.MASTER
session = model.createSession()

for trackway in session.query(model).all():
    print('[CREATED]:', trackway)


