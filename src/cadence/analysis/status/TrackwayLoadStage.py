# TrackwayLoadStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.number.NumericUtils import NumericUtils
from pyaid.system.SystemUtils import SystemUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.CsvWriter import CsvWriter
from cadence.models.tracks.Tracks_Track import Tracks_Track



#*************************************************************************************************** TrackwayLoadStage
class TrackwayLoadStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayLoadStage."""
        super(TrackwayLoadStage, self).__init__(key, owner, **kwargs)

        self.count              = 0
        self.ignoredCount       = 0
        self.incompleteCount    = 0
        self._sitemapCsv        = None
        self._trackwayCsv       = None
        self._orphanCsv         = None
        self._unknownCsv        = None
        self._allTracks         = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        csv = CsvWriter()
        csv.path = self.getPath('Unknown-Track-Report.csv')
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint') )
        self._unknownCsv = csv

        csv = CsvWriter()
        csv.path = self.getPath('Ignored-Track-Report.csv')
        csv.addFields(
            ('uid', 'UID'),
            ('sitemap', 'Sitemap Name'),
            ('fingerprint', 'Fingerprint'),
            ('hidden', 'Hidden'),
            ('orphan', 'Orphaned') )
        self._orphanCsv = csv

        smCsv = CsvWriter()
        smCsv.path = self.getPath('Sitemap-Report.csv')
        smCsv.addFields(
            ('name', 'Sitemap Name'),
            ('ignores', 'Ignored'),
            ('count', 'Count'),
            ('incomplete', 'Incomplete'),
            ('completion', 'Completion (%)') )
        self._sitemapCsv = smCsv

        twCsv = CsvWriter()
        twCsv.path = self.getPath('Trackway-Report.csv')
        twCsv.addFields(
            ('name', 'Name'),
            ('leftPes', 'Left Pes'),
            ('rightPes', 'Right Pes'),
            ('leftManus', 'Left Manus'),
            ('rightManus', 'Right Manus'),
            ('incomplete', 'Incomplete'),
            ('total', 'Total'),
            ('ready', 'Analysis Ready'),
            ('complete', 'Completion (%)') )
        self._trackwayCsv = twCsv

        self._allTracks = dict()

        #-------------------------------------------------------------------------------------------
        # CREATE ALL TRACK LISTING
        #       This list is used to find tracks that are not referenced by relationships to
        #       sitemaps, which would never be loaded by standard analysis methods
        model = Tracks_Track.MASTER
        session = model.createSession()
        for t in session.query(model).all():
            self._allTracks[t.uid] = {'uid':t.uid, 'fingerprint':t.fingerprint}
        session.close()

#___________________________________________________________________________________________________ _addSitemapCsvRow
    def _addSitemapCsvRow(self, sitemap, count, incomplete, ignores):
        """_addSitemapCsvRow doc..."""

        if count == 0:
            completion = 0
        else:
            completion = NumericUtils.roundToOrder(100.0*float(count - incomplete)/float(count), -2)

        self._sitemapCsv.createRow(
            name=sitemap.filename,
            count=count,
            ignores=ignores,
            incomplete=incomplete,
            completion=completion)

#___________________________________________________________________________________________________ _addTrackwayCsvRow
    def _addTrackwayCsvRow(self, trackway):
        """_addTrackwayCsvRow doc..."""
        series      = dict()
        count       = 0
        incomplete  = 0
        isReady     = True

        for key, s in self.owner.getTrackwaySeries(trackway).items():
            isReady     = isReady and s.isReady
            count      += s.count
            incomplete += len(s.incompleteTracks)

            suffix = ''
            if not s.isValid:
                suffix += '*'
            if not s.isComplete:
                suffix += '...'

            series[s.trackwayKey] = '%s%s' % (int(s.count), suffix)

        completion = NumericUtils.roundToOrder(100.0*float(count - incomplete)/float(count), -2)

        self._trackwayCsv.createRow(
            name=trackway.name,
            incomplete=incomplete,
            total=count,
            ready='YES' if isReady else 'NO',
            complete=completion,
            **series)

        return count, incomplete

#___________________________________________________________________________________________________ _analyzeSitemap
    # noinspection PyUnusedLocal
    def _analyzeSitemap(self, sitemap):
        """_analyzeSitemap doc..."""
        self.logger.write('%s' % sitemap)

        smCount         = 0
        smInCompCount   = 0
        ignores         = 0

        #-------------------------------------------------------------------------------------------
        # SITE MAP TRACKS
        #       Iterate through all the tracks within a sitemap and look for hidden or orphaned
        #       tracks to account for any that may not be loaded by standard means. Any tracks
        #       found this way are removed from the all list created above, which specifies that
        #       they were found by other means.
        for t in sitemap.getAllTracks():
            if t.uid in self._allTracks:
                del self._allTracks[t.uid]

            if not t.hidden and t.next:
                continue

            prev = t.getPreviousTrack()
            if prev and not t.hidden:
                continue

            self.ignoredCount += 1
            ignores += 1

            isOrphaned = not t.next and not prev

            self._orphanCsv.createRow(
                fingerprint=t.fingerprint,
                orphan='YES' if isOrphaned else 'NO',
                hidden='YES' if t.hidden else 'NO',
                uid=t.uid,
                sitemap=sitemap.filename)

        #-------------------------------------------------------------------------------------------
        # TRACKWAYS
        #       Iterate over the trackways within the current site
        for t in self.owner.getTrackways(sitemap):
            stats = self._addTrackwayCsvRow(t)

            tc  = stats[0]
            tic = stats[1]

            self.count           += tc
            self.incompleteCount += tic
            smCount              += tc
            smInCompCount        += tic

            self.logger.write('   * %s [TRACKS: %s]' % (t, tc))

        self._addSitemapCsvRow(sitemap, smCount, smInCompCount, ignores)
        if smCount:
            self.logger.write('   * TOTAL TRACKS: %s' % smCount)

        if ignores:
            self.logger.write('   * IGNORED TRACKS: %s' % ignores)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        count       = self.count
        ignoreCount = self.ignoredCount
        self.logger.write('TOTAL TRACKS: %s + (%s ignored) = %s' % (
            count, ignoreCount, count + ignoreCount))

        SystemUtils.remove(self._unknownCsv.path)
        if self._allTracks:
            for uid, data in self._allTracks.items():
                self._unknownCsv.createRow(uid=uid, fingerprint=data['fingerprint'])
            self._unknownCsv.save()

        self._trackwayCsv.save()
        self._sitemapCsv.save()
        self._orphanCsv.save()
