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

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)

        self.firstBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'first.png')))
        self.prevBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'prev.png')))
        self.nextBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'next.png')))
        self.lastBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'last.png')))

        # in Track tab:
        self.pullBtn.clicked.connect(self._handlePullBtn)
        self.pushBtn.clicked.connect(self._handlePushBtn)

        self.firstBtn.clicked.connect(self._handleFirstBtn)
        self.prevBtn.clicked.connect(self._handlePrevBtn)
        self.nextBtn.clicked.connect(self._handleNextBtn)
        self.lastBtn.clicked.connect(self._handleLastBtn)

        self.linkBtn.clicked.connect(self._handleLinkBtn)
        self.unlinkBtn.clicked.connect(self._handleUnlinkBtn)

        trackSelectionMethods = ('<Selection Method>',
                                 'Select by Name',
                                 'Select by Index',
                                 'Select Previous',
                                 'Select Subsequent',
                                 'Select All')

        self.selectionMethodCB.addItems(trackSelectionMethods)
        self.selectBtn.clicked.connect(self._handleSelectBtn)

        # in Trackway tab:
        self.showTrackwayBtn.clicked.connect(self._handleShowTrackwayBtn)
        self.hideTrackwayBtn.clicked.connect(self._handleHideTrackwayBtn)
        self.selectTrackwayBtn.clicked.connect(self._handleSelectTrackwayBtn)

        self.showAllTrackwaysBtn.clicked.connect(self._handleShowAllTrackwaysBtn)
        self.hideAllTrackwaysBtn.clicked.connect(self._handleHideAllTrackwaysBtn)
        self.selectAllTrackwaysBtn.clicked.connect(self._handleSelectAllTrackwaysBtn)

        self._session = None

#===================================================================================================
#                                                                                     P U B L I C
#

#__________________________________________________________________________________________________  getSelectedTracks
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

        model = Tracks_Track.MASTER
        for uid in result.payload['selectedUidList']:
            tracks.append(model.getByUid(uid, self._getSession()))
        return tracks

#___________________________________________________________________________________________________ getFirstTrack
    def getFirstTrack(self):
        """ Returns the track model corresponding to the first track in a series. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        t = selectedTracks[0]
        p = t.getPreviousTrack(self._getSession())
        while p is not None:
            t = p
            p = p.getPreviousTrack(self._getSession())
        return t

#___________________________________________________________________________________________________ getLastTrack
    def getLastTrack(self):
        """ Returns the track model corresponding to the last track in a series. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[-1]
        n = t.getNextTrack(self._getSession())
        while n is not None:
            t = n
            n = t.getNextTrack(self._getSession())
        return t

#___________________________________________________________________________________________________ getFirstSelectedTrack
    def getFirstSelectedTrack(self):
        """ Returns the track model corresponding to the first of a series of selected tracks. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[0]
        p = t.getPreviousTrack(self._getSession())
        while p in selectedTracks:
            t = p
            p =t.getPreviousTrack(self._getSession())
        return t

#___________________________________________________________________________________________________ getLastSelectedTrack
    def getLastSelectedTrack(self):
        """ Returns the track model corresponding to the last of a series of selected tracks. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[-1]
        n = t.getNextTrack(self._getSession())
        while n in selectedTracks:
            t = n
            n = t.getNextTrack(self._getSession())
        return t

 #__________________________________________________________________________________________________ getTrackSeries
    def getTrackSeries(self):
        """ Steps backward from any selected track to the first track, then creates a list of all
            track models in a given series, in order. """
        series = list()
        t = self.getFirstTrack()
        while t:
            series.append(t)
            t = t.getNextTrack()
        return series

#___________________________________________________________________________________________________ selectTrack
    def selectTrack(self, track):
        """ Select then focus the CadenceCam on the corresponding track node. """
        cmds.select(track.nodeName)
        track.setCadenceCamFocus()


#===================================================================================================
#                                                                               P R O T E C T E D


