from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.OsUtils import OsUtils
from pyaid.dict.DictUtils import DictUtils
from pyaid.file.FileUtils import FileUtils

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
from cadence.svg.CadenceDrawing import CadenceDrawing

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap

#---------------------------------------------------------------------------------------------------
model = Tracks_SiteMap.MASTER
session = model.createSession()

sitemap = session.query(model).filter(model.name == 'BEB').filter(model.level == '515').first()
print('SITEMAP[%s]: %s' % (sitemap.index, sitemap.name))

output = FileUtils.makeFilePath(OsUtils.getHomePath(), 'Desktop', '%s.svg' % sitemap.name)
drawing = CadenceDrawing(output, sitemap)

trackways = sitemap.getTrackways()
print('TRACKWAY COUNT: %s' % len(trackways))

for trackway in trackways:
    #if trackway.name != 'BEB-515-2009-1-S-21':
    #    continue
    print('TRACKWAY[%s]: %s' % (trackway.index, trackway.name))

    for key, series in DictUtils.iter(trackway.getTrackSeries()):
        for track in series.tracks:
            print('  * %s' % track.fingerprint)
            drawing.circle(
                track.positionValue.toMayaTuple(), 5,
                stroke='none', fill='#003300', fill_opacity='0.1')

drawing.save()
