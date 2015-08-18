# Track.py
# (C)2013
# Kent A. Stevens and Scott Ernst


from nimble import cmds

from cadence.enums.TrackPropEnum import TrackPropEnum

#_______________________________________________________________________________
class Track(object):
    """ A track object wraps a reference to a Maya nodeName (it's string name). A track has properties
        that are stored in the nodeName, as string attributes, or floats, or directly by the values of
        the transforms."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, node =None):
        self.node = node

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def depthMeasured(self):
        return self._getTrackAttr(TrackPropEnum.DEPTH_MEASURED)

#_______________________________________________________________________________
    @property
    def depthUncertainty(self):
        return self._getTrackAttr(TrackPropEnum.DEPTH_UNCERTAINTY)

#_______________________________________________________________________________
    @property
    def index(self):
        return self._getTrackAttr(TrackPropEnum.INDEX)

#_______________________________________________________________________________
    @property
    def left(self):
        return self._getTrackAttr(TrackPropEnum.LEFT)

#_______________________________________________________________________________
    @property
    def length(self):
        return self._getTrackAttr(TrackPropEnum.LENGTH, 'scaleZ')

#_______________________________________________________________________________
    @property
    def level(self):
        return self._getTrackAttr(TrackPropEnum.LEVEL)

#_______________________________________________________________________________
    @property
    def name(self):
        number = self.number if self.number else u'-'
        return (u'L' if self.left else u'R') + (u'P' if self.pes else u'M') + number

#_______________________________________________________________________________
    @property
    def nextNode(self):
        connections = cmds.listConnections(self.node + '.message', d=True, p=True)
        if not connections:
            return None

        for c in connections:
            if c.endswith('.prevTrack'):
                node = c.split('.')[0]
                return node
        return None

#_______________________________________________________________________________
    @property
    def next(self):
        n = self.nextNode
        if not n:
            return ""
        t = Track(node=n)
        return t.name

#_______________________________________________________________________________
    @property
    def note(self):
        return self._getTrackAttr(TrackPropEnum.NOTE)

#_______________________________________________________________________________
    @property
    def number(self):
        return self._getTrackAttr(TrackPropEnum.NUMBER).lstrip('0')

#_______________________________________________________________________________
    @property
    def pes(self):
        return self._getTrackAttr(TrackPropEnum.PES)

#_______________________________________________________________________________
    @property
    def prev(self):
        p = self.prevNode
        if not p:
            return ""
        t = Track(node=p)
        name = t.name
        return name

#_______________________________________________________________________________
    @property
    def prevNode(self):
        connections = cmds.listConnections(self.node + '.prevTrack', s=True, p=True)
        if not connections:
            return None

        for c in connections:
            if c.endswith('.message'):
                node = c.split('.')[0]
                return node
        return None

#_______________________________________________________________________________
    @property
    def rotation(self):
        return self._getTrackAttr(TrackPropEnum.ROTATION, 'ry')

#_______________________________________________________________________________
    @property
    def site(self):
        return self._getTrackAttr(TrackPropEnum.SITE)

#_______________________________________________________________________________
    @property
    def sector(self):
        #return self._getTrackAttr(TrackPropEnum.SECTOR)
        return '1'

#_______________________________________________________________________________
    @property
    def trackwayType(self):
        return self._getTrackAttr(TrackPropEnum.TRACKWAY_TYPE)

#_______________________________________________________________________________
    @property
    def trackwayNumber(self):
        return self._getTrackAttr(TrackPropEnum.TRACKWAY_NUMBER).lstrip('0')

#_______________________________________________________________________________
    @property
    def year(self):
    #    return self._getTrackAttr(TrackPropEnum.YEAR)
        return '2009'

#_______________________________________________________________________________
    @property
    def width(self):
        return self._getTrackAttr(TrackPropEnum.WIDTH, 'scaleX')

#_______________________________________________________________________________
    @property
    def x(self):
        return self._getTrackAttr(TrackPropEnum.X, 'translateX')

#_______________________________________________________________________________
    @property
    def z(self):
        return self._getTrackAttr(TrackPropEnum.Z, 'translateZ')

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def getProperty(self, enum):
        if enum.name == TrackPropEnum.WIDTH.name:
            return self.width
        elif enum.name == TrackPropEnum.LENGTH.name:
            return self.length
        elif enum.name == TrackPropEnum.ROTATION.name:
            return self.rotation
        elif enum.name == TrackPropEnum.X.name:
            return self.x
        elif enum.name == TrackPropEnum.Z.name:
            return self.z
        return self._getTrackAttr(enum)

#_______________________________________________________________________________
    def getProperties(self):
        propEnums = [TrackPropEnum.LEFT,
                     TrackPropEnum.LENGTH,
                     TrackPropEnum.LEVEL,
                     TrackPropEnum.NOTE,
                     TrackPropEnum.NUMBER,
                     TrackPropEnum.PES,
                     TrackPropEnum.ROTATION,
                     TrackPropEnum.SITE,
                     TrackPropEnum.TRACKWAY_NUMBER,
                     TrackPropEnum.TRACKWAY_TYPE,
                     TrackPropEnum.WIDTH,
                     TrackPropEnum.X,
                     TrackPropEnum.Z]

        props = dict()
        for enum in propEnums:
            value = self.getProperty(enum)
            if value is not None:
                props[enum.name] = value
#                print "%s : %s" % (enum.name, value)
        return props

#
#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _getTrackAttr(self, enum, mayaAttrName =None):
        if mayaAttrName is None:
            mayaAttrName = enum.name
        return cmds.getAttr(self.node + '.' + mayaAttrName)
