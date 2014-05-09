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
        self.pushBtn.clicked.connect(self._handlePushBtn)

        self.firstBtn.clicked.connect(self._handleFirstBtn)
        self.prevBtn.clicked.connect(self._handlePrevBtn)
        self.nextBtn.clicked.connect(self._handleNextBtn)
        self.lastBtn.clicked.connect(self._handleLastBtn)

        self.linkBtn.clicked.connect(self._handleLinkBtn)
        self.unlinkBtn.clicked.connect(self._handleUnlinkBtn)

        trackSelectionMethods = (
            '<Selection Method>',
            self.SELECT_BY_NAME,
            self.SELECT_BY_INDEX,
            self.SELECT_ALL_BEFORE,
            self.SELECT_ALL_AFTER,
            self.SELECT_ALL)

        self.selectionMethodCB.addItems(trackSelectionMethods)
        self.selectBtn.clicked.connect(self._handleSelectBtn)

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

#___________________________________________________________________________________________________ getTrackByProperties
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
        """ This runs a remote script to get a list of the track UID from the selected Maya track
            nodes. A list of the corresponding track models with those UIDs is returned. """
        conn = nimble.getConnection()
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

#___________________________________________________________________________________________________ getFirstTrackInSeries
    def getFirstTrackInSeries(self):
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

#___________________________________________________________________________________________________ getLastTrackInSeries
    def getLastTrackInSeries(self):
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

#___________________________________________________________________________________________________ getFirstTrackInSelection
    def getFirstTrackInSelection(self):
        """ Returns the track model corresponding to the first of a series of selected tracks. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[0]
        p = self.getPreviousTrack(t)
        while p in selectedTracks:
            t = p
            p = self.getPreviousTrack(p)
        return t

#___________________________________________________________________________________________________ getLastTrackInSelection
    def getLastTrackInSelection(self):
        """ Returns the track model corresponding to the last of a series of selected tracks. """
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
        t = self.getFirstTrackInSeries()
        while t:
            series.append(t)
            t = self.getNextTrack(t)
        return series

#___________________________________________________________________________________________________ selectTrack
    def selectTrack(self, track):
        """ Select the node corresponding to this track model instance, then focus the CadenceCam
            upon this node. """
        print 'in selectTrack, track node is %s' % self.getNode(track)
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
        s = ''
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
            t.width = self.widthSbx.value()
            print 'in _handleWidthSbx: current width value = %s ' % t.width
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
            t.length = self.lengthSbx.value()
            print 'in _handleLengthSbx: current length value = %s ' % t.length
            t.updateNode()
            self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleRotationSpinBox
    def _handleRotationSbx(self):
        """ The rotation of the selected track (manus or pes) is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            t = selectedTracks[0]
            t.rotation = self.rotationSbx.value()
            print 'in _handleRotationSbx: current rotation value = %s ' % t.rotation
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
            t.x = self.xSbx.value()
            print 'in _handleXSbx: current x value = %s ' % t.x
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
            t.z = self.zSbx.value()
            print 'current z value = %s ' % t.z
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
        print 'in _handlePullBtn, t = %s' % t.name

        dict = t.toDict()
        self.refreshTrackwayUI(dict)
        if len(selectedTracks) == 1:
            self.refreshTrackUI(dict)
        else:
            self.clearTrackUI()
        self._closeSession(commit=True)
