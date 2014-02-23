# Track.py
# (C)2013
# Kent A. Stevens and Scott Ernst


from nimble import cmds

from cadence.enum.TrackPropEnum import TrackPropEnum

#___________________________________________________________________________________________________ Track
class Track(object):
    """ A track object wraps a reference to a Maya node (it's string name). A track has properties
        that are stored in the node, as string attributes, or floats, or directly by the values of
        the transforms."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, node =None):
        self.node = node

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: comm
    @property
    def comm(self):
        return self._getTrackAttr(TrackPropEnum.COMM)

#___________________________________________________________________________________________________ GS: depthMeasured
    @property
    def depthMeasured(self):
        return self._getTrackAttr(TrackPropEnum.DEPTH_MEASURED)

#___________________________________________________________________________________________________ GS: depthUncertainty
    @property
    def depthUncertainty(self):
        return self._getTrackAttr(TrackPropEnum.DEPTH_UNCERTAINTY)

#___________________________________________________________________________________________________ GS: index
    @property
    def index(self):
        return self._getTrackAttr(TrackPropEnum.INDEX)

#___________________________________________________________________________________________________ GS: left
    @property
    def left(self):
        return self._getTrackAttr(TrackPropEnum.LEFT)

#___________________________________________________________________________________________________ GS: length
    @property
    def length(self):
        return self._getTrackAttr(TrackPropEnum.LENGTH, 'scaleZ')

#___________________________________________________________________________________________________ GS: level
    @property
    def level(self):
        return self._getTrackAttr(TrackPropEnum.LEVEL)

#___________________________________________________________________________________________________ GS: name
    @property
    def name(self):
        number = self.number if self.number else u'-'
        return (u'L' if self.left else u'R') + (u'P' if self.pes else u'M') + number

#___________________________________________________________________________________________________ GS: nextNode
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

#___________________________________________________________________________________________________ GS: nextTrack
    @property
    def next(self):
        n = self.nextNode
        if not n:
            return ""
        t = Track(node=n)
        return t.name

#___________________________________________________________________________________________________ GS: note
    @property
    def note(self):
        return self._getTrackAttr(TrackPropEnum.NOTE)

#___________________________________________________________________________________________________ GS: number
    @property
    def number(self):
        return self._getTrackAttr(TrackPropEnum.NUMBER)

#___________________________________________________________________________________________________ GS: pes
    @property
    def pes(self):
        return self._getTrackAttr(TrackPropEnum.PES)

#___________________________________________________________________________________________________ GS: prev
    @property
    def prev(self):
        p = self.prevNode
        if not p:
            return ""
        t = Track(node=p)
        name = t.name
        return name

#___________________________________________________________________________________________________ GS: prevNode
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

#___________________________________________________________________________________________________ GS: rotation
    @property
    def rotation(self):
        return self._getTrackAttr(TrackPropEnum.ROTATION, 'ry')

#___________________________________________________________________________________________________ GS: site
    @property
    def site(self):
        return self._getTrackAttr(TrackPropEnum.SITE)

#___________________________________________________________________________________________________ GS: sector
    @property
    def sector(self):
        return self._getTrackAttr(TrackPropEnum.SECTOR)

#___________________________________________________________________________________________________ GS: trackwayType
    @property
    def trackwayType(self):
        return self._getTrackAttr(TrackPropEnum.TRACKWAY_TYPE)

#___________________________________________________________________________________________________ GS: trackwayNumber
    @property
    def trackwayNumber(self):
        return self._getTrackAttr(TrackPropEnum.TRACKWAY_NUMBER)

#___________________________________________________________________________________________________ GS: year
    @property
    def year(self):
        return self._getTrackAttr(TrackPropEnum.YEAR)

#___________________________________________________________________________________________________ GS: width
    @property
    def width(self):
        return self._getTrackAttr(TrackPropEnum.WIDTH, 'scaleX')

#___________________________________________________________________________________________________ GS: x
    @property
    def x(self):
        return self._getTrackAttr(TrackPropEnum.X, 'translateX')

#___________________________________________________________________________________________________ GS: z
    @property
    def z(self):
        return self._getTrackAttr(TrackPropEnum.Z, 'translateZ')

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getProperty
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

#___________________________________________________________________________________________________ getProperties
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
#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getTrackAttr
    def _getTrackAttr(self, enum, mayaAttrName =None):
        if mayaAttrName is None:
            mayaAttrName = enum.name
        return cmds.getAttr(self.node + '.' + mayaAttrName)
