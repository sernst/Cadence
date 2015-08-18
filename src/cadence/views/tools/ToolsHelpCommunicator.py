# ToolsHelpCommunicator.py
# (C)2013
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import markdown

from PySide import QtCore
from pyaid.string.StringUtils import StringUtils

from pyglass.web.PyGlassCommunicator import PyGlassCommunicator

#_______________________________________________________________________________
class ToolsHelpCommunicator(PyGlassCommunicator):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        """Creates a new instance of ToolsHelpCommunicator."""
        super(ToolsHelpCommunicator, self).__init__(None, **kwargs)
        self._target = None
        self._content = None

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def javaScriptID(self):
        return 'CADENCE'

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def loadContent(self, target):
        self._target = target
        helpPath     = target.getResourcePath('help.markdown', isFile=True)

        try:
            if os.path.exists(helpPath):
                f = open(helpPath, 'r+')
                md = f.read().encode('utf-8', 'ignore')
                f.close()
                self._content = markdown.markdown(md)
            else:
                return False
        except Exception:
            return False

        self.callUpdate()
        return True

#_______________________________________________________________________________
    @QtCore.Slot(result=StringUtils.TEXT_TYPE)
    def getContent(self):
        return self._content if self._content else u''

