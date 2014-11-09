# TrackLinkConnector.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.string.StringUtils import StringUtils

from cadence.models.tracks.Tracks_Track import Tracks_Track



#___________________________________________________________________________________________________ TrackLinkConnector
class TrackLinkConnector(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    _TRACK_NUMBER_RE = re.compile('(?P<prefix>[^0-9]*)(?P<number>[0-9]+)(?P<suffix>[^0-9]*)')

#___________________________________________________________________________________________________ __init__
    def __init__(self, logger =None):
        """Creates a new instance of TrackLinkConnector."""
        self.logger = logger
        if not logger:
            self.logger = Logger(self, printOut=True)

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
            model.site == source.site,
            model.sector == source.sector,
            model.level == source.level,
            model.trackwayType == source.trackwayType,
            model.trackwayNumber == source.trackwayNumber,
            model.pes == source.pes,
            model.left == source.left).order_by(model.number.asc()).all()

        if not trackSeries:
            return False

        #-------------------------------------------------------------------------------------------
        # TRACK ORDERING
        #       Tracks numbers are strings to support naming conventions like 10b or 12c, where the
        #       number is possibly followed by a non-numeric set of characters. To establish track
        #       ordering the sequence should be sorted primarily by the numeric sequence and
        #       secondarily by the suffix first numerically and then alphabetically respectively.

        trackNumbers = dict()
        for track in trackSeries:
            result = self._TRACK_NUMBER_RE.search(track.number)
            if not result or result.group('prefix'):
                self.logger.write([
                    u'ERROR: Unable to parse track number: ' + StringUtils.toUnicode(track.number),
                    u'TRACK: ' + DictUtils.prettyPrint(track.toDict()) ])
                continue

            number = result.group('number')
            suffix = result.group('suffix')

            if number not in trackNumbers:
                trackNumbers[number] = {'track':None, 'extras':{}, 'number':int(number)}
            entry = trackNumbers[number]

            if number == track.number and not suffix:
                entry['track'] = track
            elif not suffix:
                self.logger.write([
                    u'ERROR: Invalid track number: ' + StringUtils.toUnicode(track.number),
                    u'TRACK: ' + DictUtils.prettyPrint(track.toDict()) ])
                continue
            else:
                entry['extras'][suffix] = track

            if track not in self.operatedTracks:
                self.operatedTracks.append(track)

        prev = None
        entries = list(trackNumbers.values())
        entries.sort(key=lambda x: x['number'])
        for entry in entries:
            track = entry['track']
            tracks = [] if track is None else [track]
            for key in sorted(entry['extras']):
                tracks.append(entry['extras'][key])

            for track in tracks:
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

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
