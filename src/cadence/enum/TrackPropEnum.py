# TrackPropEnum.py
# (C)2013
# Kent A. Stevens

from collections import namedtuple

#___________________________________________________________________________________________________ TRACK_PROP_NT
TRACK_PROP_NT = namedtuple('TRACK_PROP_NT', ['name', 'type', 'intrinsic'])

#___________________________________________________________________________________________________ TrackPropEnum
class TrackPropEnum(object):
    """A class for all track properties encoded either as additional attributes of the Maya
    transform node which represents a track (of type string or float) or computed from other
    'intrinsic' transform attributes such as scale, rotation, or translation."""

#===================================================================================================
#                                                                                       C L A S S

    COMM     = TRACK_PROP_NT('community', 'string', False)
    SITE     = TRACK_PROP_NT('site',      'string', False)
    YEAR     = TRACK_PROP_NT('year',      'string', False)
    LEVEL    = TRACK_PROP_NT('level',     'string', False)
    SECTOR   = TRACK_PROP_NT('sector',    'string', False)
    TRACKWAY = TRACK_PROP_NT('trackway',  'string', False)
    NAME     = TRACK_PROP_NT('name',      'string', False)
    NOTE     = TRACK_PROP_NT('note',      'string', False)
    PREV     = TRACK_PROP_NT('prev',      'string', False)
    NEXT     = TRACK_PROP_NT('next',      'string', False)
    SNAPSHOT = TRACK_PROP_NT('snapshot',  'string', False)
    INDEX    = TRACK_PROP_NT('index',     'string', False)
    ID       = TRACK_PROP_NT('id',        'string', False)
    WIDTH    = TRACK_PROP_NT('width',     'float',  True)
    LENGTH   = TRACK_PROP_NT('length',    'float',  True)
    ROTATION = TRACK_PROP_NT('rotation',  'float',  True)
    X        = TRACK_PROP_NT('x',         'float',  True)
    Z        = TRACK_PROP_NT('z',         'float',  True)

    WIDTH_UNCERTAINTY    = TRACK_PROP_NT('widthUncertainty',    'float', False)
    LENGTH_UNCERTAINTY   = TRACK_PROP_NT('lengthUncertainty',   'float', False)
    ROTATION_UNCERTAINTY = TRACK_PROP_NT('rotationUncertainty', 'float', False)
    WIDTH_MEASURED       = TRACK_PROP_NT('widthMeasured',       'float', False)
    LENGTH_MEASURED      = TRACK_PROP_NT('lengthMeasured',      'float', False)
    DEPTH_MEASURED       = TRACK_PROP_NT('depthMeasured',       'float', False)
    DEPTH_UNCERTAINTY    = TRACK_PROP_NT('depthUncertainty',    'float', False)
