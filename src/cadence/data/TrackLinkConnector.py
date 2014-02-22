# TrackLinkConnector.py
# (C)2014
# Scott Ernst

#___________________________________________________________________________________________________ TrackLinkConnector
from cadence.models.tracks.Tracks_Track import Tracks_Track


class TrackLinkConnector(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        """Creates a new instance of TrackLinkConnector."""
        self.searchNext         = True
        self.searchPrev         = True
        self.overrideExisting   = False
        self.operatedTracks     = []
        self.modifiedTracks     = []
        self.trackLinkages      = []

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ echoResult
    def echoResult(self):
        out = []
        for item in self.trackLinkages:
            out.append(item[0].name + ' -> ' + item[1].name)
        return u'\n'.join(out)

#___________________________________________________________________________________________________ runAll
    def runAll(self, session):
        model = Tracks_Track.MASTER
        return self.run(session.query(model).all(), session)

#___________________________________________________________________________________________________ run
    def run(self, tracks, session):
        """Doc..."""

        for track in tracks:
            if track not in self.operatedTracks:
                self._runTrack(track, session)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _runTrack
    def _runTrack(self, source, session):
        """Doc..."""

        model = source.__class__
        trackSeries = session.query(model).filter(
            model.site == source.site).filter(
            model.sector == source.sector).filter(
            model.level == source.level).filter(
            model.trackwayType == source.trackwayType).filter(
            model.trackwayNumber == source.trackwayNumber).filter(
            model.pes == source.pes).filter(
            model.left == source.left).order_by(model.number.asc()).all()

        if not trackSeries:
            return False

        self.operatedTracks += trackSeries

        prev = None
        for track in trackSeries:
            try:
                number = int(track.number)
            except Exception, err:
                continue

            if not prev:
                prev = track
                continue

            # If the previous entry has an existing next that doesn't match
            if not self.overrideExisting and prev.next and prev.next != track.uid:
                continue

            prev.next = track.uid
            self.modifiedTracks.append(prev)
            self.trackLinkages.append((prev, track))
            prev = track

#___________________________________________________________________________________________________ _linkNext
    def _linkNext(self, track):
        pass

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return unicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
