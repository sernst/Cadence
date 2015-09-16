# PostProcessor.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

#*******************************************************************************
class PostProcessor(object):
    """A class for..."""

#_______________________________________________________________________________
    def __init__(self, paperFolderName):
        """Creates a new instance of PostProcessor."""
        self._paperFolderName = paperFolderName

    #===========================================================================
    #                                                               P U B L I C

    #___________________________________________________________________________
    def getPlotlyName(self, filename):
        return 'A16/%s/%s' % (self._paperFolderName, filename)

    #===========================================================================
    #                                                         I N T R I N S I C

    #___________________________________________________________________________
    def __repr__(self):
        return self.__str__()

    #___________________________________________________________________________
    def __str__(self):
        return '<%s>' % self.__class__.__name__

