# TrackPropEnum.py
# (C)2013
# Kent A. Stevens

from collections import namedtuple

#___________________________________________________________________________________________________ TRACK_PROP_NT
TRACK_PROP_NT = namedtuple('TRACK_PROP_NT', ['name', 'type'])

#___________________________________________________________________________________________________ TrackPropEnum
class TrackPropEnum(object):
    """A class for all track properties encoded either as additional attributes of the Maya
    transform node which represents a track (of type string or float) or computed from other
    transform attributes such as scale, rotation, or translation."""

#===================================================================================================
#                                                                                       C L A S S

    COMM     = TRACK_PROP_NT('community', 'string')
    SITE     = TRACK_PROP_NT('site',      'string')
    YEAR     = TRACK_PROP_NT('year',      'string')
    LEVEL    = TRACK_PROP_NT('level',     'string')
    SECTOR   = TRACK_PROP_NT('sector',    'string')
    TRACKWAY = TRACK_PROP_NT('trackway',  'string')
    NAME     = TRACK_PROP_NT('name',      'string')
    NOTE     = TRACK_PROP_NT('note',      'string')
    PREV     = TRACK_PROP_NT('prev',      'string')
    NEXT     = TRACK_PROP_NT('next',      'string')
    SNAPSHOT = TRACK_PROP_NT('snapshot',  'string')
    INDEX    = TRACK_PROP_NT('index',     'string')
    WIDTH    = TRACK_PROP_NT('width',     'float')
    LENGTH   = TRACK_PROP_NT('length',    'float')
    ROTATION = TRACK_PROP_NT('rotation',  'float')
    X        = TRACK_PROP_NT('x',         'float')
    Z        = TRACK_PROP_NT('z',         'float')

    WIDTH_UNCERTAINTY    = TRACK_PROP_NT('widthUncertainty',    'float')
    LENGTH_UNCERTAINTY   = TRACK_PROP_NT('lengthUncertainty',   'float')
    ROTATION_UNCERTAINTY = TRACK_PROP_NT('rotationUncertainty', 'float')
    WIDTH_MEASURED       = TRACK_PROP_NT('widthMeasured',       'float')
    LENGTH_MEASURED      = TRACK_PROP_NT('lengthMeasured',      'float')

