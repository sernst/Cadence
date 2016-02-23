# TrackwayManager.py
# (C)2012-2014
# Kent A. Stevens and Scott Ernst

from __future__ import\
    print_function, absolute_import, unicode_literals, division

import nimble
from nimble import cmds
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager

from cadence.config import CadenceConfigs
from cadence.enums.TrackPropEnum import TrackPropEnum
from cadence.enums.SourceFlagsEnum import SourceFlagsEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.util.maya.MayaUtils import MayaUtils
from cadence.mayan.trackway import GetSelectedUidList
from cadence.mayan.trackway import GetUidList
from cadence.mayan.trackway import GetTrackNodeData
from cadence.mayan.trackway import SetNodeDatum
from cadence.mayan.trackway import SetNodeLinks
from cadence.mayan.trackway import CreateProxyNode
#_______________________________________________________________________________
class TrackwayManager(object):
    """ This class provides access to the database and to the Maya scene. Tracks
        in Maya are represented by track nodes, each a transform node with an
        additional attribute specifying the UID of that track.  The transform's
        scale, position, and rotation (about Y) are used to intrinsically
        represent track dimensions, position, and orientation.  Track models are
        accessed by query based on the UID, and for a given session. """

#===============================================================================
#                                                                     C L A S S
# RESOURCE_FOLDER_PREFIX = ['tools']

    LAYER_SUFFIX = '_Trackway_Layer'
    PATH_LAYER   = 'Track_Path_Layer'
    FIT_FACTOR   = 0.4
    CADENCE_CAM  = 'CadenceCam'

#_______________________________________________________________________________
    def __init__(self):
        self._session = None

#===============================================================================
#                                                                   P U B L I C
#
#_______________________________________________________________________________
    def getUidList(self):
        """ Returns a list of the UIDs of all track nodes currently loaded into
            Maya. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetUidList, runInMaya=True)

        # and check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed UID Query',
                'Unable to get UID list from Maya',
                'Error')
            self.closeSession()
            return None

        self.closeSession()
        return result.payload['uidList']

#_______________________________________________________________________________
    def getAllTracksInMaya(self):
        """ Returns a list of all tracks that are currently loaded into
            Maya. """

        uidList = self.getUidList()

        # and from this list of UIDs, compile the corresponding list of track
        # instances
        tracks  = []
        for uid in uidList:
            tracks.append(self.getTrackByUid(uid))

        print('length of tracks from getAllTracksInMaya = %s' % len(tracks))

        self.closeSession()
        return tracks if len(tracks) > 0 else None

#_______________________________________________________________________________
    def getCompletedTracks(self, completed =True, uidList =None):
        """ Returns a list of all tracks within the scene that are either
            completed or incomplete, depending on the boolean kwarg. """

        if not uidList:
            uidList = self.getUidList()

        # given a list of UIDs of those track currently in the Maya scene,
        # determine which are completed (or incomplete, depending on the
        # boolean), and return those as a list of tracks
        return self.getFlaggedTracks(
            uidList, SourceFlagsEnum.COMPLETED, completed)

#_______________________________________________________________________________
    def getFirstTrack(self):
        """ Returns the track model corresponding to the first track in a
            series, based on a given selection of one or more track nodes. """

        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[0]
        p = self.getPreviousTrack(t)

        while p is not None:
            t = p
            p = self.getPreviousTrack(p)

        return t

#_______________________________________________________________________________
    def getFirstSelectedTrack(self):
        """ Returns the track model corresponding to the first of a series of
            selected nodes. """

        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[0]
        p = self.getPreviousTrack(t)

        while p in selectedTracks:
            t = p
            p = self.getPreviousTrack(p)

        return t

#_______________________________________________________________________________
    def getFlaggedTracks(self, uidList, flag, set=True):
        """ Creates a list of all tracks that have a given source flag either
            set or cleared, based on the boolean argument set. """

        model   = Tracks_Track.MASTER
        state   = flag if set else 0
        size    = 200
        iMax    = len(uidList)/size
        i       = 0
        entries = []

        session = self._getSession()
        while i < iMax:
            query   = session.query(model)
            batch   = uidList[i*size : (i + 1)*size]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.sourceFlags.op('&')(flag) == state)
            entries += query.all()
            i       += 1

        if i*size < len(uidList):
            query   = session.query(model)
            batch   = uidList[i*size :]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.sourceFlags.op('&')(flag) == state)
            entries += query.all()

        self.closeSession(commit=False)

        return entries if len(entries) > 0 else None

#_______________________________________________________________________________
    def getLastTrack(self):
        """ Returns the track model corresponding to the last track in a
            series. """

        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[-1]
        n = self.getNextTrack(t)

        while n is not None:
            t = n
            n = self.getNextTrack(n)
        return t

#_______________________________________________________________________________
    def getLastSelectedTrack(self):
        """ Returns the track model corresponding to the last of a series of
            selected nodes. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[-1]
        n = self.getNextTrack(t)
        while n in selectedTracks:
            t = n
            n = self.getNextTrack(n)
        return t

