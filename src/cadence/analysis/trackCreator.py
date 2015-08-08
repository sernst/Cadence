# trackCreator.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sys
import os

import pandas as pd
from pyaid.json.JSON import JSON

from pyaid.string.StringUtils import StringUtils

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track

#---------------------------------------------------------------------------------------------------
# INITIALIZATION
#       The following variables must be set for the script to work properly

CSV_SOURCE_PATH = '/Users/kent/Dropbox/A16/spreadsheets/BEB_S_500/Custom_Tracks.csv'

####################################################################################################

if not CSV_SOURCE_PATH or not os.path.exists(CSV_SOURCE_PATH):
    print('[FATAL]: Invalid source path specified. Operation aborted.')
    sys.exit(1)

try:
    data = pd.read_csv(CSV_SOURCE_PATH)
except Exception:
    print('[FATAL]: Invalid csv file. Operation aborted.')
    sys.exit(2)

model = Tracks_Track.MASTER
session = model.createSession()

try:
    for index, row in data.iterrows():
        # For each row in the source spreadsheet file, create a new track if no such track exists

        if row.site == 'FAKE':
            # Skip tracks marked with the site name FAKE as they represent file structure
            # formatting examples and not real tracks
            continue

        t = Tracks_Track()
        t.custom = True

        t.site = StringUtils.toText(row.site)
        t.sector = StringUtils.toText(row.sector)
        t.level = StringUtils.toText(row.level)
        t.trackwayNumber = StringUtils.toText(row.trackwayNumber)
        t.name = StringUtils.toText(row.trackwayName)

        t.trackwayType = 'S'
        t.year = '2014'
        t.index = -1

        existing = t.findExistingTracks(session=session)
        if existing:
            # Do not create a track if the fingerprint for the new track matches one already found
            # in the database
            print('[WARNING]: Track "%s" already exists. Skipping this entry.')
            continue
        session.add(t)

        # Populate the new tracks with "reasonable" starting values to make the tracks easier to
        # manipulate. The number "42" is used in repetition to make the starting values obviously
        # fake and require adjustment.
        t.snapshotData = dict()
        t.width = 0.424242
        t.widthUncertainty = 0.05
        t.length = 0.424242
        t.lengthUncertainty = 0.05
        t.rotation = 42.4242

except Exception:
    print('[FATAL]: Improperly formatted spreadsheet')
    session.close()
    raise

session.commit()
print('[COMPLETE]: New tracks have been saved to the database.')
