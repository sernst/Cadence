# IntegrityAnalyzer.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.integrity.DeviationsStage import DeviationsStage
from cadence.analysis.AnalyzerBase import AnalyzerBase

#___________________________________________________________________________________________________ IntegrityAnalyzer
class IntegrityAnalyzer(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of IntegrityAnalyzer."""
        super(IntegrityAnalyzer, self).__init__(**kwargs)
        self.addStage(DeviationsStage('deviations', self))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ _main_
def _main_():
    IntegrityAnalyzer().run()

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    _main_()
