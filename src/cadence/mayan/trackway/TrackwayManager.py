# TrackwayManager.py
# (C)2012-2013 http://cadence.ThreeAddOne.com
# Scott Ernst

from nimble import cmds

#___________________________________________________________________________________________________ TrackwayManager
class TrackwayManager(object):

    _PREVIOUS_PRINT_ATTR = 'previousPrint'

#___________________________________________________________________________________________________ build
    @classmethod
    def build(cls):
        prints = cls.getTargets(2)
        if not prints or len(prints) < 2:
            return False

        prev = prints[0]
        for p in prints[1:]:
            if not cmds.attributeQuery(cls._PREVIOUS_PRINT_ATTR, node=p, exists=True):
                cmds.addAttr(longName=cls._PREVIOUS_PRINT_ATTR, attributeType='message')

            prevs = cls.getPrevious(p)
            if not prevs or prev not in prevs:
                cmds.connectAttr(prev + '.message', p + '.' + cls._PREVIOUS_PRINT_ATTR, force=True)

            prev = p

        return True

#___________________________________________________________________________________________________ remove
    @classmethod
    def remove(cls):
        prints = cls.getTargets(1)
        if not prints:
            return False

        for p in prints:
            if not cmds.attributeQuery(cls._PREVIOUS_PRINT_ATTR, node=p, exists=True):
                print 'UNRECOGNIZED ITEM: "%s" is not a valid footprint and has been skipped.' % p
                continue

            nexts = cls.getNext(p)
            for c in nexts:
                cmds.disconnectAttr(p + '.message', c + '.' + cls._PREVIOUS_PRINT_ATTR)

            prevs = cls.getPrevious(p)
            for c in prevs:
                try:
                    cmds.disconnectAttr(c + '.message', p + '.' + cls._PREVIOUS_PRINT_ATTR)
                except Exception, err:
                    print 'DISCONNECT FAILURE | Unable to disconnect'
                    print '\tTarget:', str(p) + '.' + cls._PREVIOUS_PRINT_ATTR
                    print '\tSource:', str(c) + '.message'
                    raise

            cmds.deleteAttr(p + '.' + cls._PREVIOUS_PRINT_ATTR)
            cmds.connectAttr(
                prevs[0] + '.message',
                nexts[0] + '.' + cls._PREVIOUS_PRINT_ATTR,
                force=True
            )

        return True


#___________________________________________________________________________________________________ findPrevious
    @classmethod
    def findPrevious(cls, start=False):
        prints = cls.getTargets(1)
        if not prints:
            return False

        selection = []
        for p in prints:
            prev = p
            while True:
                prevs = cls.getPrevious(target=prev)
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
    def findNext(cls, end =False):
        prints = cls.getTargets(1)
        if not prints:
            return False

        selection = []
        for p in prints:
            next = p
            while True:
                nexts = cls.getNext(next)
                if not nexts:
                    break
                next = nexts[0]

                # Breaks on the first find if the next was selected
                if not end:
                    break

            if next not in selection:
                selection.append(next)

        cmds.select(selection)

#___________________________________________________________________________________________________ isFootprint
    @classmethod
    def isFootprint(cls, target):
        return cmds.attributeQuery(cls._PREVIOUS_PRINT_ATTR, node=target, exists=True)

#___________________________________________________________________________________________________ getTargets
    @classmethod
    def getTargets(cls, minCount =0):
        targets = cmds.ls(selection=True, exactType='transform')
        if minCount and len(targets) < minCount:
            print 'INVALID SELECTION: You must select at least %s footprint%s.' \
                  % (str(minCount), 's' if minCount > 1 else '')
            return []

        if not targets:
            return []

        return targets

#___________________________________________________________________________________________________ getPrevious
    @classmethod
    def getPrevious(cls, target=None):
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

#___________________________________________________________________________________________________ getNext
    @classmethod
    def getNext(cls, target=None):
        if not target:
            target = cmds.ls(selection=True, exactType='transform')[0]

        conns = cmds.listConnections(
            target + '.message',
            destination=True,
            plugs=True
        )
        nexts = []
        if conns:
            for c in conns:
                if c.endswith('.' + cls._PREVIOUS_PRINT_ATTR):
                    nexts.append(c.split('.')[0])
            return nexts

        return []

#___________________________________________________________________________________________________ getFootPrintsInfo
    @classmethod
    def getFootPrintsInfo(cls):
        prints = cls.getTargets(1)
        if not prints:
            return False

        out = []
        for p in prints:
            conns = cmds.listConnection
            out.append({
                'source':p,
                'previous':cls.getPrevious(target=p),
                'next':cls.getNext(target=p)
            })

        return out

#___________________________________________________________________________________________________ addTrack
    @classmethod
    def addTrack(cls):
        print "in TrackwayManager, adding track"
        cmds.sphere(radius=1.0)