#___________________________________________________________________________________________________ _handlePushBtn
    def _handlePushBtn(self):
        """ The UI can be used to set some (but not all) attributes in both the database and in
            the Maya scene representation.  For instance, multiple track nodes can be selected, and
            their rotational uncertainty set to all by clicking a given uncertainty radio button
            then this push button.  One can also link (or unlink) multiple tracks by this method.
            The data specific to an instance of track model is updated with data extracted from the
            UI then the track model is used to update the node, and the session is closed. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            t = selectedTracks[0]
            t.updateNode()
#            Tracks_Track.fromDict(self.getTrackwayPropertiesFromUI())
#            Tracks_Track.updateNode()
            self._closeSession(commit=True)

# __________________________________________________________________________________________________ _handleFirstBtn
    def _handleFirstBtn(self):
        """ Get the first track, select the corresponding node, and focus the camera on it. """
        t = self.getFirstTrackInSeries()
        if t is None:
            return

        self.selectTrack(t)
        self.refreshTrackUI(t.toDict())

#___________________________________________________________________________________________________ gotoPrevTrack
    def _handlePrevBtn(self):
        """ Get the previous track, select its corresponding node, and focus the camera on it. If
            there is no previous node, just leave the current node selected. """
        t = self.getFirstTrackInSelection()
        if t is None:
            return

        t = self.getPreviousTrack(t)
        if t is None:
            return

        self.selectTrack(t)
        self.refreshTrackUI(t.toDict())

#___________________________________________________________________________________________________ _handleNextBtn
    def _handleNextBtn(self):
        """ Get the next track, select its corresponding node, and focus the camera on it. If
            there is no next node, just leave the current node selected. """
        t = self.getLastTrackInSelection()
        if t is None:
            return

        t = self.getNextTrack(t)
        if t is None:
            return

        self.selectTrack(t)
        self.refreshTrackUI(t.toDict())

#___________________________________________________________________________________________________ _handleLastBtn
    def _handleLastBtn(self):
        """ Get the last track, select the corresponding node, and focus the camera on it. """
        t = self.getLastTrackInSeries()
        if t is None:
            return

        self.selectTrack(t)
        self.refreshTrackUI(t.toDict())

#___________________________________________________________________________________________________ _handleSelectBtn
    def _handleSelectBtn(self):
        if self.selectionMethodCB.currentText() == self.SELECT_BY_NAME:
            name = self.trackNameLE.text()
            print 'in _handleSelectBtn: requested track name =' + name
            print "trackway properties from UI are:"
            print self.getTrackwayPropertiesFromUI()
            tracks = self.getTrackByName(name, **self.getTrackwayPropertiesFromUI())
            if len(tracks) == 1:
                track = tracks[0]
                print 'UID = ' + track.name
                self.selectTrack(track)
        elif self.selectTrack.currentText() == self.SELECT_BY_INDEX:
          print 'selected' + self.SELECT_BY_INDEX
        elif self.selectionMethodCB.currentText() == self.SELECT_ALL_BEFORE:
            print 'selected' + self.SELECT_ALL_BEFORE
        elif self.selectionMethodCB.currentText() == self.SELECT_ALL_AFTER:
            print 'selected' + self.SELECT_ALL_AFTER
        elif self.selectionMethodCB.currentText() == self.SELECT_ALL:
            print 'selected' + self.SELECT_ALL
        else:
            print 'choose a method by which to select a track or tracks then click select'


    # def _handleSelectPriorBtn(self):
    #      """ Selects in Maya all nodes in the given track series up to but not including the first
    #       selected track. """
    #      t = self.getFirstTrackInSelection()
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
    #     t = self.getLastTrackInSelection()
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

#___________________________________________________________________________________________________ _handleLinkBtn
    def _handleLinkBtn(self):
        """ Two or more tracks are linked by first select them in Maya (in the intended order)
        and their models will be linked accordingly.  By convention, the last track node is then
        selected. Note that we may want to handle the case where a given track is regarded as
        the next track by more than one track. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        i = 0
        while i < len(selectedTracks) - 1:
            selectedTracks[i].next = selectedTracks[i + 1].uid
            i += 1
        cmds.select(selectedTracks[-1].nodeName) # the last selected Maya nodeName is selected

        self.importFromMaya()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleUnlinkBtn
    def _handleUnlinkBtn(self):
        """ The next attribute is simply cleared for one or more selected tracks. Unlinking does
        not attempt to relink tracks automatically (one must do explicit linking instead). """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.next = u''

        self.importFromMaya()
        self._closeSession(commit=True)

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
