# TrackwayManagerWidget.py
# (C)2012-2014
# Scott Ernst and Kent A. Stevens

import nimble

from nimble import cmds

# from pyaid.json.JSON import JSON

from PySide import QtGui

from pyglass.widgets.PyGlassWidget import PyGlassWidget
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track

from cadence.mayan.trackway import GetSelectedUidList

#___________________________________________________________________________________________________ TrackwayManagerWidget
class TrackwayManagerWidget(PyGlassWidget):
    """ This widget is the primary GUI for interacting with the Maya scene representation of a
        trackway.  It permits selection of tracks interactively in Maya and display and editing of
        their attributes.  Tracks in Maya are represented by track nodes, each a transform nodeName
        with an additional attribute specifying the UID of that track.  The transform's scale,
        position, and rotation (about Y) are used to intrinsically represent track dimensions,
        position, and orientation.  Track models are accessed by query based on the UID, and for a
        given session. """
#===================================================================================================
#                                                                                       C L A S S
    RESOURCE_FOLDER_PREFIX = ['tools']

    SELECT_BY_NAME    = 'Select by Name'
    SELECT_BY_INDEX   = 'Select by Index'
    SELECT_ALL_BEFORE = 'Select All Before'
    SELECT_ALL_AFTER  = 'Select All After'
    SELECT_ALL        = 'Select All'

    EXTRAPOLATE_TRACK = 'Extrapolate Next Track'
    INTERPOLATE_TRACK = 'Interpolate This Track'
    LINK_SELECTED     = 'Link Selected Tracks'
    UNLINK_SELECTED   = 'Unlink Selected Tracks'
    SET_DIMENSIONS    = 'Set Dimensions of Selected'
    SET_WIDTH         = 'Set Width of Selected'
    SET_LENGTH        = 'Set Length of Selected'
    SET_THETA         = 'Set Theta of Selected'
    SET_ALL_UNC       = 'Set Uncertainties'
    SET_WIDTH_UNC     = 'Set Width Uncertainty'
    SET_LENGTH_UNC    = 'Set Length Uncertainty'
    SET_THETA_UNC     = 'Set Theta Uncertainty'

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)

        self.firstBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'first.png')))
        self.prevBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'prev.png')))
        self.nextBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'next.png')))
        self.lastBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'last.png')))

        # in Track tab:
        self.widthSbx.valueChanged.connect(self._handleWidthSbx)
        self.widthSbx.setAccelerated(True)

        self.lengthSbx.valueChanged.connect(self._handleLengthSbx)
        self.lengthSbx.setAccelerated(True)

        self.rotationSbx.valueChanged.connect(self._handleRotationSbx)
        self.rotationSbx.setAccelerated(True)

        self.xSbx.valueChanged.connect(self._handleXSbx)
        self.xSbx.setAccelerated(True)

        self.zSbx.valueChanged.connect(self._handleZSbx)
        self.zSbx.setAccelerated(True)

        self.pullBtn.clicked.connect(self._handlePullBtn)

        self.firstBtn.clicked.connect(self._handleFirstBtn)
        self.prevBtn.clicked.connect(self._handlePrevBtn)
        self.nextBtn.clicked.connect(self._handleNextBtn)
        self.lastBtn.clicked.connect(self._handleLastBtn)

        trackSelectionMethods = (
            '<Track Selection Method>',
            self.SELECT_BY_NAME,
            self.SELECT_BY_INDEX,
            self.SELECT_ALL_BEFORE,
            self.SELECT_ALL_AFTER,
            self.SELECT_ALL)

        self.selectionMethodCB.addItems(trackSelectionMethods)
        self.selectBtn.clicked.connect(self._handleSelectBtn)

        trackOperationMethods = (
            '<Perform Operation >',
            self.EXTRAPOLATE_TRACK,
            self.INTERPOLATE_TRACK,
            self.LINK_SELECTED,
            self.UNLINK_SELECTED,
            self.SET_DIMENSIONS,
            self.SET_WIDTH,
            self.SET_LENGTH,
            self.SET_THETA,
            self.SET_ALL_UNC,
            self.SET_WIDTH_UNC,
            self.SET_LENGTH_UNC,
            self.SET_THETA_UNC)

        self.operationCB.addItems(trackOperationMethods)
        self.operateBtn.clicked.connect(self._handleOperateBtn)

        # in Trackway tab:
        self.showTrackwayBtn.clicked.connect(self._handleShowTrackwayBtn)
        self.hideTrackwayBtn.clicked.connect(self._handleHideTrackwayBtn)
        self.selectTrackwayBtn.clicked.connect(self._handleSelectTrackwayBtn)

        self.showAllTrackwaysBtn.clicked.connect(self._handleShowAllTrackwaysBtn)
        self.hideAllTrackwaysBtn.clicked.connect(self._handleHideAllTrackwaysBtn)
        self.selectAllTrackwaysBtn.clicked.connect(self._handleSelectAllTrackwaysBtn)

        self.clearTrackwayUI()
        self.clearTrackUI()
        Tracks_Track.initializeCadenceCam()
        cmds.select(clear=True)
        self._session = None

