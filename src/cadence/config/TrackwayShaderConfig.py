# TrackwayColorConfig.py
# (C)2013
# Kent A. Stevens

from __future__ import \
    print_function, absolute_import, unicode_literals, division

#_______________________________________________________________________________
class TrackwayShaderConfig(object):
    """A class for defining colors"""

#===============================================================================

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
        'uid':   'CadenceBlueLambert',
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
        'transparency': [0.5, 0.5, 0.5]
    }

    LEFT_PES_TOKEN_COLOR = {
        'uid': 'CadenceTransparentDodgerBlue',
        'type': 'lambert',
        'color': [0.12, 0.56, 1.00],
        'transparency': [0.5, 0.5, 0.5]
    }

    LEFT_MANUS_TOKEN_COLOR = {
        'uid': 'CadenceTransparentDarkOliveGreen',
        'type': 'lambert',
        'color': [0.33, 0.42, 0.18 ],
        'transparency': [0.5, 0.5, 0.5]
    }

    RIGHT_PES_TOKEN_COLOR = {
        'uid': 'CadenceTransparentDarkOrange',
        'type': 'lambert',
        'color': [1.00, 0.55, 0.00],
        'transparency': [0.5, 0.5, 0.5]
    }

    RIGHT_MANUS_TOKEN_COLOR = {
        'uid': 'CadenceTransparentDarkOrchid',
        'type': 'lambert',
        'color': [0.6, 0.2, 0.8],
        'transparency': [0.5, 0.5, 0.5]
    }