# CadenceCompiler.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.compile.PyGlassApplicationCompiler import PyGlassApplicationCompiler
from pyglass.compile.SiteLibraryEnum import SiteLibraryEnum

#_______________________________________________________________________________
class CadenceCompiler(PyGlassApplicationCompiler):
    """A class for..."""

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def siteLibraries(self):
        return [SiteLibraryEnum.PYSIDE, SiteLibraryEnum.SQL_ALCHEMY]

#_______________________________________________________________________________
    @property
    def binPath(self):
        return ['..', '..', 'bin']

#_______________________________________________________________________________
    @property
    def appFilename(self):
        return 'Cadence'

#_______________________________________________________________________________
    @property
    def appDisplayName(self):
        return 'Cadence'

#_______________________________________________________________________________
    @property
    def applicationClass(self):
        from cadence.CadenceApplication import CadenceApplication
        return CadenceApplication

#_______________________________________________________________________________
    @property
    def iconPath(self):
        return ['apps', 'Cadence']

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    CadenceCompiler().run()