#===================================================================================================
#                                                                                     P U B L I C
#
#
#___________________________________________________________________________________________________ getTrack
    def getTrack(self, uid):
        """ This gets the track model instance, corresponding to a given uid. """
        model = Tracks_Track.MASTER
        return model.getByUid(uid, self._getSession())

#___________________________________________________________________________________________________ getTrackByName
    def getTrackByName(self, name, **kwargs):
        """ This gets the track model instance by name plus trackway properties. """
        model = Tracks_Track.MASTER
        return model.getByName(name, self._getSession(), **kwargs)

#___________________________________________________________________________________________________ getPreviousTrack
    def getPreviousTrack(self, track):
        """ This method just encapsulates the session getter. """
        return track.getPreviousTrack(self._getSession())

#___________________________________________________________________________________________________ getNextTrack
    def getNextTrack(self, track):
        """ This method just encapsulates the session getter. """
        return track.getNextTrack(self._getSession())

#___________________________________________________________________________________________________ getNode
    def getNode(self, track):
        """ This gets the transient node name for this track. """
        if track is None:
            return None
        if track.nodeName is None:
            track.createNode()
        return track.nodeName

# __________________________________________________________________________________________________ getSelectedTracks
    def getSelectedTracks(self):
        """ This returns a list of track model instances corresponding to the track nodes that are
            currently selected.  To achieve this, it first runs a remote script to get a list of
            track UIDs from the selected Maya track nodes. A list of the corresponding track models
            is then returned. """
        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetSelectedUidList)
        tracks = list()

        # Check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed UID Query',
                'Unable to get selected UID list from Maya', 'Error')
            return tracks

        for uid in result.payload['selectedUidList']:
            tracks.append(self.getTrack(uid))
        return tracks

#___________________________________________________________________________________________________ getFirstTrack
    def getFirstTrack(self):
        """ Returns the track model corresponding to the first track in a series. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        t = selectedTracks[0]
        p = self.getPreviousTrack(t)
        while p is not None:
            t = p
            p = self.getPreviousTrack(p)
        return t

#___________________________________________________________________________________________________ getLastTrack
    def getLastTrack(self):
        """ Returns the track model corresponding to the last track in a series. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[-1]
        n = self.getNextTrack(t)
        while n is not None:
            t = n
            n = self.getNextTrack(n)
        return t

#___________________________________________________________________________________________________ getFirstSelectedTrack
    def getFirstSelectedTrack(self):
        """ Returns the track model corresponding to the first of a series of selected nodes. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[0]
        p = self.getPreviousTrack(t)
        while p in selectedTracks:
            t = p
            p = self.getPreviousTrack(p)
        return t

#___________________________________________________________________________________________________ getLastSelectedTrack
    def getLastSelectedTrack(self):
        """ Returns the track model corresponding to the last of a series of selected nodes. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[-1]
        n = self.getNextTrack(t)
        while n in selectedTracks:
            t = n
            n = self.getNextTrack(n)
        return t

 #__________________________________________________________________________________________________ getTrackSeries
    def getTrackSeries(self):
        """ Steps backward from any selected track to the first track, then creates a list of all
            track models in a given series, in order. """
        series = list()
        t = self.getFirstTrack()
        while t:
            series.append(t)
            t = self.getNextTrack(t)
        return series

