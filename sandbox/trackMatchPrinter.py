
from __future__ import print_function, absolute_import, unicode_literals, division

import sqlalchemy as sqla
from pyaid.dict.DictUtils import DictUtils
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.models.tracks.Tracks_Track import Tracks_Track

models = {'Track':Tracks_Track.MASTER}
session = Tracks_Track.MASTER.createSession()
verbose = True

for label,model in models.iteritems():
    query = session.query(model).filter(model.uid.in_((
        'track1l2ic-1s7-rZ3g4I0Yzvzd',
        'track1l2id-1sZ-UvtVfQoOAOPo')) )
    items = query.all()
    print('\n\n\n%s' % (60*'-'))
    print('MODEL:', label)
    print('COUNT:', len(items))

    if not items:
        print('No matching items found')
    else:
        for item in items:
            if verbose:
                print('[TRACK]: %s [%s]:\n  * hidden: %s\n  * complete: %s\n  * next: %s\n%s' % (
                    item.fingerprint, item.uid,
                    'Y' if item.hidden else 'N', 'Y' if item.isComplete else 'N', item.next,
                    '\n  * ' + DictUtils.prettyPrint(item.toDict(uniqueOnly=True), '\n  * ')))
                print('  * Length Uncertainty: %s' % item.rotationUncertainty)
            else:
                print('%s[H:%s|C:%s] "%s" -> "%s"' % (
                    item.fingerprint,
                    'Y' if item.hidden else 'N',
                    'Y' if item.isComplete else 'N',
                    item.uid, item.next))
