# AnalysisFlagsEnum.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

#_______________________________________________________________________________
class AnalysisFlagsEnum(object):
    """ Boolean flags to signify states associated with the analysis phase for
        individual tracks. The methods only return new values to be assigned
        to the 'analysisFlags' property for a given track. """

#===============================================================================
#                                                                                       C L A S S

    CLEARED       = 0
    IGNORE_PACE   = 1 << 0
    IGNORE_STRIDE = 1 << 1

#_______________________________________________________________________________
class AnalysisFlagsEnumOps(object):
    """ Support class for helper operations related to the SourceFlagsEnum class. """

#_______________________________________________________________________________
    @classmethod
    def clearAll(cls):
        """ Used to clear all flags associated with the given track. """
        return AnalysisFlagsEnum.CLEARED

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