#___________________________________________________________________________________________________ selectTrack
    def selectTrack(self, track):
        """ Select the node corresponding to this track model instance, then focus the CadenceCam
            upon this node. """
        cmds.select(self.getNode(track))
        track.setCadenceCamFocus()
        track.colorTrack()

#___________________________________________________________________________________________________ clearTrackwayUI
    def clearTrackwayUI(self):
        """ Clears the banner at the top of the UI. """
        self.commLE.setText('')
        self.siteLE.setText('')
        self.yearLE.setText('')
        self.sectorLE.setText('')
        self.levelLE.setText('')
        self.trackwayTypeLE.setText('')
        self.trackwayNumberLE.setText('')

#___________________________________________________________________________________________________ clearTrackUI
    def clearTrackUI(self):
        """ Clears out the text fields associated with the track parameters in the UI. """
        self.lengthSbx.setValue(0)
        self.widthSbx.setValue(0)
        self.rotationSbx.setValue(0)
        self.noteTE.setText(u'')
        self.trackNameLE.setText(u'')
        self.trackIndexLE.setText(u'')

#___________________________________________________________________________________________________ refreshTrackwayUI
    def refreshTrackwayUI(self, dict):
        """ The trackway UI is updated using the values of the passed track model instance. """
        community = dict[TrackPropEnum.COMM.name]
        if community:
            self.commLE.setText(community)
        site = dict[TrackPropEnum.SITE.name]
        if site:
            self.siteLE.setText(site)
        year = dict[TrackPropEnum.YEAR.name]
        if year:
            self.yearLE.setText(year)
        sector = dict[TrackPropEnum.SECTOR.name]
        if sector:
            self.sectorLE.setText(sector)
        level = dict[TrackPropEnum.LEVEL.name]
        if level:
            self.levelLE.setText(level)
        type = dict[TrackPropEnum.TRACKWAY_TYPE.name]
        if type:
            self.trackwayTypeLE.setText(type)
        number = dict[TrackPropEnum.TRACKWAY_NUMBER.name]
        if number:
            self.trackwayNumberLE.setText(number)

#___________________________________________________________________________________________________ refreshTrackUI
    def refreshTrackUI(self, dict):
        """ The track properties aspect of the UI display is updated based on a dictionary derived
            from a given track model instance. """
        self.widthSbx.setValue(dict[TrackPropEnum.WIDTH.name])
        self.lengthSbx.setValue(dict[TrackPropEnum.LENGTH.name])

        self.rotationSbx.setValue(dict[TrackPropEnum.ROTATION.name])

        self.xSbx.setValue(dict[TrackPropEnum.X.name])
        self.zSbx.setValue(dict[TrackPropEnum.Z.name])
        self.noteTE.setText(dict[TrackPropEnum.NOTE.name])

        left   = dict[TrackPropEnum.LEFT.name]
        pes    = dict[TrackPropEnum.PES.name]
        number = dict[TrackPropEnum.NUMBER.name]

        name = (u'L' if left else u'R') + (u'P' if pes else u'M') + number if number else u'-'
        self.trackNameLE.setText(name)
        self.trackIndexLE.setText(unicode([TrackPropEnum.INDEX.name]))

#___________________________________________________________________________________________________ getTrackwayPropertiesFromUI
    def getTrackwayPropertiesFromUI(self):
        """ Returns a dictionary of trackway properties, extracted from the UI. """
        d = dict()
        d[TrackPropEnum.COMM.name]            = self.commLE.text()
        d[TrackPropEnum.SITE.name]            = self.siteLE.text()
        d[TrackPropEnum.YEAR.name]            = self.yearLE.text()
        d[TrackPropEnum.SECTOR.name]          = self.sectorLE.text()
        d[TrackPropEnum.LEVEL.name]           = self.levelLE.text()
        d[TrackPropEnum.TRACKWAY_TYPE.name]   = self.trackwayTypeLE.text()
        d[TrackPropEnum.TRACKWAY_NUMBER.name] = self.trackwayNumberLE.text()
        return d
