# TrackwayColorConfig.py
# (C)2013
# Kent A. Stevens

#___________________________________________________________________________________________________ TrackwayColorConfig
class TrackwayShaderConfig(object):
    """A class for defining colors"""

#===================================================================================================

    GREEN_COLOR = {
        'uid': 'CadenceGreenLambert',
        'type': 'lambert',
        'color': [0.0, 1.0, 0.0]
    }

    RED_COLOR = {
        'uid': 'CadenceRedLambert',
        'type': 'lambert',
        'color': [1.0, 0.0, 0.0]
    }


    LIGHT_GRAY_COLOR = {
        'uid': 'CadenceLightGrayLambert',
        'type': 'lambert',
        'color': [0.8, 0.8, 0.8]
    }

    DARK_GRAY_COLOR = {
        'uid': 'CadenceDarkGrayLambert',
        'type': 'lambert',
        'color': [0.4, 0.4, 0.4]
    }
