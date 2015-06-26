# Tracks_Track.py
# (C)2013-2015
# Scott Ernst and Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division

import nimble

from cadence.enums.SourceFlagsEnum import SourceFlagsEnum
from cadence.mayan.trackway import GetTrackNodeData
from cadence.mayan.trackway import UpdateTrackNode
from cadence.mayan.trackway import CreateTrackNode
from cadence.models.tracks.TracksTrackDefault import TracksTrackDefault


# AS NEEDED: from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
# AS NEEDED: from cadence.models.analysis.Analysis_Track import Analysis_Track

#___________________________________________________________________________________________________ Tracks_Track
# noinspection PyAttributeOutsideInit
class Tracks_Track(TracksTrackDefault):
    """ Database model representation of a track with all the attributes and information for a
        specific track as well connectivity information for the track within its series. """

#===================================================================================================
#                                                                                       C L A S S

    __tablename__  = 'tracks'

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: nodeName
    @property
    def nodeName(self):
        """ A cached value for the name of the Maya nodeName representing this track if one exists,
            which is updated each time a create/update operation on the nodeName occurs. Can be
            incorrect if the nodeName was renamed between such operations. """

        return self.fetchTransient('nodeName')
    @nodeName.setter
    def nodeName(self, value):
        self.putTransient('nodeName', value)

#___________________________________________________________________________________________________ GS: completed
    @property
    def completed(self):
        """ Getter returns a boolean indicating whether the 'completed' source flag is set. """
        flags = self.sourceFlags & ~SourceFlagsEnum.COMPLETED

        return SourceFlagsEnum.get(flags, SourceFlagsEnum.COMPLETED)
    @completed.setter
    def completed(self, value):
        """ Setter sets or clears the 'completed' source flag, depending on the boolean value. """
        # preserve the state of any other flags
        flags = self.sourceFlags & ~SourceFlagsEnum.COMPLETED

        if value:
            self.sourceFlags = SourceFlagsEnum.set(flags, SourceFlagsEnum.COMPLETED)
        else:
            self.sourceFlags = SourceFlagsEnum.clear(flags, SourceFlagsEnum.COMPLETED)

#___________________________________________________________________________________________________ GS: locked
    @property
    def locked(self):
        """ Getter returns a boolean indicating whether the 'locked' source flag is set. """
        flags = self.sourceFlags & ~SourceFlagsEnum.LOCKED
        return SourceFlagsEnum.get(flags, SourceFlagsEnum.LOCKED)
    @locked.setter
    def locked(self, value):
        """ Setter sets or clears the 'locked' source flag, depending on the boolean value. """
        # preserve the state of any other flags
        flags = self.sourceFlags & ~SourceFlagsEnum.LOCKED

        if value:
            self.sourceFlags = SourceFlagsEnum.set(flags, SourceFlagsEnum.LOCKED)
        else:
            self.sourceFlags = SourceFlagsEnum.clear(flags, SourceFlagsEnum.LOCKED)

#___________________________________________________________________________________________________ GS: marked
    @property
    def marked(self):
        """ Getter returns a boolean indicating whether the 'marked' source flag is set. """
        flags = self.sourceFlags & ~SourceFlagsEnum.MARKED
        return SourceFlagsEnum.get(flags, SourceFlagsEnum.MARKED)
    @marked.setter
    def marked(self, value):
        """ Setter sets or clears the 'marked' source flag, depending on the boolean value. """
        # preserve the state of any other flags
        flags = self.sourceFlags & ~SourceFlagsEnum.MARKED

        if value:
            self.sourceFlags = SourceFlagsEnum.set(flags, SourceFlagsEnum.MARKED)
        else:
            self.sourceFlags = SourceFlagsEnum.clear(flags, SourceFlagsEnum.MARKED)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ createTrackNode
    def createTrackNode(self):
        """ Create a visual representation of a track, to signify the position, dimensions (length
            and width), and rotation of either a manus or pes track.  The representation has
            basic dimensions of one meter so that the scale in x and z equates to the width and
            length of the manus or pes in fractional meters (e.g., 0.5 = 50 cm).  The node is
            prohibited from changing in y (elevation) or to rotate about either x or z. """

        conn = nimble.getConnection()
        out  = conn.runPythonModule(
            CreateTrackNode,
            uid=self.uid,
            props=self.toMayaNodeDict(),
            runInMaya=True)
        if not out.success:
            print('Error in CreateNode:', out.error)
            return None

        self.nodeName = out.payload.get('nodeName')

        return self.nodeName

#___________________________________________________________________________________________________ updateNode
    def updateNode(self):
        """ Sends values to Maya nodeName representation of the track to synchronize the values in
            the model and the nodeName. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            UpdateTrackNode,
            uid=self.uid,
            props=self.toMayaNodeDict(),
            runInMaya=True)
        if not result.success:
            return False

        self.nodeName = result.payload.get('nodeName')
        return True

#___________________________________________________________________________________________________ updateFromNode
    def updateFromNode(self):
        """ Retrieves Maya values from the nodeName representation of the track and updates this
            model instance with those values. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            GetTrackNodeData,
            uid=self.uid,
            nodeName=self.nodeName,
            runInMaya=True)
        if result.payload.get('error'):
            print('Error in updateFromNode:', result.payload.get('message'))
            return False

        self.nodeName = result.payload.get('nodeName')

        if self.nodeName:
            self.fromDict(result.payload.get('props'))
            return True

        return False

#___________________________________________________________________________________________________ mergeToStorage
    def mergeToStorage(self, session):
        store = self.getMatchingTrackStore(session)
        if not store:
            return False

        store.fromDict(self.toDict())
        return True

#___________________________________________________________________________________________________ getMatchingTrack
    def getMatchingTrackStore(self, session):
        """ Returns the Tracks_Track instance that corresponds to this Tracks_TrackStore instance
            if such an instance exists. """

        from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
        model  = Tracks_TrackStore.MASTER
        result = session.query(model).filter(model.uid == self.uid).all()
        return result[0] if result else None

#___________________________________________________________________________________________________ removeTracksByUid
    @classmethod
    def removeTracksByUid(cls, uid, session, analysisSession):
        """removeTrackByUid doc..."""
        model = cls.MASTER
        tracks = session.query(model).filter(model.uid == uid).all()
        if not tracks:
            return []

        for track in tracks:
            cls.removeTrack(track, analysisSession)
        return tracks

#___________________________________________________________________________________________________ removeTrack
    @classmethod
    def removeTrack(cls, track, analysisSession):
        """removeTrack doc..."""
        session = track.mySession
        analysisTrack = track.getAnalysisPair(analysisSession)

        if analysisTrack:
            analysisSession.delete(analysisTrack)

        from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
        storeModel = Tracks_TrackStore.MASTER
        for store in session.query(storeModel).filter(storeModel.uid == track.uid).all():
            session.delete(store)

        session.delete(track)


#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getAnalysisPair
    def _getAnalysisPair(self, session, createIfMissing):
        """_getAnalysisPair doc..."""

        from cadence.models.analysis.Analysis_Track import Analysis_Track
        model = Analysis_Track.MASTER

        result = session.query(model).filter(model.uid == self.uid).first()

        if createIfMissing and not result:
            result = model()
            result.uid = self.uid
            session.add(result)
            session.flush()

        return result