#___________________________________________________________________________________________________ getTrackPropertiesFromUI
    def getTrackPropertiesFromUI(self):
        """ Returns a dictionary of track properties, extracted from the UI. """
        d = dict()
        d[TrackPropEnum.X.name]                    = self.xLE.value()
        d[TrackPropEnum.Z.name]                    = self.zLE.value()
        d[TrackPropEnum.WIDTH.name]                = self.widthLE.value()
        d[TrackPropEnum.WIDTH_MEASURED.name]       = self.widthMeasuredLE.value()
        d[TrackPropEnum.WIDTH_UNCERTAINTY.name]    = self.widthUncertaintyLE.value()
        d[TrackPropEnum.LENGTH.name]               = self.lengthLE.value()
        d[TrackPropEnum.LENGTH_MEASURED.name]      = self.lengthMeasuredLE.value()
        d[TrackPropEnum.LENGTH_UNCERTAINTY.name]   = self.lengthUncertaintyLE.value()
        d[TrackPropEnum.DEPTH_MEASURED.name]       = self.depthMeasuredLE.float()
        d[TrackPropEnum.DEPTH_UNCERTAINTY.name]    = self.depthUncertaintyLE.float()
        d[TrackPropEnum.ROTATION.name]             = self.rotationLE.float()
        d[TrackPropEnum.ROTATION_UNCERTAINTY.name] = self.rotationUncertaintyLE.float()
        d[TrackPropEnum.NOTE.name]                 = self.noteTE.text()
        return d

#___________________________________________________________________________________________________ exportSelected
#     def exportSelected(self):
#         tracks = self.getSelectedTracks()
#         if tracks is None:
#             return
#
#         l = list()
#         for t in tracks:
#             l.append(t.getProperties())
#         JSON.toFile('../../sandbox/test.json', l)
#         return tracks

#___________________________________________________________________________________________________ addTrackwayToCB
    # def addTrackwayToCB(self, trackwayNumber):
    #     trackway = "S" + trackwayNumber.zfill(2)
    #     i = self.trackwayCB.findText(trackway)
    #     if i != -1:
    #         return
    #
    #     trackways = [self.trackwayCB.itemText(i) for i in range(self.trackwayCB.count())]
    #     trackways.append(trackway)
    #     trackways.sort()
    #
    #     self.trackwayCB.clear()
    #     self.trackwayCB.addItems(trackways)
    #     i = self.trackwayCB.findText(trackway)
    #     self.trackwayCB.setCurrentIndex(i)


#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _handleWidthSbx
    def _handleWidthSbx(self):
        """ The width of the selected track is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            t = selectedTracks[0]
            t.updateFromNode()
            t.width = self.widthSbx.value()
            t.updateNode()
            self._closeSession(commit=True)

 #___________________________________________________________________________________________________ _handleLengthSbx
    def _handleLengthSbx(self):
        """ The length of the selected track is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            t = selectedTracks[0]
            t.updateFromNode()
            t.length = self.lengthSbx.value()
            t.updateNode()
            self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleRotationSBox
    def _handleRotationSbx(self):
        """ The rotation of the selected track (manus or pes) is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            t = selectedTracks[0]
            t.updateFromNode()
            t.rotation = self.rotationSbx.value()
            t.updateNode()
            self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleXSbx
    def _handleXSbx(self):
        """ The x coordinate of the selected track (manus or pes) is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            t = selectedTracks[0]
            t.updateFromNode()
            t.x = self.xSbx.value()
            t.updateNode()
            self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleZSbx
    def _handleZSbx(self):
        """ The x coordinate of the selected track (manus or pes) is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            t = selectedTracks[0]
            t.updateFromNode()
            t.z = self.zSbx.value()
            t.updateNode()
            self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handlePullBtn
    def _handlePullBtn(self):
        """ The transform data in the selected track node(s) is used to populate the UI. Note that
            if multiple track nodes are selected, the last such track node is used to extract data
            for the trackway UI. For multiple selections, however, the track UI (but not the
            trackway UI) is cleared. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            self.clearTrackwayUI()
            self.clearTrackUI()
            return

        for t in selectedTracks:
            t.updateFromNode()

        t = selectedTracks[-1]

        dict = t.toDict()
        self.refreshTrackwayUI(dict)
        if len(selectedTracks) == 1:
            self.refreshTrackUI(dict)
        else:
            self.clearTrackUI()
        self._closeSession(commit=True)
