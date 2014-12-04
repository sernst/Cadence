
from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.dict.DictUtils import DictUtils
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track
# from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
from cadence.enums.TrackPropEnum import TrackPropEnum

models = {'Track':Tracks_Track.MASTER} # , 'Track Store':Tracks_TrackStore.MASTER}
session = Tracks_Track.MASTER.createSession()

for label,model in models.iteritems():
    query = session.query(model).filter(
        getattr(model, TrackPropEnum.LEVEL.name) == '515').filter(
        getattr(model, TrackPropEnum.SITE.name) == 'BEB').filter(
        getattr(model, TrackPropEnum.YEAR.name) == '2009').filter(
        getattr(model, TrackPropEnum.SECTOR.name) == '1').filter(
        getattr(model, TrackPropEnum.PES.name) == False).filter(
        getattr(model, TrackPropEnum.LEFT.name) == False).filter(
        getattr(model, TrackPropEnum.TRACKWAY_NUMBER.name) == '21').filter(
        getattr(model, TrackPropEnum.TRACKWAY_TYPE.name) == 'S')
    items = query.all()
    print('\n\n\n%s' % (60*'-'))
    print('MODEL:', label)

    if not items:
        print('No matching items found')
    else:
        for item in items:
            print('Found: %s (Hidden: %s) (Complete: %s) %s\n  * next: %s' % (
                item.fingerprint,
                'Y' if item.hidden else 'N',
                'Y' if item.isComplete else 'N',
                '\n  * ' + DictUtils.prettyPrint(item.toDict(uniqueOnly=True), '\n  * '),
                item.next))
