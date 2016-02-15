from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyaid.dict.DictUtils import DictUtils
from pyaid.number.NumericUtils import NumericUtils
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.analysis.Analysis_Sitemap import Analysis_Sitemap
from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.models.tracks.Tracks_Trackway import Tracks_Trackway
from cadence.analysis.shared.CsvWriter import CsvWriter

SITEMAP_NAME = None # 'BEB'
SITEMAP_LEVEL = None # '500'
TRACKWAY_NAME = 'BEB-500-2014-1-S-10' #'BSY-1040-2008-20-S-19' #'CRO-500-2004-1-S-3'
WRITE_TO_FILE = True

smModel   = Tracks_SiteMap.MASTER
twModel   = Tracks_Trackway.MASTER
session   = twModel.createSession()

asmModel = Analysis_Sitemap.MASTER
aSession = asmModel.createSession()

#_______________________________________________________________________________
# SITEMAP QUERY
query = session.query(smModel)
if SITEMAP_NAME:
    query = query.filter(smModel.name == SITEMAP_NAME)
if SITEMAP_LEVEL:
    query = query.filter(smModel.level == SITEMAP_LEVEL)
siteMaps = query.all()

#_______________________________________________________________________________
# TRACK ITERATOR
for siteMap in siteMaps:
    query = session.query(twModel).filter(twModel.siteMapIndex == siteMap.index)
    if TRACKWAY_NAME:
        query = query.filter(twModel.name == TRACKWAY_NAME)
    trackways = query.all()

    for trackway in trackways:
        tw_data = dict(lp=[], rp=[], lm=[], rm=[])

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
                data = tw_data.get('{}{}'.format(
                    'l' if track.left else 'r',
                    'p' if track.pes else 'm' ))
                data.append(track.positionValue)

                print(track.echoForVerification())
                print('        size: (%s, %s) | field (%s, %s)' % (
                    track.width, track.length,
                    track.widthMeasured, track.lengthMeasured))

                aTrack = track.getAnalysisPair(aSession)
                print('        curve[%s]: %s (%s)' % (
                    aTrack.curveSegment,
                    NumericUtils.roundToSigFigs(aTrack.segmentPosition, 4),
                    NumericUtils.roundToSigFigs(aTrack.curvePosition, 4)))
                print('        snapshot: {}\n'.format(
                        DictUtils.prettyPrint(track.snapshotData)) )

            if not WRITE_TO_FILE:
                continue

            csv = CsvWriter(
                path='{}.csv'.format(trackway.name),
                fields=[
                    'lpx', 'lpxunc', 'lpy', 'lpyunc',
                    'rpx', 'rpxunc', 'rpy', 'rpyunc',
                    'lmx', 'lmxunc', 'lmy', 'lmyunc',
                    'rmx', 'rmxunc', 'rmy', 'rmyunc' ])

            lp = tw_data['lp']
            rp = tw_data['rp']
            lm = tw_data['lm']
            rm = tw_data['rm']

            for i in range(max(*[len(x) for x in tw_data.values()])):
                csv.createRow(
                    lpx=lp[i].x if len(lp) > i else '',
                    lpxunc=lp[i].xUnc if len(lp) > i else '',
                    lpy=lp[i].y if len(lp) > i else '',
                    lpyunc=lp[i].yUnc if len(lp) > i else '',

                    rpx=rp[i].x if len(rp) > i else '',
                    rpxunc=rp[i].xUnc if len(rp) > i else '',
                    rpy=rp[i].y if len(rp) > i else '',
                    rpyunc=rp[i].yUnc if len(rp) > i else '',

                    lmx=lm[i].x if len(lm) > i else '',
                    lmxunc=lm[i].xUnc if len(lm) > i else '',
                    lmy=lm[i].y if len(lm) > i else '',
                    lmyunc=lm[i].yUnc if len(lm) > i else '',

                    rmx=rm[i].x if len(rm) > i else '',
                    rmxunc=rm[i].xUnc if len(rm) > i else '',
                    rmy=rm[i].y if len(rm) > i else '',
                    rmyunc=rm[i].yUnc if len(rm) > i else '')

            csv.save()

#_______________________________________________________________________________
# CLEANUP
session.close()
aSession.close()