#___________________________________________________________________________________________________ _handlePushBtn
    def _handlePushBtn(self):
        """ The UI set attributes in both the database and in the Maya scene representation. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            t = selectedTracks[0]
            t.updateNode()
            t.fromDict(self.getTrackwayPropertiesFromUI())
#            Tracks_Track.updateNode()
            self._closeSession(commit=True)

# __________________________________________________________________________________________________ _handleFirstBtn
    def _handleFirstBtn(self):
        """ Get the first track, select the corresponding node, and focus the camera on it. """
        t = self.getFirstTrack()
        if t is None:
            return

        self.selectTrack(t)
        self.refreshTrackUI(t.toDict())

#___________________________________________________________________________________________________ _handlePrevBtn
    def _handlePrevBtn(self):
        """ Get the previous track, select its corresponding node, and focus the camera on it. If
            there is no previous node, just leave the current node selected. """
        t = self.getFirstSelectedTrack()
        if t is None:
            return

        p = self.getPreviousTrack(t)
        if p is None:
            return

        p.updateFromNode()
        self.selectTrack(p)
        self.refreshTrackUI(p.toDict())

#___________________________________________________________________________________________________ _handleNextBtn
    def _handleNextBtn(self):
        """ Get the next track, select its corresponding node, and focus the camera on it. If
            there is no next node, just leave the current node selected. """
        t = self.getLastSelectedTrack()
        if t is None:
            return

        n = self.getNextTrack(t)
        if n is None:
            return

        n.updateFromNode()
        self.selectTrack(n)
        self.refreshTrackUI(n.toDict())

#___________________________________________________________________________________________________ _handleLastBtn
    def _handleLastBtn(self):
        """ Get the last track, select the corresponding node, and focus the camera on it. """
        t = self.getLastTrack()
        if t is None:
            return

        self.selectTrack(t)
        self.refreshTrackUI(t.toDict())

#___________________________________________________________________________________________________ _handleSelectBtn
    def _handleSelectBtn(self):
        """ The various options for selecting a track or tracks are dispatched from here. """
        if self.selectionMethodCB.currentText() == self.SELECT_BY_NAME:
            name = self.trackNameLE.text()
            tracks = self.getTrackByName(name, **self.getTrackwayPropertiesFromUI())
            if len(tracks) == 1:
                self.selectTrack(tracks[0])
        elif self.selectTrackCB.currentText() == self.SELECT_BY_INDEX:
          print 'selected' + self.SELECT_BY_INDEX
        elif self.selectionMethodCB.currentText() == self.SELECT_ALL_BEFORE:
            print 'selected' + self.SELECT_ALL_BEFORE
        elif self.selectionMethodCB.currentText() == self.SELECT_ALL_AFTER:
            print 'selected' + self.SELECT_ALL_AFTER
        elif self.selectionMethodCB.currentText() == self.SELECT_ALL:
            print 'selected' + self.SELECT_ALL
        else:
            print 'Choose a method by which to select a track (or tracks) then click select'

    # def _handleSelectPriorBtn(self):
    #      """ Selects in Maya all nodes in the given track series up to but not including the first
    #       selected track. """
    #      t = self.getFirstSelectedTrack()
    #      if t is None:
    #          return
    #
    #      precursorNodes = list()
    #      t = t.getPrevTrack(self._getSession())
    #      while t:
    #         precursorNodes.append(t.nodeName)
    #         t = t.prevTrack(self.getSession())
    #      cmds.select(precursorNodes)
    #
    # def _handleSelectLaterBtn(self):
    #     """ Selects in Maya all nodes in the given track series after the last selected track. """
    #     t = self.getLastSelectedTrack()
    #     if t is None:
    #         return
    #
    #     successorNodes = list()
    #     t = t.getNextTrack(self._getSession())
    #     while t:
    #         successorNodes.append(t.nodeName)
    #         t = t.getNextTrack(self._getSession())
    #     cmds.select(successorNodes)
    #
    #
    #     """ Select in Maya the nodes for the entire track series based on the given selection. """
    #     tracks = self.getTrackSeries()
    #     if tracks is None:
    #         return
    #
    #     print "Selected series consists of %s tracks" % len(tracks)
    #     nodes = list()
    #     for t in tracks:
    #         nodes.append(t.nodeName)
    #     cmds.select(nodes)

