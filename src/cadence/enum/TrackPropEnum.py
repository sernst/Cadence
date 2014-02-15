# TrackPropEnum.py
# (C)2013-2014
# Scott Ernst and Kent A. Stevens

from collections import namedtuple

from pyaid.reflection.Reflection import Reflection

#___________________________________________________________________________________________________ TRACK_PROP_NT
# A custom data type for track property enumerations that contain the following information:
#   * name      | Key for the track property in both the database and in Maya
#   * type      | The type of attribute for the track property within Maya
#   * intrinsic | True if the track property mirrors an existing property of a Maya transform node
TRACK_PROP_NT = namedtuple('TRACK_PROP_NT', ['name', 'type', 'intrinsic' ])

#___________________________________________________________________________________________________ TrackPropEnum
class TrackPropEnum(object):
    """ A class for all track properties encoded either as additional attributes of the Maya
        transform node which represents a track (of type string or float) or computed from other
        'intrinsic' transform attributes such as scale, rotation, or translation. """

#===================================================================================================
#                                                                                       C L A S S

    # Unique identifier for the track, created when the track is first created and never changed
    # fort the lifetime of the track. The UID has no dependence upon any other track property
    UID             = TRACK_PROP_NT('uid',              'string',   False)

    # Community for the track
    COMM            = TRACK_PROP_NT('community',        'string',   False)
    SITE            = TRACK_PROP_NT('site',             'string',   False)
    YEAR            = TRACK_PROP_NT('year',             'string',   False)
    LEVEL           = TRACK_PROP_NT('level',            'string',   False)
    SECTOR          = TRACK_PROP_NT('sector',           'string',   False)
    TRACKWAY_NUMBER = TRACK_PROP_NT('trackwayNumber',   'string',   False)
    TRACKWAY_TYPE   = TRACK_PROP_NT('trackwayType',     'string',   False)
    LEFT            = TRACK_PROP_NT('left',             'bool',     False)
    PES             = TRACK_PROP_NT('pes',              'bool',     False)
    NUMBER          = TRACK_PROP_NT('number',           'string',   False)
    NOTE            = TRACK_PROP_NT('note',             'string',   False)

    # UID of the previous track in the track series, or an empty string if no previous track exists
    PREV            = TRACK_PROP_NT('prev',             'string',   False)

    # UID of the next track in the track series, or an empty string if no next track exists
    NEXT            = TRACK_PROP_NT('next',             'string',   False)

    # A serialized JSON string of that stores the last saved state of the track for reference
    SNAPSHOT        = TRACK_PROP_NT('snapshot',         'string',   False)

    # The row index of the track entry in the source spreadsheet where the track data was imported
    INDEX           = TRACK_PROP_NT('index',            'float',    False)

    WIDTH           = TRACK_PROP_NT('width',            'float',    True)
    LENGTH          = TRACK_PROP_NT('length',           'float',    True)
    ROTATION        = TRACK_PROP_NT('rotation',         'float',    True)
    X               = TRACK_PROP_NT('x',                'float',    True)
    Z               = TRACK_PROP_NT('z',                'float',    True)

    WIDTH_UNCERTAINTY    = TRACK_PROP_NT('widthUncertainty',    'float', False)
    LENGTH_UNCERTAINTY   = TRACK_PROP_NT('lengthUncertainty',   'float', False)
    ROTATION_UNCERTAINTY = TRACK_PROP_NT('rotationUncertainty', 'float', False)
    WIDTH_MEASURED       = TRACK_PROP_NT('widthMeasured',       'float', False)
    LENGTH_MEASURED      = TRACK_PROP_NT('lengthMeasured',      'float', False)
    DEPTH_MEASURED       = TRACK_PROP_NT('depthMeasured',       'float', False)
    DEPTH_UNCERTAINTY    = TRACK_PROP_NT('depthUncertainty',    'float', False)

    # A 32bit integer containing enumerated flags related to the state and type of the track
    FLAGS         = TRACK_PROP_NT('flags', 'long', False)

    # A 32bit integer containing enumerated flags related to how the track data was imported
    SOURCE_FLAGS  = TRACK_PROP_NT('flags', 'long', False)

    # A 32bit integer containing enumerated flags for how the track should be displayed
    DISPLAY_FLAGS = TRACK_PROP_NT('flags', 'long', False)

#___________________________________________________________________________________________________ TrackPropEnumOps
class TrackPropEnumOps(object):
    """ Support class for helper operations related to the TrackPropEnum class. """

#___________________________________________________________________________________________________ _getTrackPropEnum
    @classmethod
    def getTrackPropEnumByName(cls, name):
        """ Retrieves the TrackPropEnum enumerated value based on the name attribute. """

        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.name == name:
                return enum
        return None
