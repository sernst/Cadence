# ImportFlagsEnum.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#___________________________________________________________________________________________________ ImportFlagsEnum
class ImportFlagsEnum(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    NO_WIDTH  = 1 << 0

    NO_LENGTH = 1 << 1

    HIGH_WIDTH_UNCERTAINTY = 1 << 2

    HIGH_LENGTH_UNCERTAINTY = 1 << 3

    NO_ROTATION = 1 << 4

    HIGH_DEPTH_UNCERTAINTY = 1 << 5

    HIGH_ROTATION_UNCERTAINTY = 1 << 6

    HIGH_STRIDE_UNCERTAINTY = 1 << 7

    HIGH_WIDTH_ANGULATION_UNCERTAINTY = 1 << 8

    HIGH_PACE_UNCERTAINTY = 1 << 9

    HIGH_PACE_ANGULATION_UNCERTAINTY = 1 << 10

    HIGH_PROGRESSION_UNCERTAINTY = 1 << 11

    HIGH_GLENO_ACETABULAR_UNCERTAINTY = 1 << 12

