# DataLoadAnalyzer.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.ArgsUtils import ArgsUtils

from cadence.analysis.AnalyzerBase import AnalyzerBase

#*************************************************************************************************** DataLoadAnalyzer
class DataLoadAnalyzer(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of DataLoadAnalyzer."""
        ArgsUtils.addIfMissing('loadHidden', True, kwargs)
        super(DataLoadAnalyzer, self).__init__(**kwargs)

        self.createStage(
            key='count',
            sitemap=self._analyzeSitemap,
            post=self._postCount)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: count
    @property
    def count(self):
        return self.cache.get('count', 0)
    @count.setter
    def count(self, value):
        self.cache.set('count', value, 0)

#___________________________________________________________________________________________________ GS: hiddenCount
    @property
    def hiddenCount(self):
        return self.cache.get('hiddenCount', 0)
    @hiddenCount.setter
    def hiddenCount(self, value):
        self.cache.set('hiddenCount', value, 0)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, stage, sitemap):
        """_analyzeSitemap doc..."""
        self.logger.write('%s' % sitemap)

        smCount = 0
        smHidCount = 0

        for t in sitemap.getTrackways():
            if not t.count:
                continue

            tc  = t.count
            thc = t.hiddenCount

            self.count          += tc
            self.hiddenCount    += thc
            smCount             += tc
            smHidCount          += thc

            h = ('(%s) = %s' % (thc, tc + thc)) if thc else ''
            self.logger.write('   * %s [TRACKS: %s%s]' % (t, tc, h))

        if smCount or smHidCount:
            h = ('(%s) = %s' % (smHidCount, smCount + smHidCount)) if smHidCount else ''
            self.logger.write('   * TOTAL TRACKS: %s%s' % (smCount, h))

#___________________________________________________________________________________________________ _postAnalyze
    def _postCount(self, stage):

        count = self.count
        hidCount = self.hiddenCount

        h = ('(%s) = %s' % (hidCount, count + hidCount)) if hidCount else ''
        self.logger.write('TOTAL TRACKS: %s%s' % (count, h))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ _main_
def _main_():
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        When AnalyzerBase is run from the command line directly, it will output a report of the
        load process to the log, which is used to verify that the tracks and structure being
        loaded by analyzer classes matches the expected load counts based on data entry.""")

    #-----------------------------------------------------------------------------------------------
    # Optional Arguments
    parser.add_argument(
        '-lp', '--logPath', dest='logFolderPath', type=str, help=dedent("""
            The path to a folder where you wish the log file to be stored where the report
            data is written. If omitted the report data will only appear in stdout."""))

    args = parser.parse_args()
    c = DataLoadAnalyzer(logFolderPath=args.logFolderPath)
    c.run()

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    _main_()
