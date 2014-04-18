# TrackwayManagerWidget.py
# (C)2012-2014
# Scott Ernst and Kent A. Stevens

import nimble

from nimble import cmds

# from pyaid.json.JSON import JSON

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

        # in Track tab:
        self.pullBtn.clicked.connect(self._handlePullBtn)
        self.pushBtn.clicked.connect(self._handlePushBtn)

        self.firstBtn.clicked.connect(self._handleFirstBtn)
        self.prevBtn.clicked.connect(self._handlePrevBtn)
        self.nextBtn.clicked.connect(self._handleNextBtn)
        self.lastBtn.clicked.connect(self._handleLastBtn)

        self.selectTrackByNameBtn.clicked.connect(self._handleSelectByNameBtn)
        self.selectTrackByIndexBtn.clicked.connect(self._handleSelectByIndexBtn)

        self.selectPriorBtn.clicked.connect(self._handleSelectPriorBtn)
        self.selectLaterBtn.clicked.connect(self._handleSelectLaterBtn)
        self.selectSeriesBtn.clicked.connect(self._handleSelectSeriesBtn)

        self.linkBtn.clicked.connect(self._handleLinkBtn)
        self.unlinkBtn.clicked.connect(self._handleUnlinkBtn)

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
        result = conn.runPythonModule(GetSelectedUidList, runInMaya=False)
        tracks = list()

        # Check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed UID Query',
                'Unable to get selected UID list from Maya', 'Error')
            return tracks

        for uid in result.payload['selectedUidList']:
            tracks.append(Tracks_Track.getByUid(uid, self._getSession()))
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

#___________________________________________________________________________________________________ clearTrackwayUI
    def clearTrackwayUI(self):
        """ Clears out the text fields associated with the trackway banner in the UI. """
        self.communityLE.setText('')
        self.siteLE.setText('')
        self.yearLE.setText('')
        self.sectorLE.setText('')
        self.levelLE.setText('')
        self.trackwayTypeLE.setText('')
        self.trackwayNumberLE.setText('')
        self.leftLE.setText('')
        self.pesLE.setText('')
        self.numberLE.setText('')

#___________________________________________________________________________________________________ clearTrackUI
    def clearTrackUI(self):
        """ Clears out the text fields associated with the track parameters in the UI. """
        self.xLE.setText(u'')
        self.zLE.setText(u'')
        self.widthLE.setText(u'')
        self.widthUncertaintyLE.setText(u'')
        self.widthMeasuredLE.setText(u'')
        self.lengthLE.setText(u'')
        self.lengthUncertaintyLE.setText(u'')
        self.lengthMeasuredLE.setText(u'')
        self.rotationLE.setText(u'')
        self.rotationUncertaintyLE.setText(u'')
        self.depthMeasuredLE.setText(u'')
        self.depthUncertaintyLE.setText(u'')
        self.noteTE.setPlainText(u'')
        self.prevTrackLbl.setText(u'')
        self.nextTrackLbl.setText(u'')
        self.leftLE.setText(u'')
        self.pesLE.setText(u'')
        self.numberLE.setText(u'')
        self.indexLE.setText(u'')

#___________________________________________________________________________________________________ refreshTrackwayUI
    def refreshTrackwayUI(self):
        """ The trackway properties UI display is updated using the values of the currently-
            selected track. If more than one track is selected, the first track is used."""
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            self.clearTrackwayUI()
            return

        t = selectedTracks[0]
        self.communityLE.setText(t.community)
        self.siteLE.setText(t.site)
        self.yearLE.setText(t.year)
        self.sectorLE.setText(t.sector)
        self.levelLE.setTextt(t.level)
        self.trackwayTypeLE.setText(t.trackwayType)
        self.trackwayNumberLE.setText(t.trackwayNumber)

