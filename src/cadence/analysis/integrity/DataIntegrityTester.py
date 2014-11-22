# DataIntegrityTester.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.AnalyzerBase import AnalyzerBase


#___________________________________________________________________________________________________ DataIntegrityTester
class DataIntegrityTester(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of DataIntegrityTester."""
        super(DataIntegrityTester, self).__init__(**kwargs)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ run
    def run(self):
        """Doc..."""
        for sitemap in self._getSitemaps():
            print('SITEMAP:', sitemap)
            for t in self._getTrackways(sitemap):
                print('  * TRACKWAY:', t)
        return True

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ _main_
def _main_():
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        DataIntegrityTester does...""")

    dit = DataIntegrityTester()
    dit.run()

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    _main_()
