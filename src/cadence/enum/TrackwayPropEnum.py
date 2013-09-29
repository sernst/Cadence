# TrackwayPropEnum.py
# (C)2013
# Kent A. Stevens

from collections import namedtuple

#___________________________________________________________________________________________________ TRACK_PROP_NT
TRACKWAY_PROP_NT = namedtuple('TRACKWAY_PROP_NT', ['name', 'type'])


#___________________________________________________________________________________________________ MetadataEnum
class TrackwayPropEnum(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S
    COMM     = TRACKWAY_PROP_NT('community', 'string')
    SITE     = TRACKWAY_PROP_NT('site',      'string')
    YEAR     = TRACKWAY_PROP_NT('year',      'string')
    LEVEL    = TRACKWAY_PROP_NT('level',     'string')
    TRACKWAY = TRACKWAY_PROP_NT('trackway',  'string')
    SECTOR   = TRACKWAY_PROP_NT('sector',    'string')

