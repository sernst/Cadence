# RunPythonModuleThread.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import nimble

from pyglass.threading.RemoteExecutionThread import RemoteExecutionThread

#_______________________________________________________________________________
class RunPythonModuleThread(RemoteExecutionThread):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, parent, *args, **kwargs):
        """Creates a new instance of RunPythonModuleThread."""
        super(RunPythonModuleThread, self).__init__(parent)
        self._args = args
        self._kwargs = kwargs

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _runImpl(self):
        """Doc..."""
        self._output = nimble.getConnection().runPythonModule(*self._args, **self._kwargs)

