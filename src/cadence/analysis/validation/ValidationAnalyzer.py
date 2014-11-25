# ValidationAnalyzer.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.validation.StrideLengthStage import StrideLengthStage
from cadence.analysis.AnalyzerBase import AnalyzerBase

#___________________________________________________________________________________________________ ValidationAnalyzer
class ValidationAnalyzer(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of ValidationAnalyzer."""
        super(ValidationAnalyzer, self).__init__(**kwargs)
        self.addStage(StrideLengthStage('strideLength', self))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ _main_
def _main_():
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        ValidationAnalyzer does...""")

    dit = ValidationAnalyzer()
    dit.run()

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    _main_()

