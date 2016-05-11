# TrackwayManager.py
# (C)2012-2014
# Kent A. Stevens and Scott Ernst

from __future__ import\
    print_function, absolute_import, unicode_literals, division

import nimble
from nimble import cmds
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager

from cadence.enums.TrackPropEnum import TrackPropEnum
from cadence.enums.SourceFlagsEnum import SourceFlagsEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.util.maya.MayaUtils import MayaUtils
from cadence.mayan.trackway import GetSelectedUidList
from cadence.mayan.trackway import GetUidList
from cadence.mayan.trackway import GetTrackNodeProps
from cadence.mayan.trackway import CreateToken
from cadence.mayan.trackway import CreateTokens
from cadence.mayan.trackway import UpdateToken
from cadence.mayan.trackway import GetTokenProps
from cadence.mayan.trackway import DeleteTokens

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
    FIT_FACTOR   = 0.1
    CADENCE_CAM  = 'CadenceCam'

#_______________________________________________________________________________
    def __init__(self):
        self._session  = None

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
                parent=self,
                header='ERROR',
                message='Unable to get UID list from Maya')
            self.closeSession()
            return None

        self.closeSession()
        return result.payload['uidList']

#_______________________________________________________________________________
    def getAllTracksInMaya(self):
        """ Returns a list of all tracks are currently loaded into Maya. """

        uidList = self.getUidList()

        # compile the corresponding list of track node instances
        tracks  = list()
        for uid in uidList:
            tracks.append(self.getTrackByUid(uid))

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
        entries = list()

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
            track sequence. """

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
        """ Returns the track model corresponding to the last of a sequence of
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
        result = conn.runPythonModule(GetSelectedUidList, runInMaya=True )

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

        tracks = list()
        for uid in selectedUidList:
            track = self.getTrackByUid(uid)
            if track:
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
            GetTrackNodeProps,
            uid=track.uid,
            nodeName=track.nodeName,
            runInMaya=True)

        if result.payload.get('error'):
            print('Error in getTrackNode:', result.payload.get('message'))
            return False

        return result.payload.get('nodeName')

#_______________________________________________________________________________
    def getTracksAfter(self, track):
        """ This returns all tracks that are subsequent to a given specified
            track.  If track is the last track in the sequeunce (or an isolated
            track), it returns None, rather than the empty list. """

        track = self.getNextTrack(track)

        if not track:
            return None

        tracks = list()
        while track:
            tracks.append(track)
            track = self.getNextTrack(track)

        return tracks

#_______________________________________________________________________________
    def getTracksBefore(self, track):
        """ This returns all tracks that are before a given specified track.  If
            track is the first track in the sequence (or an isolated track), it
            returns None, rather than the empty list. """

        track = self.getPreviousTrack(track)

        if not track:
            return None

        tracks = list()
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

        series = list()

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
        tracks  = list()
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
        trackwayNames = list()
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

        props = {
            TrackPropEnum.SITE.name:track.site,
            TrackPropEnum.LEVEL.name:track.level,
            TrackPropEnum.YEAR.name:track.year,
            TrackPropEnum.SECTOR.name:track.sector }
        return props

#_______________________________________________________________________________
    def selectAllTracks(self):
        """ All tracks are selected, by accumulating a list of all track nodes
            in the trackway layers. """

        layers = cmds.ls( type='displayLayer')
        nodes  = list()
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
            node = self.getTrackNode(track)
            cmds.select(node)
            if setFocus:
                self.setCameraFocus()
        else:
            cmds.select(clear=True)

#_______________________________________________________________________________
    def selectTracks(self, tracks):
        """ Given a list of tracks, first compiles a list of track nodes then
            has Maya select them. """

        nodes = list()
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
#===============================================================================
#                                       M A Y A  T O K E N  O P E R A T I O N S
#
#_______________________________________________________________________________
    def createToken(self, props):
        """ Create a token in Maya, using the uid and properties specified in
            the dictionary props. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            CreateToken,
            uid=props['uid'],
            props=props,
            runInMaya=True)

        if result.payload.get('error'):
            print('Error in createToken:', result.payload.get('message'))
            return False

#_______________________________________________________________________________
    def createTokens(self, propsList):
        """ Create tokens in Maya, each based on the properties specified by a
            corresponding dictionary props within the list propsList. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            CreateTokens,
            propsList=propsList,
            runInMaya=True)

        if result.payload.get('error'):
            print('Error in createTokens:', result.payload.get('message'))
            return False

# ______________________________________________________________________________
    def getSelectedTokenUids(self):
        """ This returns a list of URL of the currently selected tokens, or
            None. """

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

        selectedUidList = result.payload['selectedUidList']
        if len(selectedUidList) == 0:
            return None

        # return those UIDs corresponding to proxies or tokens
        tokenUidList = list()
        for uid in selectedUidList:
            if uid.endswith('_proxy') or uid.endswith('_token'):
                tokenUidList.append(uid)

        return tokenUidList

# ______________________________________________________________________________
    def getSelectedTokenUid(self):
        """ This returns the URL of the currently selected token, or None. """

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

        selectedUidList = result.payload['selectedUidList']
        if len(selectedUidList) == 0:
            return None

        # check to see if it really is a proxy or token that was selected
        uid = selectedUidList[0]
        if uid.endswith('_proxy') or uid.endswith('_token'):
            return uid
        else:
            return None

