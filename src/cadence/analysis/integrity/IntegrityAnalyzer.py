# IntegrityAnalyzer.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.integrity.RotationStage import RotationStage
from cadence.analysis.integrity.LengthWidthStage import LengthWidthStage
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
        self.addStage(LengthWidthStage('lengthWidth', self))
        self.addStage(RotationStage('rotation', self))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    IntegrityAnalyzer().run()
