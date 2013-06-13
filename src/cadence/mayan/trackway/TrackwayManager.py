# TrackwayManager.py
# (C)2012-2013 http://cadence.ThreeAddOne.com
# Scott Ernst

from nimble import cmds

#___________________________________________________________________________________________________ TrackwayManager
class TrackwayManager(object):

    _PREVIOUS_PRINT_ATTR = 'previousPrint'

#___________________________________________________________________________________________________ addToSeries
    @classmethod
    def addToSeries(cls):
        tracks = cls.getTargets(2)
        if not tracks or len(tracks) < 2:
            return False

        prevTrack = tracks[0]
        for track in tracks[1:]:
            if not cmds.attributeQuery(cls._PREVIOUS_PRINT_ATTR, node=track, exists=True):
                cmds.addAttr(longName=cls._PREVIOUS_PRINT_ATTR, attributeType='message')

            prevTracks = cls.getPreviousTracks(track)
            if not prevTracks or prevTrack not in prevTracks:
                cmds.connectAttr(prevTrack + '.message', track + '.' + cls._PREVIOUS_PRINT_ATTR, force=True)

            prevTrack = track

        return True

#___________________________________________________________________________________________________ removeFromSeries
    @classmethod
    def removeFromSeries(cls):
        tracks = cls.getTargets(1)
        if not tracks:
            return False

        for track in tracks:
            if not cmds.attributeQuery(cls._PREVIOUS_PRINT_ATTR, node=track, exists=True):
                print 'UNRECOGNIZED ITEM: "%s" is not a valid footprint and has been skipped.' % track
                continue

            nextTracks = cls.getNextTracks(track)
            for t in nextTracks:
                cmds.disconnectAttr(track + '.message', t + '.' + cls._PREVIOUS_PRINT_ATTR)

            previousTracks = cls.getPreviousTracks(track)
            for t in previousTracks:
                try:
                    cmds.disconnectAttr(t + '.message', track + '.' + cls._PREVIOUS_PRINT_ATTR)
                except Exception, err:
                    print 'DISCONNECT FAILURE | Unable to disconnect'
                    print '\tTarget:', str(track) + '.' + cls._PREVIOUS_PRINT_ATTR
                    print '\tSource:', str(t) + '.message'
                    raise

            cmds.deleteAttr(track + '.' + cls._PREVIOUS_PRINT_ATTR)
            cmds.connectAttr(
                previousTracks[0] + '.message',
                nextTracks[0] + '.' + cls._PREVIOUS_PRINT_ATTR,
                force=True
            )

        return True

#___________________________________________________________________________________________________ findPrevious
    @classmethod
    def findPrevious(cls, start=False):
        tracks = cls.getTargets(1)
        if not tracks:
            return False

        selection = []
        for track in tracks:
            prev = track
            while True:
                prevs = cls.getPreviousTracks(target=prev)
                if not prevs:
                    break
                prev = prevs[0]

                # Breaks on the first find if the previous was selected
                if not start:
                    break

            if prev not in selection:
                selection.append(prev)

        cmds.select(selection)

#___________________________________________________________________________________________________ findNext
    @classmethod
    def findNext(cls, end=False):
        tracks = cls.getTargets(1)
        if not tracks:
            return False

        selection = []
        for track in tracks:
            nextTrack = track
            while True:
                nexts = cls.getNextTracks(nextTrack)
                if not nexts:
                    break
                nextTrack = nexts[0]

                # Breaks on the first find if the nextTrack was selected
                if not end:
                    break

            if nextTrack not in selection:
                selection.append(nextTrack)

        cmds.select(selection)

#___________________________________________________________________________________________________ isTrack
    @classmethod
    def isTrack(cls, target):
        return cmds.attributeQuery(cls._PREVIOUS_PRINT_ATTR, node=target, exists=True)

#___________________________________________________________________________________________________ getTargets
    @classmethod
    def getTargets(cls, minCount=0):
        targets = cmds.ls(selection=True, exactType='transform')
        if minCount and len(targets) < minCount:
            print 'INVALID SELECTION: You must select at least %s track%s.' \
                  % (str(minCount), 's' if minCount > 1 else '')
            return []

        if not targets:
            return []

        return targets

#___________________________________________________________________________________________________ getPreviousTracks
    @classmethod
    def getPreviousTracks(cls, target=None):
        if not target:
            target = cls.getTargets(1)[0]

        if not cmds.attributeQuery(cls._PREVIOUS_PRINT_ATTR, node=target, exists=True):
            return []

        conns = cmds.listConnections(
            target + '.' + cls._PREVIOUS_PRINT_ATTR,
            source=True,
            plugs=True
        )
        prevs = []
        if conns:
            for c in conns:
                if c.endswith('.message'):
                    prevs.append(c.split('.')[0])
            return prevs

        return []

#___________________________________________________________________________________________________ getNextTracks
    @classmethod
    def getNextTracks(cls, target=None):
        if not target:
            target = cmds.ls(selection=True, exactType='transform')[0]

        connections = cmds.listConnections(
            target + '.message',
            destination=True,
            plugs=True
        )
        nexts = []
        if connections:
            for c in connections:
                if c.endswith('.' + cls._PREVIOUS_PRINT_ATTR):
                    nexts.append(c.split('.')[0])
            return nexts

        return []