#_______________________________________________________________________________
    def getTokenNodeName(self, uid):
        """ This gets the name of the token (i.e., the string name of the
            transform node for a specified UID string). It returns None if that
            token is not found. """

        # if asking for nothing, then get nothing in return
        if uid is None:
            return None

        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetTokenProps, uid=uid, runInMaya=True)

        if result.payload.get('error'):
            print('Error in getTokenNodeName:', result.payload.get('message'))
            return False

        return result.payload.get('nodeName')

#_______________________________________________________________________________
    def getTokenProps(self, uid):
        """ This returns a dictionary of properties from the Maya token
            specified by the uid, or an error if it does not exist.  This
            function treats a token and a track node as equivalent. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetTokenProps, uid=uid, runInMaya=True)

        if result.payload.get('error'):
            print('Error in getTokenProps:', result.payload.get('message'))
            return False

        return result.payload.get('props')

#_______________________________________________________________________________
    def setTokenProps(self, uid, props):
        """ This sets the attributes in the Maya token based on the properties
            of the props dictionary that is passed. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            UpdateToken,
            uid=uid,
            props=props,
            runInMaya=True)

        return result.success

#_______________________________________________________________________________
    def refreshTokens(self, uidList, scenario):
        """ The tokens associated with a list of UIDs are updated. """

        for uid in uidList:
            props = scenario.getProps(uid=uid)
            self.setTokenProps(uid, props)

#_______________________________________________________________________________
    def refreshAllTokens(self, scenario):
        """ This updates the token for every UID in the scenario. """

        entries = scenario.getEntries()
        for entry in entries:
            uid = entry['uid']
            self.setTokenProps(uid, entry)

#_______________________________________________________________________________
    def deleteToken(self, uid):
        """ This looks up the token or proxy corresponding to the uid, then
        deletes it.  """

        node = self.getTokenNodeName(uid)
        if node:
            cmds.delete(node)
            number = node.split('_')[1]
            if number:
                annotation = 'TokenAnnotation_' + number
                cmds.delete(annotation)

#_______________________________________________________________________________
    def deleteTokens(self):
        """ This sets the attributes in the Maya token based on the properties
            of the props dictionary that is passed. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(DeleteTokens, runInMaya=True)

        return result.success

#_______________________________________________________________________________
    def updateScenario(self, scenario):
        """ The properties of each scenario entry are set to the values pulled
            from the corresponding Maya token. """

        if not scenario:
            return

        for limb in ['lp', 'rp', 'lm', 'rm']:
            for entry in scenario.entries[limb]:
                if entry:
                    uid = entry['uid']
                    scenario.setProps(uid, self.getTokenProps(uid))

#_______________________________________________________________________________
    def selectToken(self, uid, setFocus =True, closeup =True):
        """ Select the node corresponding to this UID, then focusses the camera
            upon that node. """

        node = self.getTokenNodeName(uid)

        if not node:
            return

        cmds.select(node)
        if setFocus:
            self.setCameraFocus(closeup)

#===============================================================================
#                                               C U R V E S   A N D   P A T H S
#
#_______________________________________________________________________________
    def addPath(self, tracks, degree =1):
        """ Creates a list of the (x, z) track coordinates in a scene from a
            given track series. The hidden tracks are not included, nor are
            tracks that are still at the origin. The path is specified as a list
            of 3D points, with the y coordinate zeroed out."""

        path = list()
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
            orthographicWidth=400)
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
    def setCameraFocus(self, closeup =True):
        """ Center the current camera (CadenceCam or persp) on the currently
            selected node. If using the CadenceCam, the view is fitted to
            FIT_FACTOR; with the persp camera, it is not so contrained. """

        if closeup:

            # compute size (in cm)
            dimensions = cmds.exactWorldBoundingBox()
            if not dimensions:
                return
            dx = dimensions[3] - dimensions[0]
            dy = dimensions[4] - dimensions[1]
            dz = dimensions[5] - dimensions[2]
            size = max(dx, dy, dz)

            # make FitFactor such that a 100 CM object would fill 25% of screen
            fitFactor = 0.25*size/100.0
            cmds.viewFit(fitFactor=fitFactor, animate=True)

        else:
            cmds.viewLookAt(())


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

        nodes = list()
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

        priorSelection = MayaUtils.getSelectedTransforms()
        cmds.select(clear=True)
        cmds.createDisplayLayer(name=layer)
        MayaUtils.setSelection(priorSelection)

#_______________________________________________________________________________
    def selectTracksInLayer(self, layer):
        """ A fast way to select the track nodes within a given layer. """

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
        """ Presuming the track nodes for a specified trackway are already in a
            corresponding layer, this turns on visibility of that layer. """

        layer = trackwayName + self.LAYER_SUFFIX

        # then set that layer either visible or invisible according to the kwarg
        cmds.setAttr('%s.visibility' % layer, visible)

#_______________________________________________________________________________
    def closeSession(self, commit =True):
        """ Closes a session (and indicates this by nulling out session).  This
            is public because the TrackwayManagerWidget needs to call it."""

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