# TrackwayColorConfig.py
# (C)2013
# Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division

#___________________________________________________________________________________________________ TrackwayColorConfig
class TrackwayShaderConfig(object):
    """A class for defining colors"""

#===================================================================================================

    RED_COLOR = {
        'uid':   'CadenceRedLambert',
        'type':  'lambert',
        'color': [1.0, 0.0, 0.0]
    }

    GREEN_COLOR = {
        'uid':   'CadenceGreenLambert',
        'type':  'lambert',
        'color': [0.0, 1.0, 0.0]
    }

    BLUE_COLOR = {
        'uid':   'CadenceRedLambert',
        'type':  'lambert',
        'color': [0.0, 0.0, 1.0]
    }

    YELLOW_COLOR = {
        'uid':   'CadenceYellowLambert',
        'type':  'lambert',
        'color':  [1.0, 1.0, 0.0]
    }

    LIGHT_GRAY_COLOR = {
        'uid':   'CadenceLightGrayLambert',
        'type':  'lambert',
        'color': [0.85, 0.85, 0.85]
    }

    DARK_GRAY_COLOR = {
        'uid':   'CadenceDarkGrayLambert',
        'type':  'lambert',
        'color': [0.3, 0.3, 0.3]
    }

    WHITE_COLOR = {
        'uid':   'CadenceWhiteLambert',
        'type':  'lambert',
        'color': [1.0, 1.0, 1.0]
    }

    BLACK_COLOR = {
        'uid':   'CadenceBlackLambert',
        'type':  'lambert',
        'color': [0.0, 0.0, 0.0]
    }

    TRANSPARENT_COLOR = {
        'uid':          'CadenceTransparent',
        'type':         'lambert',
        'color':        [0.0, 0.0, 0.0],
        'transparency': [0.9, 0.9, 0.9]
    }
