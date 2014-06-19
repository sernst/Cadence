# TrackExporter.py
# (C)2014
# Scott Ernst

from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.json.JSON import JSON
from pyaid.number.NumericUtils import NumericUtils

from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore

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
    def process(self, session):
        """Doc..."""

        if self.results is not None:
            return True

        results = []
        storeModel = Tracks_TrackStore.MASTER

        if session is None:
            session = storeModel.createSession()

        trackStores = session.query(storeModel).all()
        index = 0
        indices = NumericUtils.linearSpace(0, len(trackStores), roundToIntegers=True)[1:]

        for trackStore in trackStores:
            track = trackStore.getMatchingTrack(session)
            if track is None:
                print 'TRACK IS NONE'
                self.modifications += 1
                results.append({'uid':trackStore.uid, 'action':self.DELETED_IDENTIFIER})

                self.logger.write(
                    u'<div>DELETED: %s</div>' %  DictUtils.prettyPrint(
                        trackStore.toDict(uniqueOnly=True)))
            else:
                diff = trackStore.toDiffDict(track.toDict())
                if diff is not None:
                    self.modifications += 1
                    results.append(diff)

                    self.logger.write(
                        u'<div>MODIFIED: %s</div>' % DictUtils.prettyPrint(
                            trackStore.toDict(uniqueOnly=True)))

            index += 1
            if index in indices:
                self.logger.write(
                    u'<div style="color:#33CC33">%s%% Complete</div>' % unicode(
                        10*(indices.index(index) + 1)))

        self.logger.write(u'<div style="color:#33CC33">100% Complete</div>')

        self.results = results
        return True

#___________________________________________________________________________________________________ write
    def write(self, session, path, pretty =False, gzipped =True):
        if self.results is None and not self.process(session):
            return False

        try:
            JSON.toFile(path, self.results, pretty=pretty, gzipped=gzipped, throwError=True)
            return True
        except Exception, err:
            self.logger.writeError([
                u'ERROR: Unable to write export file',
                u'PATH: ' + unicode(path)], err)
            return False

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