#_______________________________________________________________________________
    def getMarkedTracks(self, marked =True):
        """ Returns a list of all tracks with the MARKED flag set. """

        uidList = self.getUidList()
        tracks = self.getFlaggedTracks(uidList, SourceFlagsEnum.MARKED, marked)

        return tracks

#_______________________________________________________________________________
    def getNextTrack(self, track):
        """ This method just encapsulates the session getter. """

        return track.getNextTrack(self._getSession())

#_______________________________________________________________________________
    def getPreviousTrack(self, track):
        """ This method just encapsulates the session getter. """

        return track.getPreviousTrack(self._getSession())

# ______________________________________________________________________________
    def getSelectedTracks(self):
        """ This returns a list of track model instances corresponding to the
            track nodes that are currently selected.  To achieve this, it first
            runs a remote script to get a list of track UIDs from the selected
            Maya track nodes. A list of the corresponding track models is then
            returned. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetSelectedUidList, runInMaya=True)

        # Check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed UID Query',
                'Unable to get selected UID list from Maya',
                'Error')
            return None

        # from this UID list, create the corresponding track list
        selectedUidList = result.payload['selectedUidList']
        if len(selectedUidList) == 0:
            return None

        tracks = []
        for uid in selectedUidList:
            track = self.getTrackByUid(uid)
            track.updateFromNode()
            tracks.append(track)
        return tracks

#_______________________________________________________________________________
    def getSiteMap(self, index):
        """ If the track site specified by the given index is valid, a
            Tracks_TrackSite instance is returned, otherwise None. """

        model   = Tracks_SiteMap.MASTER
        session = self._getSession()
        siteMap = session.query(model).filter(model.index == index).first()

        # close this session to release the database lock
        session.close()

        # an indicator that the siteMap table is not yet populated for this
        # index, check the scale
        if not siteMap or siteMap.scale == 0:
            return None
        else:
            return siteMap

#_______________________________________________________________________________
    def getTrackByUid(self, uid):
        """ This gets the track model instance corresponding to a given uid. """

        model = Tracks_Track.MASTER
        return model.getByUid(uid, self._getSession())

#_______________________________________________________________________________
    def getTracksByProperties(self, **kwargs):
        """ This gets the track model instances with specified properties. """

        model = Tracks_Track.MASTER
        return model.getByProperties(self._getSession(), **kwargs)

#_______________________________________________________________________________
    def getTrackByName(self, name, **kwargs):
        """ This gets the track model instance by name (plus trackway
            properties). """

        model = Tracks_Track.MASTER
        return model.getByName(name, self._getSession(), **kwargs)

#_______________________________________________________________________________
    def getTrackNode(self, track):
        """ This gets the (transient) Maya node name corresponding to a given
            track, or returns None if that track has not yet been loaded into
            Maya as a node. """

        # if asking for nothing, then get nothing in return
        if track is None:
            return None

        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            GetTrackNodeData,
            uid=track.uid,
            nodeName=track.nodeName,
            runInMaya=True)

        if result.payload.get('error'):
            print('Error in getTrackNode:', result.payload.get('message'))
            return False

        return result.payload.get('nodeName')

#_______________________________________________________________________________
    def getTrackSetNode(cls):
        """ This is redundant with the version in TrackSceneUtils, but running
            locally. Note that if no TrackSetNode is found, it does not create
            one. """

        for node in cmds.ls(exactType='objectSet'):
            if node == CadenceConfigs.TRACKWAY_SET_NODE_NAME:
                return node

        return None

#_______________________________________________________________________________
    def getTracksAfter(self, track):
        """ This returns all tracks that are subsequent to a given specified
            track. If track is the last track in the series (or an isolated
            track), it returns None, rather than the empty list. """

        track = self.getNextTrack(track)

        if not track:
            return None

        tracks = []
        while track:
            tracks.append(track)
            track = self.getNextTrack(track)

        return tracks

#_______________________________________________________________________________
    def getTracksBefore(self, track):
        """ This returns all tracks that are before a given specified track.  If
            track is the first track in the series (or an isolated track), it
            returns None, rather than the empty list. """

        track = self.getPreviousTrack(track)

        if not track:
            return None

        tracks = []
        while track:
            tracks.append(track)
            track = self.getPreviousTrack(track)

        return tracks

 #______________________________________________________________________________
    def getTrackSeries(self, track):
        """ Compiles and returns a list of all tracks from the first track
            through to the last. """

        if not track:
            return None

        series = []

        tracksBefore = self.getTracksBefore(track)
        if tracksBefore:
            series.extend(tracksBefore)

        series.append(track)

        tracksAfter = self.getTracksAfter(track)
        if tracksAfter:
            series.extend(tracksAfter)

        return series

#_______________________________________________________________________________
    def getTrackway(self, trackwayName, uidList =None):
        """ Creates a list of all tracks that have Maya tracknodes (hence are in
            the uidList) and have the specified trackwayName (trackway type and
            trackway number). """

        model   = Tracks_Track.MASTER
        size    = 200
        iMax    = len(uidList)/size
        i       = 0
        tracks  = []
        type    = trackwayName[0]
        number  = trackwayName[1:]

        if not uidList:
            uidList = self.getUidList()

        session = self._getSession()
        while i < iMax:
            query   = session.query(model)
            batch   = uidList[i*size : (i + 1)*size]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.trackwayType == type)
            query   = query.filter(model.trackwayNumber == number)
            tracks += query.all()
            i       += 1

        if i*size < len(uidList):
            query   = session.query(model)
            batch   = uidList[i*size :]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.trackwayType == type)
            query   = query.filter(model.trackwayNumber == number)
            tracks += query.all()

        self.closeSession(commit=False)
        return tracks if len(tracks) > 0 else None

#_______________________________________________________________________________
    def getTrackwayNames(self, site, level):
        """ Compiles a list of the names of trackways for a specified
            site/level/sector. In some tracksites, for some levels, a given
            trackway name (such as S1) may appear in two sectors. Hence it is
            necessary to fully qualify the trackway name with site, level, and
            sector. """

        props = { TrackPropEnum.SITE.name:site, TrackPropEnum.LEVEL.name:level }

        # now get all tracks in this trackway (that share this combination of
        # site and level)
        tracks = self.getTracksByProperties(**props)

        # that list of track instances will be used to compile all trackway
        # names (with duplicates)
        trackwayNames = []
        for track in tracks:
            trackwayName = '%s%s' % (track.trackwayType, track.trackwayNumber)
            trackwayNames.append(trackwayName)

        # remove the duplicates, sort 'em and return 'em
        trackwayNames = list(set(trackwayNames))
        trackwayNames.sort()

        return trackwayNames if len(trackwayNames) > 0 else None

#_______________________________________________________________________________
    def getTrackwayProps(self, track):
        """ Returns a dictionary of trackway properties associated with a given
            track. """

        props = { TrackPropEnum.SITE.name:track.site,
                  TrackPropEnum.LEVEL.name:track.level,
                  TrackPropEnum.YEAR.name:track.year,
                  TrackPropEnum.SECTOR.name:track.sector }
        return props

#_______________________________________________________________________________
    def selectAllTracks(self):
        """ All tracks are selected, by accumulating a list of all track nodes
            in the trackway layers. """

        layers = cmds.ls( type='displayLayer')
        nodes  = []
        for layer in layers:
            if layer.endswith(self.LAYER_SUFFIX):
               nodes.extend(cmds.editDisplayLayerMembers(
                   layer, query=True, noRecurse=True))
        cmds.select(nodes)

#_______________________________________________________________________________
    def selectTrack(self, track, setFocus =True):
        """ Select the node corresponding to this track model instance, then
            focus the camera upon this node. """

        if track:
            cmds.select(self.getTrackNode(track))
            if setFocus:
                self.setCameraFocus()
        else:
            cmds.select(clear=True)

#_______________________________________________________________________________
    def selectTracks(self, tracks):
        """ Given a list of tracks, first compiles a list of track nodes then
            has Maya select them. """

        nodes= []
        for t in tracks:
            nodes.append(self.getTrackNode(t))

        # and pass that list to Maya to be selected
        if len(nodes) > 0:
            cmds.select(nodes)

#_______________________________________________________________________________
    def selectSeriesAfter(self, track):
        """ Selects all tracks in a sequence after a given specific track. """
        tracks = self.getTracksAfter(track)


        if tracks:
            self.selectTracks(tracks)

#_______________________________________________________________________________
    def selectSeriesBefore(self, track):
        """ Selects all tracks in a sequence up to (but not including) a given
            specific track. """

        tracks = self.getTracksBefore(track)

        if track:
            self.selectTracks(tracks)
#_______________________________________________________________________________
    def selectTrackSeries(self, track):
        """ Select all the tracks in the series from first to last for a given
            track. """

        tracks = self.getTrackSeries(track)

        if tracks:
            self.selectTracks(tracks)


#===============================================================================
#                                                 N O D E   O P E R A T I O N S
#
#_______________________________________________________________________________
    def setNodeDatum(self, tracks):
        """ For each track, compute some value that will be associated with the
            'datum' attribute of its corresponding node. A list of (node, value)
             pairs will be passed, where the node is the actual Maya node name
             (string). """

        nodeValuePairs = list()

        if not tracks:
            return

        for track in tracks:
            node  = self.getTrackNode(track)
            value = track.width - track.widthMeasured
            nodeValuePairs.append((node, value))

        # now send them off to be linked up by the remote module
        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            SetNodeDatum,
            nodeValuePairs=nodeValuePairs,
            runInMaya=True)

        # Check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed in setNodeDatum',
                'Unable to add datum values to specified track nodes',
                'Error')
            return None

#_______________________________________________________________________________
    def setNodeLinks(self, tracks):
        """ For each track in the specified list of tracks, its previous and
            next tracks are determined, then the track nodes for these three
            tracks are bundled in a tuple (thisNode, prevNode, nextNode) and
            appended to a list of such tuples. That list is then sent to Maya to
            be remotely executed by the SetNodeLinks module. """

        # start a list of tuples, each specifying a node and its prev and next
        # nodes
        nodeLinks = list()

        if not tracks:
            return

        for track in tracks:
            thisNode = self.getTrackNode(track)

            prevTrack = self.getPreviousTrack(track)
            prevNode  = self.getTrackNode(prevTrack) if prevTrack else None

            nextTrack = self.getNextTrack(track)
            nextNode  = self.getTrackNode(nextTrack) if nextTrack else None

            nodeLinks.append((thisNode, prevNode, nextNode))

        # now send them off to be linked up by the remote module
        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            SetNodeLinks,
            nodeLinks=nodeLinks,
            runInMaya=True)

        # Check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed in setNodeLinks',
                'Unable to add prev and next links to specified track nodes',
                'Error')
            return None


#===============================================================================
#                                                P R O X Y  O P E R A T I O N S
#
#_______________________________________________________________________________
    def createProxyNode(self, props):
        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            CreateProxyNode, runInMaya=False, props=props)

#===============================================================================
#                                               C U R V E S   A N D   P A T H S
#
#_______________________________________________________________________________
    def addPath(self, tracks, degree =1):
        """ Creates a list of the (x, z) track coordinates in a scene from a
            given track series. The hidden tracks are not included, nor are
            tracks that are still at the origin. The path is specified as a list
            of 3D points, with the y coordinate zeroed out."""

        path = []
        for track in tracks:
            if not track.hidden and track.x != 0.0 and track.z != 0.0:
                path.append((track.x, 0.0, track.z))

        curve = cmds.curve(point=path, degree=degree)

        layer = self.PATH_LAYER

        self.createLayer(layer)
        cmds.editDisplayLayerMembers(layer, curve, noRecurse=True)

#_______________________________________________________________________________
    def deleteAllPaths(self):
        """ Deletes all curves that have been placed in the PATH_LAYER. """
        curves = cmds.editDisplayLayerMembers(
            self.PATH_LAYER, query=True, noRecurse=True)
        for curve in curves:
            cmds.delete(curve)
        cmds.delete(self.PATH_LAYER)


#===============================================================================
#                                             C A M E R A   O P E R A T I O N S
#
#_______________________________________________________________________________
    def initializeCadenceCam(self):
        """ This creates an orthographic camera that looks down the Y axis onto
            the XZ plane, and rotated so that the AI file track labels are
            legible.  This camera is positioned so that the given track nodeName
            is centered in its field by setCameraFocus. """

        if cmds.objExists(self.CADENCE_CAM):
            return

        priorSelection = MayaUtils.getSelectedTransforms()

        c = cmds.camera(
            orthographic=True,
            nearClipPlane=1,
            farClipPlane=100000,
            orthographicWidth=500)
        cmds.setAttr(c[0] + '.visibility', False)
        cmds.rename(c[0], self.CADENCE_CAM)
        cmds.rotate(-90, 180, 0)
        cmds.move(0, 100, 0, self.CADENCE_CAM, absolute=True)

        MayaUtils.setSelection(priorSelection)


#_______________________________________________________________________________
    def selectCadenceCam(self):
        """ Selects the CadenceCam. """

        cmds.lookThru(self.CADENCE_CAM)
        self.setCameraFocus()

#_______________________________________________________________________________
    def selectPerspectiveCam(self):
        """ Selects the default perspective camera. """

        cmds.lookThru('persp')
        self.setCameraFocus()

#_______________________________________________________________________________
    def getCadenceCamLocation(self):
        """ Returns the current (x, z) location of the CadenceCam. This is
            useful for placing the camera above a given track, or for snapping a
            track to the current location of the camera. """

        x = cmds.getAttr(self.CADENCE_CAM + '.translateX')
        z = cmds.getAttr(self.CADENCE_CAM + '.translateZ')

        return (x, z)
#_______________________________________________________________________________
    def setCameraFocus(self):
        """ Center the current camera (CadenceCam or persp) on the currently
            selected node. If using the CadenceCam, the view is fitted to
            FIT_FACTOR; with the persp camera, it is not so contrained. """

        cmds.viewFit(fitFactor=self.FIT_FACTOR, animate=True)

#===============================================================================
#                                 D I S P L A Y   L A Y E R   U T I L I T I E S
#
#_______________________________________________________________________________
    def initializeLayers(self):
        """ Creates a new layer for each trackway in this site and level based
            on the first UID found (returned by getUidList).  It is important to
            load into the Maya scene only trackways from a common combination of
            site, level, and sector, since a given trackway may be redundantly
            defined in different sectors for a given site and level. The list of
            trackway names is returned for the TrackwayManagerWidget to populate
            a combo box. """

        # first delete any current display layers
        layers = cmds.ls( type='displayLayer')
        for layer in layers:
            if (layer.endswith(self.LAYER_SUFFIX)):
                cmds.delete(layer)

        # get the current UID list so we can extract the site, year, sector, and
        # level information
        uidList = self.getUidList()

        if not uidList:
            return

        # we'll use the first track as representative of the site and level,
        # presumed to be in common with all tracks in this scene.
        track         = self.getTrackByUid(uidList[0])
        trackwayNames = self.getTrackwayNames(track.site, track.level)

        # then for each trackway name (such as 'S1') create a corresponding
        # layer with the LAYER_SUFFIX, then populate it with the track nodes of
        # the tracks comprising that trackway
        for trackwayName in trackwayNames:
            layer = '%s%s' % (trackwayName, self.LAYER_SUFFIX)

            # then make the layer
            self.createLayer(layer)

            # get a list of tracks for this trackway (filtering on site, level,
            # sector and name)
            trackway = self.getTrackway(trackwayName, uidList)
            if trackway and len(trackway) > 0:
                self.addTrackwayToLayer(layer, trackway)

        return trackwayNames

#_______________________________________________________________________________
    def addTrackwayToLayer(self, layer, tracks):
        """ Populates the specified display layer with the track nodes
            corresponding to the specified tracks. """

        nodes = []
        for track in tracks:
            trackNode = self.getTrackNode(track)
            if trackNode:
                nodes.append(trackNode)

        if len(nodes) == 0:
            return

        # now add those nodes to the layer
        cmds.editDisplayLayerMembers(layer, nodes, noRecurse=True)

#_______________________________________________________________________________
    def createLayer(self, layer, useExisting =True):
        """ Creates a display layer with the specified name. """

        if useExisting and cmds.objExists(layer):
            return

        # Since nothing should be selected when creating a new display layer,
        # save selection
        priorSelection = MayaUtils.getSelectedTransforms()

        cmds.select(clear=True)
        cmds.createDisplayLayer(name=layer)

        #  Restore the prior state of selection
        MayaUtils.setSelection(priorSelection)

#_______________________________________________________________________________
    def selectTracksInLayer(self, layer):
        """ A fast way to select the track nodes within a given layer. """

        nodes = cmds.editDisplayLayerMembers(layer, query=True, noRecurse=True)
        cmds.select(nodes)

#_______________________________________________________________________________

        nodes = cmds.editDisplayLayerMembers(layer, query=True, noRecurse=True)
        cmds.select(nodes)
#_______________________________________________________________________________
    def deleteLayer(self, layer):
        """ Deletes a display layer. """

        if not cmds.objExists(layer):
            cmds.delete(layer)

#_______________________________________________________________________________
    def setAllLayersVisible(self, visible):
        """ This sets all layers visible, as the name suggests. """

        layers = cmds.ls( type='displayLayer')

        for layer in layers:
            if layer.endswith(self.LAYER_SUFFIX):
                cmds.setAttr('%s.visibility' % layer, visible)

#_______________________________________________________________________________
    def showTrackway(self, trackwayName, visible =True):
        """ Presuming that the track nodes for a specified trackway are already
            in a corresponding layer, this turns on visibility of that
            layer. """

        layer = trackwayName + self.LAYER_SUFFIX

        # then set that layer either visible or invisible according to the kwarg
        cmds.setAttr('%s.visibility' % layer, visible)


#_______________________________________________________________________________
    def closeSession(self, commit =True):
        """ Closes a session and indicates such by nulling out model and
            session.  This is public because the TrackwayManagerWidget needs to
            call it."""

        session = self._session
        self._session = None

        if session:
            if commit:
                session.commit()
            session.close()

        return bool(session is not None)

#===============================================================================
#                                                                 P R I V A T E
#
#_______________________________________________________________________________
    def _getSession(self):
        """ Access to model instances is based on the current model and session,
            stored in two local instance variables so that multiple operations
            can be performed before closing this given session. """

        if self._session is not None:
            return self._session

        self._session = Tracks_Track.MASTER.createSession()
        return self._session