#___________________________________________________________________________________________________ _handleOperateBtn
    def _handleOperateBtn(self):
        """ A number of operations can be performed on one or more selected tracks. """
        if self.operationCB.currentText() == self.EXTRAPOLATE_TRACK:
            self._handleExtrapolation()
        if self.operationCB.currentText() == self.INTERPOLATE_TRACK:
            print 'interpolating values of selected'
            self._handleInterpolation()
        if self.operationCB.currentText() == self.LINK_SELECTED:
            print 'linking selected'
            self._handleLink()
        if self.operationCB.currentText() == self.UNLINK_SELECTED:
            print 'unlinking selected'
            self._handleUnlink()
        if self.operationCB.currentText() == self.SET_DIMENSIONS:
            print 'setting dimensions of selected'
            pass
        if self.operationCB.currentText() == self.SET_WIDTH:
            print 'setting width of selected'
            pass
        if self.operationCB.currentText() == self.SET_LENGTH:
            print 'setting length of selected'
            pass
        if self.operationCB.currentText() == self.SET_THETA:
            print 'setting theta of selected'
            pass
        if self.operationCB.currentText() == self.SET_ALL_UNC:
            print 'setting uncertainty values of selected'
            pass
        if self.operationCB.currentText() == self.SET_WIDTH_UNC:
            print 'setting width uncertainty values of selected'
            pass
        if self.operationCB.currentText() == self.SET_LENGTH_UNC:
            print 'setting length uncertainty values of selected'
            pass
        if self.operationCB.currentText() == self.SET_THETA_UNC:
            print 'setting theta uncertainty values of selected'
            pass

#___________________________________________________________________________________________________ _handleExtrapolation
    def _handleExtrapolation(self):
        """ Given at least two tracks in a series, this method allows a next track to be placed in
            a straight line extrapolation of the previous two tracks.  Note that you select a given
            track (which has a precursor track) and then extrapolate to bring the next track into
            position (and to provide it an initial orientation and uncertainty associated with the
            given selected track, as a starting point). Note that if multiple nodes have been
            selected, this extrapolation is based on the last such track. """
        t = self.getLastSelectedTrack()
        if t is None:
            return
        p = self.getPreviousTrack(t)

        if p is None:
            return
        n = self.getNextTrack(t)
        if n is None:
            return

        p.updateFromNode()
        t.updateFromNode()

        deltaX = t.x - p.x
        deltaZ = t.z - p.z
        self._getSession()
        n.x        = t.x + deltaX
        n.z        = t.z + deltaZ
        n.rotation = t.rotation

        # provide n with t's uncertainties as well?

        # and finally update the node and select it
        n.updateNode()
        self.selectTrack(n)
        self._closeSession(commit=True)


#___________________________________________________________________________________________________ _handleInterpolation
    def _handleInterpolation(self):
        """ Given at least three tracks in a series, this method allows the middle track to be
            placed as a straight-line interpolation of the other two tracks.  Note that you select
            a given (which has a precursor and a next track) and then compute the position,
            orientation, and uncertainties as averages. """
        pass
