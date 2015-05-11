# Tracks_TrackStore.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.dict.DictUtils import DictUtils

from cadence.models.tracks.TracksTrackDefault import TracksTrackDefault


# AS NEEDED: from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ Tracks_TrackStore
class Tracks_TrackStore(TracksTrackDefault):
    """ Database model representation of a track with all the attributes and information for a
        specific track as well as a connectivity information for the track within its series. """

#===================================================================================================
#                                                                                       C L A S S

    __tablename__  = u'trackStores'

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ toDiffDict
    def toDiffDict(self, comparison):
        """ Compares the dictionary of properties against the properties of this track store
            instance and returns a dictionary of only the properties that differ. This is used
            to export changes made in a database to serial format for storage. """

        out = dict()
        for key,value in DictUtils.iter(comparison):
            if getattr(self, key, value) != value:
                out[key] = value

        if len(list(out.keys())) == 0:
            return None

        out['uid'] = self.uid
        return out

#___________________________________________________________________________________________________ getMatchingTrack
    def getMatchingTrack(self, session):
        """ Returns the Tracks_Track instance that corresponds to this Tracks_TrackStore instance
            if such an instance exists. """

        from cadence.models.tracks.Tracks_Track import Tracks_Track
        model  = Tracks_Track.MASTER
        result = session.query(model).filter(model.uid == self.uid).all()
        return result[0] if result else None

#___________________________________________________________________________________________________ getOrCreateMatchingTrack
    def getOrCreateMatchingTrack(self, session):
        t = self.getMatchingTrack(session)

        from cadence.models.tracks.Tracks_Track import Tracks_Track

        if t is None:
            model = Tracks_Track.MASTER
            t = model()
            t.uid = self.uid
            t.fromDict(self.toDict())
            session.add(t)
        else:
            t.fromDict(self.toDiffDict(t.toDict()))

        return t