#___________________________________________________________________________________________________ _clearTrackwayUI
    def _clearTrackwayUI(self):
        """ Clears the banner at the top of the UI. """
        self.trackwayLbl.setText('[No Trackway Selected]')

#___________________________________________________________________________________________________ _clearTrackUI
    def _clearTrackUI(self):
        """ Clears out the text fields associated with the track parameters in the UI. """

        self.lengthLbl.setText(u'')
        self.widthLbl.setText(u'')
        self.rotationLbl.setText(u'')

        #self.dimensionalUncertainty. ?? clear all radio buttons
        #self.rotationalUncertainty ?? clear all radio buttons

        self.noteTE.setText(u'')
        self.trackNameLE.setText(u'')
        self.trackIndexLE.setText(u'')
#___________________________________________________________________________________________________ refreshTrackwayUI
    def _refreshTrackwayUI(self, track):
        """ The trackway UI display is updated using the values of the (single) passed track
            model instance. """

        s = ''
        if track.community:
            s += 'community = ' + track.community
        if track.site:
            s += '    site = ' + track.site
        if track.year:
            s += '    year = ' + track.year
        if track.sector:
            s += '    sector = ' + track.sector
        if track.level:
            s += '    level = ' + track.level
        if track.trackwayType:
            s += '    trackway = ' + track.trackwayType
        if track.trackwayNumber:
            s += track.trackwayNumber
        self.trackwayLbl.setText(s)

#___________________________________________________________________________________________________ _refreshTrackUI
    def _refreshTrackUI(self, track):
        """ The track properties UI display is updated based on the passed track model instance.
            The format for length is the fitted length (based on the node) and in parentheses is
            the value from the catalog, with two decimal place precision e.g., 123.12 (123.12).
            Note that there is length, width, rotation, and estimates of dimensional and
            rotational uncertainty. """

        d = track.toDict()

        self.lengthLbl.setText(('%.2f (%.2f)') % (d[TrackPropEnum.LENGTH.name],
                                                  d[TrackPropEnum.LENGTH_MEASURED.name]))
        self.widthLbl.setText(('%.2f (%.2f)') % (d[TrackPropEnum.WIDTH.name],
                                                  d[TrackPropEnum.WIDTH_MEASURED.name]))

        print 'rotation =', d[TrackPropEnum.ROTATION.name]
        self.rotationLbl.setText(('%.2f') % (d[TrackPropEnum.ROTATION.name]))

        #self.dimensionalUncertainty ?? set the appropriate radio button
        #self.rotationalUncertainty  ?? set the appropriate radio button

        self.noteTE.setText(d[TrackPropEnum.NOTE.name])
        self.trackNameLE.setText(track.name)
        self.trackIndexLE.setText(unicode([TrackPropEnum.INDEX.name]))

#___________________________________________________________________________________________________ _getTrackwayPropertiesFromUI
    def _getTrackwayPropertiesFromUI(self):
        """ Returns a dictionary of trackway properties, extracted from the UI. """
        out = dict()
        out[TrackPropEnum.COMM.name] = self.communityLE.text()
        out[TrackPropEnum.SITE.name] = self.siteLE.text()
        out[TrackPropEnum.YEAR.name] = self.yearLE.text()
        out[TrackPropEnum.SECTOR.name] = self.sectorLE.text()
        out[TrackPropEnum.LEVEL.name] = self.levelLE.text()
        out[TrackPropEnum.TRACKWAY_TYPE.name] = self.trackwayTypeLE.text()
        out[TrackPropEnum.TRACKWAY_NUMBER.name] = self.trackwayNumberLE.text()
        return out
