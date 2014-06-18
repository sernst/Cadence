# TrackExporter.py
# (C)2014
# Scott Ernst

from pyaid.debug.Logger import Logger
from pyaid.json.JSON import JSON

from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
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

        for trackStore in session.query(storeModel).all():
            track = trackStore.getMatchingTrack(session)
            if track is None:
                results.append({'uid':trackStore.uid, 'action':self.DELETED_IDENTIFIER})
            else:
                diff = trackStore.toDiffDict(track.toDict())
                if diff is not None:
                    results.append(diff)

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
                u'PATH: ' + unicode(self.path)], err)
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
