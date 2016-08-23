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
TRACKWAY_NAME = 'BEB-500-2014-1-S-1'
# TRACKWAY_NAME = 'CRO-500-2004-1-S-3'
# TRACKWAY_NAME = 'BEB-500-2014-1-S-4'
# TRACKWAY_NAME = 'BSY-1040-2008-20-S-19'
WRITE_TO_FILE = True

smModel = Tracks_SiteMap.MASTER
twModel = Tracks_Trackway.MASTER
asmModel = Analysis_Sitemap.MASTER


def get_sitemap_query(session):
    """

    @param session:
    @return:
    """

    query = session.query(smModel)
    if SITEMAP_NAME:
        query = query.filter(smModel.name == SITEMAP_NAME)
    if SITEMAP_LEVEL:
        query = query.filter(smModel.level == SITEMAP_LEVEL)
    return query.all()


def get_trackway_query(site_map, session):
    """

    @param site_map:
    @param session:
    @return:
    """

    query = session.query(twModel).filter(
        twModel.siteMapIndex == site_map.index
    )

    if TRACKWAY_NAME:
        query = query.filter(twModel.name == TRACKWAY_NAME)
    return query.all()


def write_to_file(trackway, tracks_data):
    """
    @param trackway:
    @param tracks_data:
    @return:
    """

    csv = CsvWriter(
        path='{}.csv'.format(trackway.name),
        autoIndexFieldName='Index',
        fields=[
            'lp_name', 'lp_uid',
            'lp_x', 'lp_dx', 'lp_y', 'lp_dy',
            'lp_w', 'lp_dw', 'lp_l', 'lp_dl',
            'rp_name', 'rp_uid',
            'rp_x', 'rp_dx', 'rp_y', 'rp_dy',
            'rp_w', 'rp_dw', 'rp_l', 'rp_dl',
            'lm_name', 'lm_uid',
            'lm_x', 'lm_dx', 'lm_y', 'lm_dy',
            'lm_w', 'lm_dw', 'lm_l', 'lm_dl',
            'rm_name', 'rm_uid',
            'rm_x', 'rm_dx', 'rm_y', 'rm_dy',
            'rm_w', 'rm_dw', 'rm_l', 'rm_dl',
        ]
    )

    count = max([len(ts) if ts else 0 for ts in tracks_data.values()])

    for i in range(count):
        entry = {}

        for key in ['lp', 'rp', 'lm', 'rm']:
            data = tracks_data[key][i] if i < len(tracks_data[key]) else None
            track = data['track'] if data else None

            entry.update({
                '{}_name'.format(key): track.fingerprint if track else '',
                '{}_uid'.format(key): track.uid if track else ''
            })

            point = track.positionValue if track else None
            entry.update({
                '{}_x'.format(key): point.x if point else '',
                '{}_dx'.format(key): point.xUnc if point else '',
                '{}_y'.format(key): point.y if point else '',
                '{}_dy'.format(key): point.yUnc if point else '',
            })

            length = track.widthValue if track else None
            entry.update({
                '{}_l'.format(key): length.value if length else '',
                '{}_dl'.format(key): length.uncertainty if length else ''
            })

            width = track.widthValue if track else None
            entry.update({
                '{}_w'.format(key): width.value if width else '',
                '{}_dw'.format(key): width.uncertainty if width else ''
            })

        csv.createRow(**entry)

    csv.save()


def print_track(track, aSession):
    """

    @param track:
    @param aSession:
    @return:
    """

    limb_id = '{}{}'.format(
        'l' if track.left else 'r',
        'p' if track.pes else 'm'
    )

    print(track.echoForVerification())
    print('        size: (%s, %s) | field (%s, %s)' % (
        track.width, track.length,
        track.widthMeasured, track.lengthMeasured
    ))

    aTrack = track.getAnalysisPair(aSession)
    print('        curve[#%s -> %s]: %s (%s)' % (
        aTrack.curveIndex,
        aTrack.curveSegment,
        NumericUtils.roundToSigFigs(aTrack.segmentPosition, 4),
        NumericUtils.roundToSigFigs(aTrack.curvePosition, 4)
    ))
    print('        snapshot: {}\n'.format(
        DictUtils.prettyPrint(track.snapshotData))
    )

    return dict(
        limb_id=limb_id,
        track=track,
        aTrack=aTrack
    )


def do_printing(session, aSession):
    """

    @param session:
    @param aSession:
    @return:
    """

    for siteMap in get_sitemap_query(session):
        for trackway in get_trackway_query(siteMap, session):
            tracks_data = dict(lp=[], rp=[], lm=[], rm=[])

            print('\n\n\n%s\nTRACKWAY[%s]:' % (60*'=', trackway.name))

            trackwaySeries = trackway.getTrackwaySeriesBundle()
            for label, series in trackwaySeries.items():
                if not series.tracks:
                    continue
                print('\n  %s\n  SERIES[%s]: %s' % (
                    58*'-',
                    label,
                    'COMPLETE' if series.isComplete else 'INCOMPLETE'
                ))

                for track in series.tracks:
                    data = print_track(track, aSession)
                    tracks_data[data['limb_id']].append(data)

            if WRITE_TO_FILE:
                write_to_file(trackway, tracks_data)


def run():
    """

    @return:
    """

    session = twModel.createSession()
    aSession = asmModel.createSession()

    do_printing(
        session=session,
        aSession=aSession
    )

    session.close()
    aSession.close()


if __name__ == '__main__':
    run()

