from pyaid.json.JSON import JSON

from cadence.enums.TrackPropEnum import TrackPropEnum
from cadence.enums.TrackPropEnum import TrackPropEnumOps

data = JSON.fromFile('/Users/scott/Desktop/test.json')
result = []

for entry in data:
    out = {
        TrackPropEnum.YEAR.name:u'2009',
        TrackPropEnum.SECTOR.name:u'1' }

    skipped = False
    for n,v in entry.iteritems():
        enum = TrackPropEnumOps.getTrackPropEnumByName(n)
        if not enum:
            continue

        if enum == TrackPropEnum.TRACKWAY_NUMBER:
            v = unicode(v).lstrip(u'0')
            if not v:
                skipped = True
                break
            out[n] = v
        elif enum.unique:
            out[n] = v
        elif enum in [TrackPropEnum.X, TrackPropEnum.Z, TrackPropEnum.ROTATION]:
            out[n] = v

    if not skipped:
        result.append(out)

JSON.toFile('/Users/scott/Desktop/BEB-Pre-Database-Snapshot.json', result)
