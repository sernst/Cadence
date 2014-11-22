from pyaid.dict.DictUtils import DictUtils
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
from cadence.enums.TrackPropEnum import TrackPropEnum

models = {'Track':Tracks_Track.MASTER, 'Track Store':Tracks_TrackStore.MASTER}
session = Tracks_Track.MASTER.createSession()

for label,model in models.iteritems():
    query = session.query(model).filter(getattr(model, TrackPropEnum.LEVEL.name) == u'555')
    items = query.all()
    print 60*u'-'
    print u'MODEL:', label

    if not items:
        print u'No matching items found'
    else:
        for item in items:
            print u'Found:', \
                item.uid, \
                u'\n  * ' + DictUtils.prettyPrint(item.toDict(uniqueOnly=True), u'\n  * ')
