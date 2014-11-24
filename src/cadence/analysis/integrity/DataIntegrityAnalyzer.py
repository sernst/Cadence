# DataIntegrityAnalyzer.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.integrity.DeviationsStage import DeviationsStage
from cadence.analysis.AnalyzerBase import AnalyzerBase

#___________________________________________________________________________________________________ DataIntegrityAnalyzer
class DataIntegrityAnalyzer(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of DataIntegrityAnalyzer."""
        super(DataIntegrityAnalyzer, self).__init__(**kwargs)
        self.addStage(DeviationsStage('deviations', self))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ _main_
def _main_():
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        DataIntegrityAnalyzer does...""")

    dit = DataIntegrityAnalyzer()
    dit.run()

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    _main_()