#___________________________________________________________________________________________________ getTrackInfo
    @classmethod
    def getTrackInfo(cls):
        tracks = cls.getTargets(1)
        if not tracks:
            return False

        out = []
        for track in tracks:
            out.append({
                'source':track,
                'previous':cls.getPreviousTracks(target=track),
                'next':cls.getNextTracks(target=track)
            })

        return out

#___________________________________________________________________________________________________ initialTrack
    @classmethod
    def initializeTrackway(cls):
        cmds.file('data/pesTokenL.obj', i=True, type='OBJ', renameAll=True, mergeNamespacesOnClash=True,
                  namespace='Cadence', options='mo=1', preserveReferences=True, loadReferenceDepth='all')
        cmds.file('data/pesTokenR.obj', i=True, type='OBJ', renameAll=True, mergeNamespacesOnClash=True,
                  namespace='Cadence', options='mo=1', preserveReferences=True, loadReferenceDepth='all')
        cmds.file('data/manusTokenL.obj', i=True, type='OBJ', renameAll=True, mergeNamespacesOnClash=True,
                  namespace='Cadence', options='mo=1', preserveReferences=True, loadReferenceDepth='all')
        cmds.file('data/manusTokenR.obj', i=True, type='OBJ', renameAll=True, mergeNamespacesOnClash=True,
                  namespace='Cadence', options='mo=1', preserveReferences=True, loadReferenceDepth='all')
        cmds.rename('Cadence:pesTokenL', 'pesTokenLMaster')
        cmds.rename('Cadence:pesTokenR', 'pesTokenRMaster')
        cmds.rename('Cadence:manusTokenL', 'manusTokenLMaster')
        cmds.rename('Cadence:manusTokenR', 'manusTokenRMaster')

        cmds.duplicate('pesTokenLMaster', name='PL1')
        cmds.duplicate('pesTokenRMaster', name='PR1')
        cmds.duplicate('manusTokenLMaster', name='ML1')
        cmds.duplicate('manusTokenRMaster', name='MR1')

        cmds.setAttr('pesTokenLMaster.visibility', 0)
        cmds.setAttr('pesTokenRMaster.visibility', 0)
        cmds.setAttr('manusTokenLMaster.visibility', 0)
        cmds.setAttr('manusTokenRMaster.visibility', 0)

        cmds.move(200.0, 0.0, 100.0, 'PL1' )
        cmds.move(100.0, 0.0, 100.0, 'PR1' )
        cmds.move(200.0, 0.0, 200.0, 'ML1' )
        cmds.move(100.0, 0.0, 200.0, 'MR1' )

        cmds.duplicate('PL1', name='PL2')
        cmds.duplicate('PR1', name='PR2')
        cmds.duplicate('ML1', name='ML2')
        cmds.duplicate('MR1', name='MR2')

        cmds.move(200.0, 0.0, 400.0, 'PL2' )
        cmds.move(100.0, 0.0, 400.0, 'PR2' )
        cmds.move(200.0, 0.0, 500.0, 'ML2' )
        cmds.move(100.0, 0.0, 500.0, 'MR2' )

        cmds.select('PL2')
        cmds.addAttr(longName=cls._PREVIOUS_PRINT_ATTR, attributeType='message')
        cmds.connectAttr('PL1' + '.message', 'PL2' + '.' + cls._PREVIOUS_PRINT_ATTR, force=True)

        cmds.select('PR2')
        cmds.addAttr(longName=cls._PREVIOUS_PRINT_ATTR, attributeType='message')
        cmds.connectAttr('PR1' + '.message', 'PR2' + '.' + cls._PREVIOUS_PRINT_ATTR, force=True)

        cmds.select('ML2')
        cmds.addAttr(longName=cls._PREVIOUS_PRINT_ATTR, attributeType='message')
        cmds.connectAttr('ML1' + '.message', 'ML2' + '.' + cls._PREVIOUS_PRINT_ATTR, force=True)

        cmds.select('MR2')
        cmds.addAttr(longName=cls._PREVIOUS_PRINT_ATTR, attributeType='message')
        cmds.connectAttr('MR1' + '.message', 'MR2' + '.' + cls._PREVIOUS_PRINT_ATTR, force=True)

#___________________________________________________________________________________________________ newTrack
    @classmethod
    def newTrack(cls):
        tracks = cls.getTargets(1)
        if not tracks or len(tracks) != 1:
            return False

        lastTrack = tracks[0]
        prevTracks = cls.getPreviousTracks(lastTrack)
        if not prevTracks:
            return False

        prevTrack = prevTracks[0]
        posPrev = cmds.xform(prevTrack, query=True, translation=True)
        posLast = cmds.xform(lastTrack, query=True, translation=True)
        rotLast = cmds.xform(lastTrack, query=True, rotation=True)
        thisTrack = cmds.duplicate(lastTrack)[0]
        dx = posLast[0] - posPrev[0]
        dy = posLast[1] - posPrev[1]
        dz = posLast[2] - posPrev[2]
        cmds.move(dx, dy, dz, relative=True)
        cmds.rotate(rotLast[0], rotLast[1], rotLast[2])
        cmds.connectAttr(lastTrack + '.message', thisTrack + '.' + cls._PREVIOUS_PRINT_ATTR, force=True)
        return True