#___________________________________________________________________________________________________ _getTrackPropertiesFromUI
    def _getTrackPropertiesFromUI(self):
        """ Returns a dictionary of track properties, extracted from the UI. """
        d = dict()
        d[TrackPropEnum.X.name] = self.xLE.text()
        d[TrackPropEnum.Z.name] = self.zLE.text()
        d[TrackPropEnum.WIDTH.name] = self.widthLE.text()
        d[TrackPropEnum.WIDTH_MEASURED.name] = self.widthMeasuredLE.text()
        d[TrackPropEnum.WIDTH_UNCERTAINTY.name] = self.widthUncertaintyLE.text()
        d[TrackPropEnum.LENGTH.name] = self.lengthLE.text()
        d[TrackPropEnum.LENGTH_MEASURED.name] = self.lengthMeasuredLE.text()
        d[TrackPropEnum.LENGTH_UNCERTAINTY.name] = self.lengthUncertaintyLE.text()
        d[TrackPropEnum.DEPTH_MEASURED.name] = self.depthMeasuredLE.text()
        d[TrackPropEnum.DEPTH_UNCERTAINTY.name] = self.depthUncertaintyLE.text()
        d[TrackPropEnum.ROTATION.name] = self.rotationLE.text()
        d[TrackPropEnum.ROTATION_UNCERTAINTY.name] = self.rotationUncertaintyLE.text()
        d[TrackPropEnum.NOTE.name] = self.noteTE.text()
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

#___________________________________________________________________________________________________ _handlePullBtn
    def _handlePullBtn(self):
        """ The transform data in the selected track node(s) is used to populate the UI. Note that
            if multiple track nodes are selected, the last such track node is used to extract data
            for the trackway UI. For multiple selections, however, the track UI (but not the
            trackway UI) is cleared. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            print 'clearing both UIs'
            self._clearTrackwayUI()
            self._clearTrackUI()
            return

        for t in selectedTracks:
            t.updateFromNode()

        t = selectedTracks[-1]

        self._refreshTrackwayUI(t)
        if len(selectedTracks) == 1:
            self._refreshTrackUI(t)
        else:
            self._clearTrackUI()
        self._closeSession(commit=True)
#___________________________________________________________________________________________________ _handlePushBtn
    def _handlePushBtn(self):
        """ The UI can be used to set some (but not all) attributes in both the database and in
            the Maya scene representation.  For instance, multiple track nodes can be selected, and
            their rotational uncertainty set to all by clicking a given uncertainty radio button
            then this push button.  One can also link multiple (or unlink multiple) by this method.
            In the case that some c????????????????

            ?????????????


            The data specific to an instance of track model is updated with data extracted from the
            UI then the track model is used to update the node, and the session is closed. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            Tracks_Track.fromDict(self._getTrackwayPropertiesFromUI())
            Tracks_Track.updateNode()
            self._closeSession(commit=True)

# __________________________________________________________________________________________________ _handleFirstBtn
    def _handleFirstBtn(self):
        """ Get the first track, select the corresponding node, and focus the camera on it. """
        t = self.getFirstTrack()
        if t is None:
            return
        self.selectTrack(t)
        self.importFromMaya()

#___________________________________________________________________________________________________ gotoPrevTrack
    def _handlePrevBtn(self):
        """ Get the previous track, select the corresponding node, and focus the camera on it. """
        t = self.getFirstSelectedTrack()
        if t is None:
            return
        p = t.prevTrack
        self.selectTrack(p if p else t)
        self.importFromMaya()

#___________________________________________________________________________________________________ _handleNextBtn
    def _handleNextBtn(self):
        """ Get the next track, select the corresponding node, and focus the camera on it. """
        t = self.getLastSelectedTrack()
        if t is None:
            return
        n = t.nextTrack
        self.selectTrack(n if n else t)
        self.importFromMaya()

#___________________________________________________________________________________________________ _handleLastBtn
    def _handleLastBtn(self):
        """ Get the last track, select the corresponding node, and focus the camera on it. """
        t = self.getLastTrack()
        if t is None:
            return
        self.selectTrack(t)
        self.importFromMaya()

#___________________________________________________________________________________________________ _handleSelectBtn
# CB
    def _handleSelectBtn(self):
        pass
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