#___________________________________________________________________________________________________ refreshTrackUI
    def refreshTrackUI(self):
        """ The track properties UI display is updated using the values of the currently-
            selected track. If more than one track is selected, empty strings are displayed. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks or (len(selectedTracks) > 1):
            self.clearTrackUI()
            return

        d = selectedTracks[0].toDict()
        self.xLE.setText('%.2f' % d[TrackPropEnum.X.name])
        self.zLE.setText('%.2f' % d[TrackPropEnum.Z.name])
        self.widthLE.setText('%.2f' % d[TrackPropEnum.WIDTH.name])
        self.widthMeasuredLE.setText('%.2f' % d[TrackPropEnum.WIDTH_MEASURED.name])
        self.widthUncertaintyLE.setText('%.2f' % d[TrackPropEnum.WIDTH_UNCERTAINTY.name])
        self.lengthLE.setText('%.2f' % d[TrackPropEnum.LENGTH.name])
        self.lengthMeasuredLE.setText('%.2f' % d[TrackPropEnum.LENGTH_MEASURED.name])
        self.lengthUncertaintyLE.setText('%.2f' % d[TrackPropEnum.LENGTH_UNCERTAINTY.name])
        self.depthMeasuredLE.setText('%.2f' % d[TrackPropEnum.DEPTH_MEASURED.name])
        self.depthUncertaintyLE.setText('%.2f' % d[TrackPropEnum.DEPTH_UNCERTAINTY.name])
        self.rotationLE.setText('%.2f' % d[TrackPropEnum.ROTATION.name])
        self.rotationUncertaintyLE.setText('%.2f' % d[TrackPropEnum.ROTATION_UNCERTAINTY.name])
        self.noteTE.setText(d[TrackPropEnum.NOTE.name])
        self.leftLE.setText(d[TrackPropEnum.LEFT.name])
        self.pesLE.setText(d[TrackPropEnum.PES.name])
        self.numberLE.setText(d[TrackPropEnum.NUMBER.name])
        self.indexLE.setText((d[TrackPropEnum.INDEX.name]))

#___________________________________________________________________________________________________ getTrackwayPropertiesFromUI
    def getTrackwayPropertiesFromUI(self):
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
#___________________________________________________________________________________________________ getTrackPropertiesFromUI
    def getTrackPropertiesFromUI(self):
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


#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _handlePullBtn
    def _handlePullBtn(self):
        """ The transform data in the track node is used to populate the UI. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        t = selectedTracks[0]
        self._getSession()
        Tracks_Track.updateFromNode()
        self.closeSession(commit=True)


#___________________________________________________________________________________________________ _handlePushBtn
    def _handlePushBtn(self):
        """ The data specific to a track is extracted from the UI and used to update the track
            model.  The track model is then used to update the node. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            self._getSession()
            Tracks_Track.fromDict(self.getTrackwayPropertiesFromUI())
            Tracks_Track.updateNode()
            self.closeSession(commit=True)

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

#___________________________________________________________________________________________________ _handleSelectByNameBtn
    def _handleSelectByNameBtn(self):
        pass

#___________________________________________________________________________________________________ _handleSelectByIndexBtn
    def _handleSelectByIndexBtn(self):
        pass

#___________________________________________________________________________________________________ _handleSelectPriorBtn
    def _handleSelectPriorBtn(self):
         """ Selects in Maya all nodes in the given track series up to but not including the first
          selected track. """
         t = self.getFirstSelectedTrack()
         if t is None:
             return

         precursorNodes = list()
         t = t.getPrevTrack(self._getSession())
         while t:
            precursorNodes.append(t.nodeName)
            t = t.prevTrack(self.getSession())
         cmds.select(precursorNodes)

#___________________________________________________________________________________________________ _handleSelectLaterBtn
    def _handleSelectLaterBtn(self):
        """ Selects in Maya all nodes in the given track series after the last selected track. """
        t = self.getLastSelectedTrack()
        if t is None:
            return

        successorNodes = list()
        t = t.getNextTrack(self._getSession())
        while t:
            successorNodes.append(t.nodeName)
            t = t.getNextTrack(self._getSession())
        cmds.select(successorNodes)

#___________________________________________________________________________________________________ _handleSelectSeriesBtn
    def _handleSelectSeriesBtn(self):
        """ Select in Maya the nodes for the entire track series based on the given selection. """
        tracks = self.getTrackSeries()
        if tracks is None:
            return

        print "Selected series consists of %s tracks" % len(tracks)
        nodes = list()
        for t in tracks:
            nodes.append(t.nodeName)
        cmds.select(nodes)

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
        self.closeSession(commit=True)

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
        self.closeSession(commit=True)

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
        self.closeSession(commit=True)

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
