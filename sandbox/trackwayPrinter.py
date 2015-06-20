
from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.dict.DictUtils import DictUtils
from pyaid.number.NumericUtils import NumericUtils

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.analysis.Analysis_Sitemap import Analysis_Sitemap
from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.models.tracks.Tracks_Trackway import Tracks_Trackway

SITEMAP_NAME = 'BEB'
SITEMAP_LEVEL = '500'
TRACKWAY_NAME = '' #'BSY-1040-2008-20-S-19' #'CRO-500-2004-1-S-3'

smModel   = Tracks_SiteMap.MASTER
twModel   = Tracks_Trackway.MASTER
session   = twModel.createSession()

asmModel = Analysis_Sitemap.MASTER
aSession = asmModel.createSession()

#___________________________________________________________________________________________________
# SITEMAP QUERY
query = session.query(smModel)
if SITEMAP_NAME:
    query = query.filter(smModel.name == SITEMAP_NAME)
if SITEMAP_LEVEL:
    query = query.filter(smModel.level == SITEMAP_LEVEL)
siteMaps = query.all()

#___________________________________________________________________________________________________
# TRACK ITERATOR
for siteMap in siteMaps:
    query = session.query(twModel).filter(twModel.siteMapIndex == siteMap.index)
    if TRACKWAY_NAME:
        query = query.filter(twModel.name == TRACKWAY_NAME)
    trackways = query.all()

    for trackway in trackways:
        print('\n\n\n%s\nTRACKWAY[%s]:' % (60*'=', trackway.name))

        trackwaySeries = trackway.getTrackwaySeriesBundle()
        for label, series in trackwaySeries.items():
            if not series.tracks:
                continue
            print('\n  %s\n  SERIES[%s]: %s' % (
                58*'-',
                label,
                'COMPLETE' if series.isComplete else 'INCOMPLETE'))

            for track in series.tracks:
                print(track.echoForVerification())
                print('        size: (%s, %s)' % (track.width, track.length))

                aTrack = track.getAnalysisPair(aSession)
                print('        curve[%s]: %s (%s)' % (
                    aTrack.curveSegment,
                    NumericUtils.roundToSigFigs(aTrack.segmentPosition, 4),
                    NumericUtils.roundToSigFigs(aTrack.curvePosition, 4)))
                print('        snapshot: %s\n' % DictUtils.prettyPrint(track.snapshotData))

#___________________________________________________________________________________________________
# CLEANUP
session.close()
aSession.close()


