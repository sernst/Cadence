# AnalyzerBase.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.dict.DictUtils import DictUtils
from cadence.analysis.TrackSeries import TrackSeries

from cadence.analysis.Trackway import Trackway
from cadence.enums.SourceFlagsEnum import SourceFlagsEnum
from cadence.enums.TrackPropEnum import TrackPropEnum
from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.models.tracks.Tracks_Track import Tracks_Track


#*************************************************************************************************** AnalyzerBase
class AnalyzerBase(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of AnalyzerBase."""
        self._tracksSession = kwargs.get('tracksSession')

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getTracksSession
    def _getTracksSession(self):
        """_getTracksSession doc..."""
        if self._tracksSession is None:
            self._tracksSession = Tracks_SiteMap.createSession()
        return self._tracksSession

#___________________________________________________________________________________________________ _closeTracksSession
    def _closeTracksSession(self, commit =True):
        """_closeTracksSession doc..."""
        if not self._tracksSession:
            return

        if commit:
            self._tracksSession.commit()
        self._tracksSession.close()
        self._tracksSession = None

#___________________________________________________________________________________________________ _getSitemaps
    def _getSitemaps(self):
        model   = Tracks_SiteMap.MASTER
        session = self._getTracksSession()
        return session.query(model).all()

#___________________________________________________________________________________________________ _getTrackSeries
    @classmethod
    def _getTrackSeries(cls, sitemap):
        """_getTrackSeries doc..."""
        series  = dict()
        model   = Tracks_Track.MASTER
        column  = getattr(model, TrackPropEnum.SOURCE_FLAGS.name)
        result  = sitemap.getTracksQuery().filter(
            column.op('&')(SourceFlagsEnum.COMPLETED) == 1).all()

        for track in result:
            fingerprint = track.trackSeriesFingerprint
            if not fingerprint in series:
                series[fingerprint] = TrackSeries(sitemap=sitemap)
                series[fingerprint].tracks.append(track)

        for n, s in DictUtils.iter(series):
            s.sort()

        return series

#___________________________________________________________________________________________________ _getTrackways
    @classmethod
    def _getTrackways(cls, sitemap):
        """_getTrackways doc..."""

        trackways = dict()
        for name, series in DictUtils.iter(cls._getTrackSeries(sitemap)):
            firstTrack = series.tracks[0]
            fingerprint = firstTrack.trackwayFingerprint
            if fingerprint not in trackways:
                trackways[fingerprint] = Trackway(sitemap=sitemap, fingerprint=fingerprint)
            if not trackways[fingerprint].addSeries(series, allowReplace=False):
                raise ValueError('Ambiguous track series encountered in trackway %s' % fingerprint)

        return trackways

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

