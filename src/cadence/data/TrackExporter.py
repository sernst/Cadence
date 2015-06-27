# TrackExporter.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

from cadence.models.tracks.Tracks_Track import Tracks_Track


#___________________________________________________________________________________________________ TrackExporter
class TrackExporter(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    DELETED_IDENTIFIER = u'##DEL##'

#___________________________________________________________________________________________________ __init__
    def __init__(self, logger =None):
        """Creates a new instance of TrackExporter."""
        self.results = None
        self.logger = logger
        self.modifications = 0
        if not logger:
            self.logger = Logger(self, printOut=True)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ process
    def process(self, session, difference =True):
        """Doc..."""

        if self.results is not None:
            return True

        results = []
        model = Tracks_Track.MASTER

        if session is None:
            session = model.createSession()

        trackStores = session.query(model).all()
        index = 0
        indices = NumericUtils.linearSpace(0, len(trackStores), roundToIntegers=True)[1:]

        for trackStore in trackStores:
            track = trackStore.getMatchingTrack(session)
            if track is None:
                self.modifications += 1
                results.append({'uid':trackStore.uid, 'action':self.DELETED_IDENTIFIER})

                self.logger.write(
                    u'<div>DELETED: %s</div>' %  DictUtils.prettyPrint(
                        trackStore.toDict(uniqueOnly=True)))
            else:
                if difference:
                    diff = trackStore.toDiffDict(track.toDict())
                    if diff is not None:
                        self.modifications += 1
                        results.append(diff)

                        self.logger.write(
                            u'<div>MODIFIED: %s</div>' % trackStore.fingerprint)
                else:
                    results.append(track.toDict())

            index += 1
            if index in indices:
                self.logger.write(
                    u'<div style="color:#33CC33">%s%% Complete</div>' % StringUtils.toUnicode(
                        10*(indices.index(index) + 1)))

        self.logger.write(u'<div style="color:#33CC33">100% Complete</div>')

        self.results = results
        return True

#___________________________________________________________________________________________________ write
    def write(self, session, path, pretty =False, gzipped =True, difference =True):
        if self.results is None and not self.process(session, difference):
            return False

        try:
            JSON.toFile(path, self.results, pretty=pretty, gzipped=gzipped, throwError=True)
            return True
        except Exception as err:
            self.logger.writeError([
                u'ERROR: Unable to write export file',
                u'PATH: ' + StringUtils.toUnicode(path)], err)
            return False

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return StringUtils.toUnicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
