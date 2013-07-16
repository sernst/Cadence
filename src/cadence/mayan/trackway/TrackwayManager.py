# TrackwayManager.py
# (C)2012-2013 http://cadence.ThreeAddOne.com
# Scott Ernst and Kent A. Stevens

import math

from pyaid.debug.Logger import Logger

from nimble import cmds
from nimble.error.MayaCommandException import MayaCommandException

from cadence.config.TrackwayShaderConfig import TrackwayShaderConfig
from cadence.util.shading.ShadingUtils import ShadingUtils

#___________________________________________________________________________________________________ TrackwayManager

class TrackwayManager(object):

    _PREV_ATTR     = 'prevTrack'
    _SITE_ATTR     = 'site'
    _LEVEL_ATTR    = 'level'
    _TRACKWAY_ATTR = 'trackway'
    _NAME_ATTR     = 'name'
    _NOTE_ATTR     = 'note'
    _SNAPSHOT_ATTR = 'snapshot'

    _log = Logger('TrackwayManager')

#============================================================================ TRACK SERIES TRAVERSAL
#___________________________________________________________________________________________________ goTo
    @classmethod
    def goTo(cls, track):
       cls.focusOnTrack('cadenceCam', track)
       cmds.select(track)

#___________________________________________________________________________________________________ goToFirstTrack
    @classmethod
    def goToFirstTrack(cls):
        cls.goTo(cls.getFirstTrack())
#___________________________________________________________________________________________________ goToLastTrack
    @classmethod
    def goToLastTrack(cls):
        cls.goTo(cls.getLastTrack())
#___________________________________________________________________________________________________ goToPreviousTrack
    @classmethod
    def goToPreviousTrack(cls):
        t = cls.getFirstTrackInSegment(cls.getSelectedTracks())
        p = cls.getPrev(t)
        if p:
            cls.goTo(p)
        else:
            cls.goTo(t)
#___________________________________________________________________________________________________ goToNextTrack
    @classmethod
    def goToNextTrack(cls):
        t = cls.getLastTrackInSegment(cls.getSelectedTracks())
        n = cls.getNext(t)
        if n:
            cls.goTo(n)
        else:
            cls.goTo(t)

#===================================================================================================
#___________________________________________________________________________________________________ getFirstTrack
    @classmethod
    def getFirstTrack(cls):
        selected = cls.getSelectedTracks()
        if not selected:
            return None
        t = selected[0]
        while cls.getPrev(t):
            t = cls.getPrev(t)
        return t
#___________________________________________________________________________________________________ getLastTrack
    @classmethod
    def getLastTrack(cls):
        selected = cls.getSelectedTracks()
        if not selected:
            return None
        t = selected[-1]
        while cls.getNext(t):
            t = cls.getNext(t)
        return t
#___________________________________________________________________________________________________ getSelectedObjects
    @classmethod
    def getSelectedObjects(cls):
        return cmds.ls(selection=True, exactType='transform')
#___________________________________________________________________________________________________ isTrack
    @classmethod
    def isTrack(cls, target):
        return cmds.attributeQuery(cls._NAME_ATTR, node=target, exists=True)
#___________________________________________________________________________________________________ getSelectedTracks
    @classmethod
    def getSelectedTracks(cls):
        selected = cls.getSelectedObjects()
        tracks = []
        for s in selected:
            if cls.isTrack(s):
                tracks.append(s)
        return tracks
#___________________________________________________________________________________________________ getFirstTrackInSegment
    @classmethod
    def getFirstTrackInSegment(cls, segment):
        if not segment:
            return None

        s = segment[0]
        while cls.getPrev(s) in segment:
            s = cls.getPrev(s)
        return s
#___________________________________________________________________________________________________ getLastTrackInSegment
    @classmethod
    def getLastTrackInSegment(cls, segment):
        if not segment:
            return None

        s = segment[-1]
        while cls.getNext(s) in segment:
            s = cls.getNext(s)
        return s

#===================================================================================================
#___________________________________________________________________________________________________ getPrev, getNext
    @classmethod
    def getPrev(cls, track):
        connections = cmds.listConnections(track + '.' + cls._PREV_ATTR, source=True, plugs=True)
        if connections:
            for c in connections:
                if c.endswith('.message'):
                    return c.split('.')[0]
        return None

    @classmethod
    def getNext(cls, track):
        connections = cmds.listConnections(track + '.message', destination=True, plugs=True)
        if connections:
            for c in connections:
                if c.endswith('.' + cls._PREV_ATTR):
                    return c.split('.')[0]
        return None

#=================================================================================================== SET / GET
#___________________________________________________________________________________________________ set/get site
    @classmethod
    def setSite(cls, track, site):
        cmds.setAttr(track + '.' + cls._SITE_ATTR, site, type='string')

    @classmethod
    def getSite(cls, track):
        return cmds.getAttr(track + '.' + cls._SITE_ATTR)
