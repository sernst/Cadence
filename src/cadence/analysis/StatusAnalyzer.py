# StatusAnalyzer.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.ArgsUtils import ArgsUtils
from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.AnalyzerBase import AnalyzerBase
from cadence.analysis.CsvWriter import CsvWriter

#*************************************************************************************************** StatusAnalyzer
class StatusAnalyzer(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of StatusAnalyzer."""
        ArgsUtils.addIfMissing('loadHidden', True, kwargs)
        super(StatusAnalyzer, self).__init__(**kwargs)

        self._sitemapCsv = None
        self._trackwayCsv = None
        self.createStage(
            key='count',
            sitemap=self._analyzeSitemap,
            post=self._postCount)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: incompleteCount
    @property
    def incompleteCount(self):
        return self.cache.get('incompleteCount', 0)
    @incompleteCount.setter
    def incompleteCount(self, value):
        self.cache.set('incompleteCount', value, 0)

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

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        smCsv = CsvWriter()
        smCsv.path = self.getPath('Sitemap-Report.csv')
        smCsv.addFields(
            ('name', 'Sitemap Name'),
            ('complete', 'Complete'),
            ('hidden', 'Hidden'),
            ('incomplete', 'Incomplete'),
            ('total', 'Total'),
            ('completion', 'Completion (%)'))
        self._sitemapCsv = smCsv

        twCsv = CsvWriter()
        twCsv.path = self.getPath('Trackway-Report.csv')
        twCsv.addFields(
            ('fingerprint', 'Fingerprint'),
            ('leftPes', 'Left Pes'),
            ('rightPes', 'Right Pes'),
            ('leftManus', 'Left Manus'),
            ('rightManus', 'Right Manus'),
            ('hidden', 'Hidden'),
            ('incomplete', 'Incomplete'),
            ('total', 'Total'),
            ('ready', 'Analysis Ready'),
            ('complete', 'Completion (%)') )
        self._trackwayCsv = twCsv

#___________________________________________________________________________________________________ _addSitemapCsvRow
    def _addSitemapCsvRow(self, sitemap, complete, hidden, incomplete):
        """_addSitemapCsvRow doc..."""
        total = complete + hidden + incomplete

        if total == 0:
            completion = 0
        else:
            completion = NumericUtils.roundToOrder(
                100.0*float(complete + hidden)/float(total), -2)

        self._sitemapCsv.createRow(
            name=sitemap.filename,
            complete=complete,
            hidden=hidden,
            incomplete=incomplete,
            completion=completion,
            total=total)

#___________________________________________________________________________________________________ _addTrackwayCsvRow
    def _addTrackwayCsvRow(self, trackway):
        """_addTrackwayCsvRow doc..."""
        series = dict()
        hidden = 0
        incomplete = 0
        for s in trackway.seriesList:
            hidden += len(s.hiddenTracks)
            incomplete += len(s.incompleteTracks)
            series[s.trackwayKey] = '%s%s' % (
                int(s.count), '' if s.isValid and s.isComplete else '*')

        completion = NumericUtils.roundToOrder(
            100.0*float(trackway.count)/float(trackway.totalCount), -2)

        self._trackwayCsv.createRow(
            fingerprint=trackway.fingerprint,
            hidden=hidden,
            incomplete=incomplete,
            total=trackway.totalCount,
            ready='YES' if trackway.isReady else 'NO',
            complete=completion,
            **series)

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, stage, sitemap):
        """_analyzeSitemap doc..."""
        self.logger.write('%s' % sitemap)

        smCount = 0
        smHidCount = 0
        smInCompCount = 0

        for t in sitemap.getTrackways():
            self._addTrackwayCsvRow(t)

            tc  = t.count
            thc = t.hiddenCount
            tic = t.incompleteCount

            self.count          += tc
            self.hiddenCount    += thc
            self.incompleteCount += tic
            smCount             += tc
            smHidCount          += thc
            smInCompCount       += tic

            h = ('(%s) = %s' % (thc, tc + thc)) if thc else ''
            self.logger.write('   * %s [TRACKS: %s%s]' % (t, tc, h))

        self._addSitemapCsvRow(sitemap, smCount, smHidCount, smInCompCount)
        if smCount or smHidCount:
            h = ('(%s) = %s' % (smHidCount, smCount + smHidCount)) if smHidCount else ''
            self.logger.write('   * TOTAL TRACKS: %s%s' % (smCount, h))

#___________________________________________________________________________________________________ _postAnalyze
    def _postCount(self, stage):

        count    = self.count
        hidCount = self.hiddenCount

        h = ('(%s) = %s' % (hidCount, count + hidCount)) if hidCount else ''
        self.logger.write('TOTAL TRACKS: %s%s' % (count, h))

        self._trackwayCsv.save()
        self._sitemapCsv.save()

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
    c = StatusAnalyzer(logFolderPath=args.logFolderPath)
    c.run()

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    _main_()
