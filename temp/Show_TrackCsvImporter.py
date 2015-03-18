from __future__ import print_function, absolute_import, unicode_literals, division

import re
import csv

from cadence.models.tracks import Track

def read(session, path):
    with open(path, 'rU') as f:
        for row in csv.reader(f, delimiter=',', quotechar='"'):
            entry = dict()

            for column in Reflection.getReflectionList(TrackCsvColumnEnum):
                entry[column.name] = row[column.index]
            fromSpreadsheetEntry(entry, session)

def fromSpreadsheetEntry(row, session):

    track = Track()

    track.site = row.get(TrackCsvColumnEnum.TRACKSITE.name).strip().upper()

    pattern = re.compile('(?P<type>[^0-9\s\t]+)[\s\t]*(?P<number>[^\(\s\t]+)')
    test = row.get(TrackCsvColumnEnum.TRACKWAY.name).strip().upper()
    result = pattern.search(test).groupdict()
    track.trackwayType = result['type'].upper().strip()
    track.trackwayNumber = result['number'].upper().strip()

    track.fieldWidth = 0.01*float(collapseManusPesProperty(
        track, row,
        TCCE.PES_WIDTH, TCCE.PES_WIDTH_GUESS,
        TCCE.MANUS_WIDTH, TCCE.MANUS_WIDTH_GUESS,
        '0', IFE.HIGH_WIDTH_UNCERTAINTY, IFE.NO_WIDTH ))

    session.add(track)
    return track