#___________________________________________________________________________________________________ set/get level
    @classmethod
    def setLevel(cls, track, level):
        cmds.setAttr(track + '.' + cls._LEVEL_ATTR, level, type='string')

    @classmethod
    def getLevel(cls, track):
        return cmds.getAttr(track + '.' + cls._LEVEL_ATTR)
#___________________________________________________________________________________________________ set/get trackway
    @classmethod
    def setTrackway(cls, track, trackway):
        cmds.setAttr(track + '.' + cls._TRACKWAY_ATTR, trackway, type='string')

    @classmethod
    def getTrackway(cls, track):
        return cmds.getAttr(track + '.' + cls._TRACKWAY_ATTR)
#___________________________________________________________________________________________________ set/get name
    @classmethod
    def setName(cls, track, name):
        cmds.setAttr(track + '.' + cls._NAME_ATTR, name, type='string')
        #
        # site     = cls.getSite(track)
        # level    = cls.getLevel(track)
        # trackway = cls.getTrackway(track)
        # return cmds.rename(track, site + '_' + level + '_' + trackway + '_' + name)

    @classmethod
    def getName(cls, track):
        return cmds.getAttr(track + '.' + cls._NAME_ATTR)
#___________________________________________________________________________________________________ set/get note
    @classmethod
    def setNote(cls, track, note):
        cmds.setAttr(track + '.' + cls._NOTE_ATTR, note, type='string')

    @classmethod
    def getNote(cls, track):
        return cmds.getAttr(track + '.' + cls._NOTE_ATTR)
#___________________________________________________________________________________________________ set/get snapshot
    @classmethod
    def setSnapshot(cls, track, snapshot):
        cmds.setAttr(track + '.' + cls._SNAPSHOT_ATTR, snapshot, type='string')

    @classmethod
    def getSnapshot(cls, track):
        return cmds.getAttr(track + '.' + cls._SNAPSHOT_ATTR)
#___________________________________________________________________________________________________ set/get metadata
    @classmethod
    def setMetadata(cls, track, site, level, trackway, note):
        cls.setSite(track, site)
        cls.setLevel(track, level)
        cls.setTrackway(track, trackway)
        cls.setNote(track, note)

    @classmethod
    def getMetadata(cls, track):
        return [
            cls.getSite(track),
            cls.getLevel(track),
            cls.getTrackway(track),
            cls.getNote(track)]
#___________________________________________________________________________________________________ isPes / isManus
    @classmethod
    def isPes(cls, track):
        return cls.getName(track)[0] is 'P'

    @classmethod
    def isManus(cls, track):
        return cls.getName(track)[0] is 'M'
#___________________________________________________________________________________________________ isRight / isLeft
    @classmethod
    def isRight(cls, track):
        return cls.getName(track)[1] is 'R'

    @classmethod
    def isLeft(cls, track):
        return cls.getName(track)[1] is 'L'
#___________________________________________________________________________________________________ set/get position
    @classmethod
    def setPosition(cls, track, position):
       cmds.move(position[0], position[1], position[2], track, absolute=True)

    @classmethod
    def getPosition(cls, track):
       return cmds.xform(track, query=True, translation=True)
#___________________________________________________________________________________________________ moveRelative
    @classmethod
    def moveRelative(cls, track, dx, dy, dz):
       cmds.move(dx, dy, dz, track, relative=True)
#___________________________________________________________________________________________________ set/get orientation
    @classmethod
    def setOrientation(cls, track, rotation):
        cmds.setAttr(track + '.ry', rotation)

    @classmethod
    def getOrientation(cls, track):
        return cmds.getAttr(track + '.rotateY')
#___________________________________________________________________________________________________ set/get dimensions
    @classmethod
    def setDimensions(cls, track, width, length):
        cmds.scale(width, 1.0, length, track)

    @classmethod
    def getDimensions(cls, track):
        width  = cmds.getAttr(track + '.scaleX')
        length = cmds.getAttr(track + '.scaleZ')
        return [width, length]

#===================================================================================================
#___________________________________________________________________________________________________ incrementName
    @classmethod
    def incrementName(cls, name):
        prefix = name[:2]
        number = int(name[2:])
        return prefix + str(number + 1)
#___________________________________________________________________________________________________ duplicateTrack
    @classmethod
    def duplicateTrack(cls):
        lastTrack = cls.getLastTrack()
        prevTrack = cls.getPrev(lastTrack)
        nextTrack = cmds.duplicate(lastTrack)[0]
        nextTrack = cls.setName(nextTrack, cls.incrementName(cls.getName(lastTrack)))
        p1 = cls.getPosition(prevTrack)
        p2 = cls.getPosition(lastTrack)
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        cls.moveRelative(nextTrack, dx, dy, dz)
        cls.link(lastTrack, nextTrack)

