# TrackPropEnum.py
# (C)2013
# Kent A. Stevens

from collections import namedtuple

#___________________________________________________________________________________________________ TRACK_PROP_NT
TRACK_PROP_NT = namedtuple('TRACK_PROP_NT', ['name', 'type'])

#___________________________________________________________________________________________________ TrackPropEnum
class TrackPropEnum(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S
    NAME     = TRACK_PROP_NT('name',     'string')
    NOTE     = TRACK_PROP_NT('note',     'string')
    SNAPSHOT = TRACK_PROP_NT('snapshot', 'string')
    INDEX    = TRACK_PROP_NT('index',    'string')
    WIDTH    = TRACK_PROP_NT('width',    'float')
    LENGTH   = TRACK_PROP_NT('length',   'float')
    ROTATION = TRACK_PROP_NT('rotation', 'float')
    X        = TRACK_PROP_NT('x',        'float')
    Z        = TRACK_PROP_NT('z',        'float')

    PREV_TRACK = TRACK_PROP_NT('prevTrack', 'message')

    WIDTH_UNCERTAINTY    = TRACK_PROP_NT('widthUncertainty',     'float')
    LENGTH_UNCERTAINTY   = TRACK_PROP_NT('lengthUncertainty',    'float')
    POSITION_UNCERTAINTY = TRACK_PROP_NT('postitionUncertainty', 'float')
    ROTATION_UNCERTAINTY = TRACK_PROP_NT('rotationUncertainty',  'float')

    WIDTH_MEASURED    = TRACK_PROP_NT('widthMeasured',    'float')
    LENGTH_MEASURED   = TRACK_PROP_NT('lengthMeasured',   'float')
    ROTATION_MEASURED = TRACK_PROP_NT('rotationMeasured', 'float')

