# SourceFlagsEnum.py
# (C) 2014
# Kent A. Stevens

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

#_______________________________________________________________________________
class SourceFlagsEnum(object):
    """ Boolean flags to signify states associated with the source data for
        individual tracks. The methods only return new values to be assigned
        to the 'sourceFlags' property for a given track. """

#===============================================================================
#                                                                   C L A S S

    CLEARED = 0
    COMPLETED = 1 << 0
    MARKED    = 1 << 1
    LOCKED    = 1 << 2

#_______________________________________________________________________________
class SourceFlagsEnumOps(object):
    """ Support class for helper operations related to the SourceFlagsEnum
        class. """

#_______________________________________________________________________________
    @classmethod
    def clearAll(cls):
        """ Used to clear all flags associated with the given track. """
        return SourceFlagsEnum.CLEARED

#_______________________________________________________________________________
    @classmethod
    def set(cls, flags, flag):
        """ Sets the specified flag in flags. """
        return flags | flag

#_______________________________________________________________________________
    @classmethod
    def clear(cls, flags, flag):
        """ Clears the specified flag in flags. """
        return flags & ~flag

#_______________________________________________________________________________
    @classmethod
    def get(cls, flags, flag):
        """ returns a boolean indicating whether the specified flag is set or
            clear in flags. """
        return bool(flags & flag)
