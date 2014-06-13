from pyaid.dict.DictUtils import DictUtils
from pyaid.file.FileUtils import FileUtils
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

location = FileUtils.getDirectoryOf(__file__)

PyGlassEnvironment.initializeExplicitAppSettings(
    FileUtils.createPath(location, '..', 'resources', isDir=True),
    FileUtils.createPath(location, '..', 'resources', 'local', isDir=True) )

from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.enum.TrackPropEnum import TrackPropEnum

model = Tracks_Track.MASTER
session = model.createSession()
query = session.query(model).filter(
    getattr(model, TrackPropEnum.SITE.name) == u'BEB').filter(
    getattr(model, TrackPropEnum.YEAR.name) == u'2010')

items = query.all()
if not items:
    print u'No matching items found'
else:
    for item in items:
        print u'Found:', \
            item.uid, \
            u'\n  * ' + DictUtils.prettyPrint(item.toDict(uniqueOnly=True), u'\n  * ')
