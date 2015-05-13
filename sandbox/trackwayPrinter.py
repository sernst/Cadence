
from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.number.NumericUtils import NumericUtils

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.analysis.Analysis_Sitemap import Analysis_Sitemap
from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.models.tracks.Tracks_Trackway import Tracks_Trackway

smModel   = Tracks_SiteMap.MASTER
twModel   = Tracks_Trackway.MASTER
session   = twModel.createSession()

asmModel = Analysis_Sitemap.MASTER
aSession = asmModel.createSession()

siteMaps = session.query(smModel).filter(smModel.name == 'CRO').filter(smModel.level == '500').all()

for siteMap in siteMaps:
    trackways = session.query(twModel) \
        .filter(twModel.siteMapIndex == siteMap.index).all()
        # .filter(twModel.name == 'BEB-515-2009-1-S-6').all()

    for trackway in trackways:
        print('\n\n\n%s\nTRACKWAY[%s]:' % (60*'=', trackway.name))

        trackwaySeries = trackway.getTrackSeries()
        for label, series in trackwaySeries.items():
            if not series.tracks:
                continue
            print('\n  %s\n  SERIES[%s]: %s' % (
                58*'-',
                label,
                'COMPLETE' if series.isComplete else 'INCOMPLETE'))

            for track in series.tracks:
                print('    * %s%s [%s] -> [%s] (%s, %s)' % (
                    '' if track.isComplete else '[INCOMPLETE] ',
                    track.fingerprint, track.uid, track.next, track.x, track.z))
                aTrack = track.getAnalysisPair(aSession)
                print('        curve[%s]: %s (%s)' % (
                    aTrack.curveSegment,
                    NumericUtils.roundToSigFigs(aTrack.segmentPosition, 4),
                    NumericUtils.roundToSigFigs(aTrack.curvePosition, 4)))

session.close()
aSession.close()


