# CadenceApplication.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassApplication import PyGlassApplication

#_______________________________________________________________________________
from cadence.CadenceEnvironment import CadenceEnvironment


class CadenceApplication(PyGlassApplication):

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def debugRootResourcePath(self):
        return ['..', '..', 'resources']

#_______________________________________________________________________________
    @property
    def splashScreenUrl(self):
        return 'splashscreen.png'

#_______________________________________________________________________________
    @property
    def appID(self):
        return CadenceEnvironment.APP_ID

#_______________________________________________________________________________
    @property
    def appGroupID(self):
        return 'cadence'

#_______________________________________________________________________________
    @property
    def mainWindowClass(self):
        from cadence.CadenceMainWindow import CadenceMainWindow
        return CadenceMainWindow

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    CadenceApplication().run()
