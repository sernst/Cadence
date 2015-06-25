# TrackwayLoadStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.number.NumericUtils import NumericUtils
from pyaid.system.SystemUtils import SystemUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.models.tracks.Tracks_Track import Tracks_Track



#*************************************************************************************************** TrackwayLoadStage
class TrackwayLoadStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayLoadStage."""
        super(TrackwayLoadStage, self).__init__(
            key, owner,
            label='Database Load',
            **kwargs)

        self.count              = 0
        self.ignoredCount       = 0
        self.incompleteCount    = 0
        self._badTrackCsv       = None
        self._sitemapCsv        = None
        self._trackwayCsv       = None
        self._orphanCsv         = None
        self._unknownCsv        = None
        self._unprocessedCsv    = None
        self._soloTrackCsv      = None
        self._allTracks         = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        csv = CsvWriter()
        csv.path = self.getPath('Solo-Track-Report.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint') )
        self._soloTrackCsv = csv

        csv = CsvWriter()
        csv.path = self.getPath('Corrupt-Track-Report.csv')
        csv.removeIfSavedEmpty = True
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('i', 'Database Index'),
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('reason', 'Reason'))
        self._badTrackCsv = csv

        csv = CsvWriter()
        csv.path = self.getPath('Unprocessed-Track-Report.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('previous', 'Previous Track UID'),
            ('next', 'Next Track UID') )
        self._unprocessedCsv = csv

        csv = CsvWriter()
        csv.path = self.getPath('Unknown-Track-Report.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint') )
        self._unknownCsv = csv

        csv = CsvWriter()
        csv.path = self.getPath('Ignored-Track-Report.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('sitemap', 'Sitemap Name'),
            ('fingerprint', 'Fingerprint'),
            ('hidden', 'Hidden'),
            ('orphan', 'Orphaned') )
        self._orphanCsv = csv

        csv = CsvWriter()
        csv.path = self.getPath('Sitemap-Report.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('name', 'Sitemap Name'),
            ('unprocessed', 'Unprocessed'),
            ('ignores', 'Ignored'),
            ('count', 'Count'),
            ('incomplete', 'Incomplete'),
            ('completion', 'Completion (%)') )
        self._sitemapCsv = csv

        csv = CsvWriter()
        csv.path = self.getPath('Trackway-Report.csv')
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('name', 'Name'),
            ('leftPes', 'Left Pes'),
            ('rightPes', 'Right Pes'),
            ('leftManus', 'Left Manus'),
            ('rightManus', 'Right Manus'),
            ('incomplete', 'Incomplete'),
            ('total', 'Total'),
            ('ready', 'Analysis Ready'),
            ('complete', 'Completion (%)') )
        self._trackwayCsv = csv

        self._allTracks = dict()

        #-------------------------------------------------------------------------------------------
        # CREATE ALL TRACK LISTING
        #       This list is used to find tracks that are not referenced by relationships to
        #       sitemaps, which would never be loaded by standard analysis methods
        model = Tracks_Track.MASTER
        session = model.createSession()
        for t in session.query(model).all():
            self._checkTrackProperties(t)
            self._allTracks[t.uid] = {'uid':t.uid, 'fingerprint':t.fingerprint}
        session.close()

#___________________________________________________________________________________________________ _checkTrackProperties
    def _checkTrackProperties(self, track):
        try:
            year = int(track.year)
        except Exception:
            year = 0

        if year > 2015 or year < 2004:
            self.logger.write([
                '[WARNING]: Invalid track year',
                'YEAR: %s' % year,
                'TRACK[#%s]: %s (%s)' % (track.i, track.fingerprint, track.uid)])
            self._badTrackCsv.createRow(
                i=track.i,
                uid=track.uid,
                fingerprint=track.fingerprint,
                reason='INVALID-YEAR')
            return

#___________________________________________________________________________________________________ _analyzeSitemap
    # noinspection PyUnusedLocal
    def _analyzeSitemap(self, sitemap):
        """_analyzeSitemap doc..."""

        smCount         = 0
        smInCompCount   = 0
        ignores         = 0

        #-------------------------------------------------------------------------------------------
        # SITE MAP TRACKS
        #       Iterate through all the tracks within a sitemap and look for hidden or orphaned
        #       tracks to account for any that may not be loaded by standard means. Any tracks
        #       found this way are removed from the all list created above, which specifies that
        #       they were found by other means.
        tracks    = sitemap.getAllTracks()
        trackways = self.owner.getTrackways(sitemap)
        processed = []

        for t in tracks:
            if t.uid in self._allTracks:
                del self._allTracks[t.uid]

            if t.next and t.next == t.uid:
                self.logger.write([
                    '[ERROR]: Circular track reference (track.uid == track.next)',
                    'TRACK: %s (%s)' % (t.fingerprint, t.uid) ])

            if not t.hidden and t.next:
                continue

            prev = t.getPreviousTrack()
            if prev and not t.hidden:
                continue
            elif not t.hidden:
                # Check for solo tracks, i.e. tracks that are the only track in their series and
                # would appear to be orphaned even though they are in a series because the series
                # itself has no connections
                soloTrack = False
                for tw in trackways:
                    if t.uid in tw.firstTracksList:
                        soloTrack = True
                        break

                if soloTrack:
                    self._soloTrackCsv.createRow(
                        uid=t.uid,
                        fingerprint=t.fingerprint)
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
            processed.append(t)

        #-------------------------------------------------------------------------------------------
        # TRACKWAYS
        #       Iterate over the trackways within the current site
        for tw in self.owner.getTrackways(sitemap):
            series          = dict()
            twCount         = 0
            twIncomplete    = 0
            isReady         = True

            for s in self.owner.getSeriesBundle(tw).asList():
                isReady         = isReady and s.isReady
                twCount        += s.count
                twIncomplete   += len(s.incompleteTracks)

                for t in s.tracks:
                    if t not in processed:
                        processed.append(t)

                suffix = ''
                if not s.isValid:
                    suffix += '*'
                if not s.isComplete:
                    suffix += '...'

                series[s.trackwayKey] = '%s%s' % (int(s.count), suffix)

            completion = NumericUtils.roundToOrder(
                100.0*float(twCount - twIncomplete)/float(twCount), -2)

            self._trackwayCsv.createRow(
                name=tw.name,
                incomplete=twIncomplete,
                total=twCount,
                ready='YES' if isReady else 'NO',
                complete=completion,
                **series)

            self.count           += twCount
            self.incompleteCount += twIncomplete
            smCount              += twCount
            smInCompCount        += twIncomplete

        smUnprocessed = 0
        if len(processed) != len(tracks):
            for pt in processed:
                tracks.remove(pt)

            smUnprocessed = len(tracks)
            for t in tracks:
                pt = t.getPreviousTrack()
                nt = t.getNextTrack()
                self._unprocessedCsv.createRow(
                    uid=t.uid,
                    fingerprint=t.fingerprint,
                    next=nt.uid if nt else 'NONE',
                    previous=pt.uid if pt else 'NONE')

        if smCount == 0:
            completion = 0
        else:
            completion = NumericUtils.roundToOrder(
                100.0*float(smCount - smInCompCount)/float(smCount), -2)

        self._sitemapCsv.createRow(
            name=sitemap.filename,
            count=smCount,
            ignores=ignores,
            incomplete=smInCompCount,
            completion=completion,
            unprocessed=smUnprocessed)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        count       = self.count
        ignoreCount = self.ignoredCount
        self.logger.write('TOTAL TRACKS: %s + (%s ignored) = %s' % (
            count, ignoreCount, count + ignoreCount))

        for uid, data in self._allTracks.items():
            self._unknownCsv.createRow(uid=uid, fingerprint=data['fingerprint'])
        self.logger.write('UNKNOWN TRACK COUNT: %s' % self._unknownCsv.count)
        self._unknownCsv.save()

        self._badTrackCsv.save()
        self._soloTrackCsv.save()
        self._unprocessedCsv.save()
        self._trackwayCsv.save()
        self._sitemapCsv.save()
        self._orphanCsv.save()