#___________________________________________________________________________________________________ _handleLink
    def _handleLink(self):
        """ Two or more tracks are linked by first select them in Maya (in the intended order)
        and their models will be linked accordingly.  By convention, the last track node is then
        selected. Note that we may want to handle the case where a given track is regarded as
        the next track by more than one track. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        if len(selectedTracks) < 2:
            return
        i = 0
        while i < len(selectedTracks) - 1:
            selectedTracks[i].next = selectedTracks[i + 1].uid
            i += 1
        cmds.select(selectedTracks[-1].nodeName) # the last selected Maya nodeName is selected

        self.importFromMaya()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleUnlink
    def _handleUnlink(self):
        """ The next attribute is simply cleared for one or more selected tracks. Unlinking does
        not attempt to relink tracks automatically (one must do explicit linking instead). """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.next = u''

        self.importFromMaya()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ TRACKWAY METHODS

#___________________________________________________________________________________________________ _handleShowTrackwayBtn
    def _handleShowTrackwayBtn(self, visible=True):
        print '_handleHideTrackwayBtn passed'

        # trackway = self.trackwayCB.currentText()
        # print('trackway = %s' % trackway)
        # if trackway == '':
        #     return
        # layer = trackway + '_Layer'
        # if cmds.objExists(layer):
        #     cmds.setAttr('%s.visibility' % layer, visible)

#___________________________________________________________________________________________________ _handleHideTrackwayBtn
    def _handleHideTrackwayBtn(self):
        print '_handleHideTrackwayBtn passed'
        self._handleShowTrackwayBtn(False)

#___________________________________________________________________________________________________ _handleSelectTrackwayBtn
    def _handleSelectTrackwayBtn(self, trackway=None):
        """ Trackways are selected by Trackway type and number (such as S18). """
        print '_handleSelectTrackwayBtn passed'

#___________________________________________________________________________________________________ _handleShowAllTrackwaysBtn
    def _handleShowAllTrackwaysBtn(self):
        print '_handleShowAllTrackwaysBtn passed'

#___________________________________________________________________________________________________ _handleHideAllTrackwaysBtn
    def _handleHideAllTrackwaysBtn(self):
        print '_handleHideAllTrackwaysBtn passed'

#___________________________________________________________________________________________________ _handleSelectAllTrackwaysBtn
    def _handleSelectAllTrackwaysBtn(self):
        print '_handleSelectAllTrackwaysBtn passed'

#___________________________________________________________________________________________________ _activateWidgetDisplayImpl
    def _activateWidgetDisplayImpl(self, **kwargs):
        if CadenceEnvironment.NIMBLE_IS_ACTIVE:
         #   self.importFromMaya()
            return

        self.setVisible(False)
        PyGlassBasicDialogManager.openOk(
            self,
            header=u'No Nimble Connection',
            message=u'This tool requires an active Nimble server connection running in Maya',
            windowTitle=u'Tool Error')

#___________________________________________________________________________________________________ _deactivateWidgetDisplayImpl
    def _deactivateWidgetDisplayImpl(self, **kwargs):
        """ When the widget is closed commit any unfinished database changes """
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _getTrackSetNode
    def _getTrackSetNode(cls):
        """ This is redundunt with the version in TrackSceneUtils, but running locally. Note that
        if no TrackSetNode is found, it does not create one. """
        for node in cmds.ls(exactType='objectSet'):
            if node == CadenceEnvironment.TRACKWAY_SET_NODE_NAME:
                return node
        return None

#___________________________________________________________________________________________________ _getSession
    def _getSession(self):
        """ Access to model instances is based on the current model and session, stored in two
         local instance variables so that multiple operations can be performed before closing this
         given session."""
        if self._session is not None:
            return self._session

        self._session = Tracks_Track.MASTER.createSession()
        return self._session

#___________________________________________________________________________________________________ _closeSession
    def _closeSession(self, commit =True):
        """ Closing a session and indicating such by nulling out model and session. """
        if self._session is not None:
            if commit:
                self._session.commit()
            self._session.close()
            return True

        self._session = None
        return False
