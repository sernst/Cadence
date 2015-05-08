
from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.models.tracks.Tracks_Trackway import Tracks_Trackway

smModel   = Tracks_SiteMap.MASTER
twModel   = Tracks_Trackway.MASTER
session   = twModel.createSession()

siteMaps = session.query(smModel).filter(smModel.name == 'BEB').filter(smModel.level == '515').all()

for siteMap in siteMaps:
    trackways = session.query(twModel).filter(twModel.siteMapIndex == siteMap.index).all()

    for trackway in trackways:
        print('\n\n\n%s\nTRACKWAY[%s]:' % (60*'=', trackway.name))

        trackwaySeries = trackway.getTrackSeries()
        for label, series in trackwaySeries.items():
            if not series.tracks:
                continue
            print('\n  %s\n  SERIES[%s]:' % (58*'-', label))
            for track in series.tracks:
                print('    * Track: %s [%s] -> [%s] (%s, %s)' % (
                    track.fingerprint, track.uid, track.next, track.x, track.z))