#___________________________________________________________________________________________________ renameSelected
    @classmethod
    def renameSelected(cls, name, site, level, trackway, note):
        selected = cls.getSelectedTracks()
        if not selected:
            return None
        for s in selected:
            cls.setName(s, name)
            t = cls.getNext(s)
            cls.setMetadata(s, site, level, trackway, note)
            name = cls.incrementName(name)

#___________________________________________________________________________________________________ insertTrack
    @classmethod
    def insertTrack(cls):
        t = cls.getLastTrackInSegment(cls.getSelectedTracks())
        n = cls.getNext(t)

#___________________________________________________________________________________________________ createTrack
    @classmethod
    def createTrack(cls, name, site, level, trackway, note):
        r = 50
        a = 2.0*r
        y = (0, 1, 0)
        c = cmds.polyCylinder(r=r, h=5, sx=40, sy=1, sz=1, ax=y, rcp=0, cuv=2, ch=1, n=name)[0]
        if name[0] == 'M':
            ShadingUtils.applyShader(TrackwayShaderConfig.LIGHT_GRAY_COLOR, c)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.DARK_GRAY_COLOR, c)
        cmds.addAttr(longName=cls._PREV_ATTR,     attributeType='message')
        cmds.addAttr(longName=cls._NAME_ATTR,     dataType='string')
        cmds.addAttr(longName=cls._SITE_ATTR,     dataType='string')
        cmds.addAttr(longName=cls._LEVEL_ATTR,    dataType='string')
        cmds.addAttr(longName=cls._TRACKWAY_ATTR, dataType='string')
        cmds.addAttr(longName=cls._NOTE_ATTR,     dataType='string')
        cmds.addAttr(longName=cls._SNAPSHOT_ATTR, dataType='string')

        cmds.setAttr(name + '.' + cls._NAME_ATTR, name, type='string')

        p = cmds.polyPrism(l=4, w=a, ns=3, sh=1, sc=0, ax=y, cuv=3, ch=1, n='pointer')[0]
        cmds.rotate(0.0, -90.0, 0.0)
        cmds.scale(1.0/math.sqrt(3.0), 1.0, 1.0)
        cmds.move(0, 5, a/6.0)
        if name[1] == 'R':
            ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, p)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR, p)

        cmds.setAttr(p + '.overrideEnabled', 1)
        cmds.setAttr(p + '.overrideDisplayType', 2)

        cmds.parent(p, name)
        cls.setMetadata(c, site, level, trackway, note)
        cmds.select(c)
        cmds.setAttr(c + '.translateY', lock=1)
        cmds.setAttr(c + '.rotateX', lock=1)
        cmds.setAttr(c + '.rotateZ', lock=1)
        cmds.setAttr(c + '.scaleY', lock=1)
        return cmds.rename(c, site + '_' + level + '_' + trackway + '_' + name)
#___________________________________________________________________________________________________ initialTrack
    @classmethod
    def initialize(cls, site, level, trackway, note):
        pl1 = cls.createTrack('LP1', site, level, trackway, note)
        pr1 = cls.createTrack('RP1', site, level, trackway, note)
        ml1 = cls.createTrack('LM1', site, level, trackway, note)
        mr1 = cls.createTrack('RM1', site, level, trackway, note)
        pl2 = cls.createTrack('LP2', site, level, trackway, note)
        pr2 = cls.createTrack('RP2', site, level, trackway, note)
        ml2 = cls.createTrack('LM2', site, level, trackway, note)
        mr2 = cls.createTrack('RM2', site, level, trackway, note)

        cls.setPosition(pl1, (200.0, 0.0, 100.0))
        cls.setPosition(pr1, (100.0, 0.0, 100.0))
        cls.setPosition(ml1, (200.0, 0.0, 200.0))
        cls.setPosition(mr1, (100.0, 0.0, 200.0))
        cls.setPosition(pl2, (200.0, 0.0, 400.0))
        cls.setPosition(pr2, (100.0, 0.0, 400.0))
        cls.setPosition(ml2, (200.0, 0.0, 500.0))
        cls.setPosition(mr2, (100.0, 0.0, 500.0))

        cls.link(pl1, pl2)
        cls.link(pr1, pr2)
        cls.link(ml1, ml2)
        cls.link(mr1, mr2)

#===================================================================================================
#___________________________________________________________________________________________________ link / unlink
    @classmethod
    def link(cls, prevTrack, nextTrack):
        p = cls.getPrev(nextTrack)
        if p:
            cls.unlink(p, nextTrack)
        cmds.connectAttr(prevTrack + '.message', nextTrack + '.' + cls._PREV_ATTR, force=True)

    @classmethod
    def unlink(cls, prevTrack, nextTrack):
        cmds.disconnectAttr(prevTrack + '.message', nextTrack + '.' + cls._PREV_ATTR)

