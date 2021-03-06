# Tracks_Trackway.py
# (C)2014-2015
# Scott Ernst and Kent A. Stevens

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from pyaid.debug.Logger import Logger
from pyaid.radix.Base36 import Base36
from pyaid.string.StringUtils import StringUtils
import sqlalchemy as sqla

from cadence.models.tracks.TracksDefault import TracksDefault


# AS NEEDED: from cadence.analysis.TrackSeries import TrackSeries
# AS NEEDED: from cadence.models.tracks.Tracks_Track import Tracks_Track

#_______________________________________________________________________________
class Tracks_Trackway(TracksDefault):

#===============================================================================
#                                                                     C L A S S

    __tablename__ = 'trackways'

    # The uniquely identifying index for this trackway, used for referencing
    _index               = sqla.Column(sqla.Integer, default=0)

    # Custom-defined name for the trackway for display purposes
    _name                = sqla.Column(sqla.Unicode, default='')

    # Index of the sitemap in which this trackway resides
    _siteMapIndex        = sqla.Column(sqla.Integer, default=0)

    # UID of the first track in the specified series, or an empty string if no
    # such series exists
    _firstLeftPes        = sqla.Column(sqla.Unicode, default='')
    _firstRightPes       = sqla.Column(sqla.Unicode, default='')
    _firstLeftManus      = sqla.Column(sqla.Unicode, default='')
    _firstRightManus     = sqla.Column(sqla.Unicode, default='')

#_______________________________________________________________________________
    def __init__(self, **kwargs):
        super(Tracks_Trackway, self).__init__(**kwargs)

#===============================================================================
#                                                                 G E T / S E T

#_______________________________________________________________________________
    @property
    def isEmpty(self):
        return len(self.firstTracksList) == 0

#_______________________________________________________________________________
    @property
    def firstTracksList(self):
        out = []
        if self.firstLeftPes:
            out.append(self.firstLeftPes)
        if self.firstRightPes:
            out.append(self.firstRightPes)
        if self.firstLeftManus:
            out.append(self.firstLeftManus)
        if self.firstRightManus:
            out.append(self.firstRightManus)
        return out

#_______________________________________________________________________________
    @property
    def uid(self):
        return Base36.to36(self.index)

#_______________________________________________________________________________
    @property
    def sitemap(self):
        out = self.fetchTransient('sitemap')
        if not out:
            return self.getSitemap()
        return out
    @sitemap.setter
    def sitemap(self, value):
        self.putTransient('sitemap', value)

#===============================================================================
#                                                                   P U B L I C

#_______________________________________________________________________________
    def getTrackwaySeriesBundle(self):
        """ Creates an ordered dictionary containing the track series for each
            series in the trackway, even if one of the series has no tracks. The
            keys of the dictionary match the key value of the track series
            instance, i.e. TrackSeries.key.

            @return: TrackSeriesBundle """

        from cadence.analysis.TrackSeriesBundle import TrackSeriesBundle

        bundle = TrackSeriesBundle(self)
        bundle.load()
        return bundle

#_______________________________________________________________________________
    def getSitemap(self):
        """getSitemap doc..."""
        if not self.siteMapIndex:
            return None

        from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
        model = Tracks_SiteMap.MASTER
        return self.mySession.query(model).filter(
            model.index == self.siteMapIndex).first()

#_______________________________________________________________________________
    @classmethod
    def populateTrackwaysTable(cls, session =None, logger =None):
        """ Populate the trackways table by removing all existing rows and
            attempting to calculate trackways from the implicit track series
            defined by the linkages of tracks. This operation should only be
            carried out for initial population purposes as it will dispose of
            all existing data and changes made by users. """

        from cadence.models.tracks.Tracks_Track import Tracks_Track
        from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap

        missingSitemaps = []

        sitemapModel = Tracks_SiteMap.MASTER
        trackModel   = Tracks_Track.MASTER
        model        = cls.MASTER

        if not logger:
            logger = Logger(cls, printOut=True)

        newSession = False
        if not session:
            newSession = True
            session = model.createSession()

        # Get all tracks that have no next (end of a track series)
        endTracks = session.query(trackModel).filter(
            trackModel.next == '').all()

        index     = 0
        trackways = dict()
        tested    = []

        for track in endTracks:
            if track in tested or track.hidden:
                # Skip tracks that have already been tested or are hidden
                continue

            prev = track
            while prev:
                tested.append(prev)
                t = prev.getPreviousTrack()
                if not t:
                    break
                prev = t

            if not prev:
                continue

            name = prev.trackwayFingerprint

            sitemapStamp = '%s-%s' % (prev.site, prev.level)
            if sitemapStamp in missingSitemaps:
                # Ignore the trackway if there's no sitemap to support it
                continue

            if name in trackways:
                tw = trackways[name]
            else:
                # If the trackway name isn't in the list of existing trackways,
                # create a new trackway model instance for that trackway

                tw       = Tracks_Trackway()
                tw.index = index
                tw.name  = name

                sitemap = session.query(sitemapModel).filter(
                    sitemapModel.name == prev.site).filter(
                    sitemapModel.level == prev.level).first()
                if not sitemap:
                    missingSitemaps.append(sitemapStamp)
                    logger.write(
                        '[WARNING]: No site map found for "%s" level "%s"' % (
                        prev.site, prev.level))
                else:
                    tw.siteMapIndex = sitemap.index
                    index += 1
                    trackways[tw.name] = tw

            if prev.left and prev.pes:
                existing = tw.firstLeftPes
                tw.firstLeftPes = prev.uid
            elif prev.left:
                existing = tw.firstLeftManus
                tw.firstLeftManus = prev.uid
            elif prev.pes:
                existing = tw.firstRightPes
                tw.firstRightPes = prev.uid
            else:
                existing = tw.firstRightManus
                tw.firstRightManus = prev.uid

            if existing and existing != prev.uid:
                logger.write([
                    '[WARNING]: Duplicate tracks found for the same series',
                    'TRACKS: "%s" AND "%s"' % (existing, prev.uid),
                    'TRACKWAY: %s' % tw.name])

        # Delete all existing rows if any exist
        rowCount = session.query(model).count()
        if rowCount > 0:
            session.query(model).delete()

        # Add the new trackways entries to the session
        for fingerprint, trackway in trackways.items():
            session.add(trackway)

        if newSession:
            session.commit()
            session.close()

#===============================================================================
#                                                             P R O T E C T E D

#_______________________________________________________________________________
    def _getAnalysisPair(self, session, createIfMissing):
        """_getAnalysisPair doc..."""

        from cadence.models.analysis.Analysis_Trackway import Analysis_Trackway
        model = Analysis_Trackway.MASTER

        result = session.query(model).filter(model.index == self.index).first()

        if createIfMissing and not result:
            result = model()
            result.index = self.index
            session.add(result)
            session.flush()

        return result

#===============================================================================
#                                                             I N T R I N S I C

#_______________________________________________________________________________
    def __str__(self):
        """__str__ doc..."""
        return StringUtils.toStr2(
            '<Trackway[%s] %s "%s">' % (self.i, self.index, self.name))