#___________________________________________________________________________________________________ linkTracks
    @classmethod
    def linkTracks(cls):
        selected = cls.getSelectedTracks()
        if not selected:
            print "select two or more tracks to link"
            return
        i = 0
        while i < len(selected) - 1:
            cls.link(selected[i], selected[i + 1])
            i += 1
        cmds.select(selected[-1])

#___________________________________________________________________________________________________ unlinkTracks
    @classmethod
    def unlinkTracks(cls):
        selected = cls.getSelectedTracks()
        if not selected:
            return

        s1 = cls.getFirstTrackInSegment(selected)
        s2 = cls.getLastTrackInSegment(selected)
        p = cls.getPrev(s1)
        n = cls.getNext(s2)

        if p and n:            # if track(s) to be unlinked are within
            cls.unlink(p, s1)  # disconnect previous track from first selected track
            cls.unlink(s2, n)  # disconnect last selected track from next track
            cls.link(p, n)     # connect previous to next, bypassing the selected track(s)
            cmds.select(p)     # select the track just prior to the removed track(s)
        elif n and not p:      # selection includes the first track
            cls.unlink(s2, n)
            cmds.select(n)     # and select the track just after the selection
        elif p and not n:      # selection includes the last track
            cls.unlink(p, s1)
            cmds.select(p)     # and bump selection back to the previous track
        for s in selected[0:-1]:
            cls.unlink(s, cls.getNext(s))


#___________________________________________________________________________________________________ cloneTracks
    @classmethod
    def cloneTracks(cls, name, metadata):
        selection = cls.getSelectedObjects()
        if not selection:
            print 'cloneTracks:  enter metadata and the name of first track, then select targets'
            return
        s0 = selection[0]
        track = cls.createTrack(name, *metadata)
        cls.setDimensions(track, *cls.getDimensions(s0))
        cls.setOrientation(track, cls.getOrientation(s0))
        cls.setPosition(track, cls.getPosition(s0))
        source = selection[1:]
        for s in source:
            nextName  = cls.incrementName(cls.getName(track))
            nextTrack = cls.createTrack(nextName, *metadata)
            cls.setDimensions(nextTrack, *cls.getDimensions(s))
            cls.setOrientation(nextTrack, cls.getOrientation(s))
            cls.setPosition(nextTrack, cls.getPosition(s))
            cls.link(track, nextTrack)
            track = nextTrack

#___________________________________________________________________________________________________ getSeries
    @classmethod
    def getSeries(cls):
        selection = cls.getSelectedTracks()
        if not selection:
            return
        first = cls.getFirstTrack()
        series = []
        t = first
        while t:
            series.append(t)
            t = cls.getNext(t)
        return series

#___________________________________________________________________________________________________ selectAll
    @classmethod
    def selectAll(cls):
        series = cls.getSeries()
        cmds.select(series)

#___________________________________________________________________________________________________ selectPrecursors
    @classmethod
    def selectPrecursors(cls):
        selected = cls.getSelectedTracks()
        if not selected:
            print 'Select at least one track'
            return
        series = cls.getSeries()
        precursors = []
        for s in series:
            if s in selected:
                break
            precursors.append(s)
        if precursors:
            cmds.select(precursors)

#___________________________________________________________________________________________________ selectSuccessors
    @classmethod
    def selectSuccessors(cls):
        selected = cls.getSelectedTracks()
        if not selected:
            print 'Select at least one track'
            return
        t = cls.getNext(cls.getLastTrackInSegment(selected))
        if not t:
            return
        successors = [t]
        while cls.getNext(t):
            t = cls.getNext(t)
            successors.append(t)
        if successors:
            cmds.select(successors)

#___________________________________________________________________________________________________ selectSuccessors
    @classmethod
    def deleteSelected(cls):
        selected = cls.getSelectedTracks()
        cls.unlinkTracks()
        cmds.delete(selected)
#___________________________________________________________________________________________________ initializeCamera
    @classmethod
    def initializeCamera(cls):
        if not cmds.objExists('cadenceCam'):
            c = cmds.camera(
                orthographic=True,
                nearClipPlane=1,
                farClipPlane=100000,
                orthographicWidth=300)
            cmds.rename(c[0], 'cadenceCam')
            cmds.rotate(-90, 180, 0)
            cmds.move(0, 100, 0, 'cadenceCam', absolute=True)

#___________________________________________________________________________________________________ focusOnTrack
    @classmethod
    def focusOnTrack(cls, camera, track):
        cls.initializeCamera()
        p = cls.getPosition(track)
        height = cmds.xform(camera, query=True, translation=True)[1]
        cmds.move(p[0], height, p[2], camera, absolute=True)
