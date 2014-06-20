# TrackwayManagerWidget.py
# (C)2012-2014
# Scott Ernst and Kent A. Stevens

import math
import nimble

from nimble import cmds

# from pyaid.json.JSON import JSON

from PySide import QtGui

from pyglass.widgets.PyGlassWidget import PyGlassWidget
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.util.maya.MayaUtils import MayaUtils

from cadence.mayan.trackway import GetSelectedUidList

#___________________________________________________________________________________________________ TrackwayManagerWidget
class TrackwayManagerWidget(PyGlassWidget):
    """ This widget is the primary GUI for interacting with the Maya scene representation of a
        trackway.  It permits selection of tracks interactively in Maya and display and editing of
        their attributes.  Tracks in Maya are represented by track nodes, each a transform node
        with an additional attribute specifying the UID of that track.  The transform's scale,
        position, and rotation (about Y) are used to intrinsically represent track dimensions,
        position, and orientation.  Track models are accessed by query based on the UID, and for a
        given session. """
#===================================================================================================
#                                                                                       C L A S S
    RESOURCE_FOLDER_PREFIX = ['tools']

    SELECT_BY_NAME       = 'Select by Name'
    SELECT_BY_INDEX      = 'Select by Index'
    SELECT_ALL_BEFORE    = 'Select All Before'
    SELECT_ALL_AFTER     = 'Select All After'
    SELECT_ALL           = 'Select All'

    EXTRAPOLATE_TRACK    = 'Extrapolate Next Track'
    INTERPOLATE_TRACK    = 'Interpolate This Track'
    LINK_SELECTED        = 'Link Selected Tracks'
    UNLINK_SELECTED      = 'Unlink Selected Tracks'
    SET_TO_MEASURED      = 'Set to Measured Dimensions'

    SET_LOW_DIM_UNCERT   = 'Set Dimension Uncertainties Low'
    SET_HIGH_DIM_UNCERT  = 'Set Dimension Uncertainties High'

    SET_LOW_ROT_UNCERT   = 'Set Rotation Uncertainty Low'
    SET_HIGH_ROT_UNCERT  = 'Set Rotation Uncertainty High'

    LOW_DIM_UNCERTAINTY  = .01
    HIGH_DIM_UNCERTAINTY = .05

    LOW_ROT_UNCERTAINTY  = 5.0
    HIGH_ROT_UNCERTAINTY = 20.0

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)

        priorSelection = MayaUtils.getSelectedTransforms()

        self.firstBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'first.png')))
        self.prevBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'prev.png')))
        self.nextBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'next.png')))
        self.lastBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'last.png')))

        # in the Track tab:
        self.widthSbx.valueChanged.connect(self._handleWidthSbx)
        self.widthSbx.setAccelerated(True)

        self.lengthSbx.valueChanged.connect(self._handleLengthSbx)
        self.lengthSbx.setAccelerated(True)

        self.widthUncertaintySbx.valueChanged.connect(self._handleWidthUncertaintySbx)
        self.lengthUncertaintySbx.valueChanged.connect(self._handleLengthUncertaintySbx)

        self.rotationSbx.valueChanged.connect(self._handleRotationSbx)
        self.rotationSbx.setAccelerated(True)
        self.rotationUncertaintySbx.valueChanged.connect(self._handleRotationUncertaintySbx)

        self.xSbx.valueChanged.connect(self._handleXSbx)
        self.xSbx.setAccelerated(True)

        self.zSbx.valueChanged.connect(self._handleZSbx)
        self.zSbx.setAccelerated(True)

        self.lengthRatioSbx.valueChanged.connect(self._handleLengthRatioSbx)

        self.pullBtn.clicked.connect(self._handlePullBtn)

        self.firstBtn.clicked.connect(self._handleFirstBtn)
        self.prevBtn.clicked.connect(self._handlePrevBtn)
        self.nextBtn.clicked.connect(self._handleNextBtn)
        self.lastBtn.clicked.connect(self._handleLastBtn)

        self.selectCadenceCamBtn.clicked.connect(self._handleSelectCadenceCamBtn)
        self.selectPerspectiveBtn.clicked.connect(self._handleSelectPerspectiveBtn)

        trackSelectionMethods = (
            self.SELECT_BY_NAME,
            self.SELECT_BY_INDEX,
            self.SELECT_ALL_BEFORE,
            self.SELECT_ALL_AFTER,
            self.SELECT_ALL)

        self.selectionMethodCB.addItems(trackSelectionMethods)
        self.selectionMethodCB.setCurrentIndex(1)
        self.selectBtn.clicked.connect(self._handleSelectBtn)

        trackOperationMethods = (
            self.EXTRAPOLATE_TRACK,
            self.INTERPOLATE_TRACK,
            self.SET_TO_MEASURED,
            self.SET_LOW_DIM_UNCERT,
            self.SET_HIGH_DIM_UNCERT,
            self.SET_LOW_ROT_UNCERT,
            self.SET_HIGH_ROT_UNCERT,
            self.LINK_SELECTED,
            self.UNLINK_SELECTED)

        # set up a bank of three combo boxes of operations
        self.operation1CB.addItems(trackOperationMethods)
        self.operation1CB.setCurrentIndex(2)
        self.operation1Btn.clicked.connect(self._handleOperation1Btn)

        self.operation2CB.addItems(trackOperationMethods)
        self.operation2CB.setCurrentIndex(3)
        self.operation2Btn.clicked.connect(self._handleOperation2Btn)

        self.operation3CB.addItems(trackOperationMethods)
        self.operation3CB.setCurrentIndex(4)
        self.operation3Btn.clicked.connect(self._handleOperation3Btn)

        # in the Trackway tab:
        self.showTrackwayBtn.clicked.connect(self._handleShowTrackwayBtn)
        self.hideTrackwayBtn.clicked.connect(self._handleHideTrackwayBtn)
        self.selectTrackwayBtn.clicked.connect(self._handleSelectTrackwayBtn)

        self.showAllTrackwaysBtn.clicked.connect(self._handleShowAllTrackwaysBtn)
        self.hideAllTrackwaysBtn.clicked.connect(self._handleHideAllTrackwaysBtn)
        self.selectAllTrackwaysBtn.clicked.connect(self._handleSelectAllTrackwaysBtn)

        # and start up with the UI displaying data for the current selection, if any
        MayaUtils.setSelection(priorSelection)
        self._session = None
        self._getSession()
        self._handlePullBtn()
        self.initializeCadenceCam()
        self.setCameraFocus()

#===================================================================================================
#                                                                                     P U B L I C
#
#
#___________________________________________________________________________________________________ getTrackByUid
    def getTrackByUid(self, uid):
        """ This gets the track model instance corresponding to a given uid. """
        model = Tracks_Track.MASTER
        return model.getByUid(uid, self._getSession())

#___________________________________________________________________________________________________ getTrackByUid
    def getTrackByProperties(self, **kwargs):
        """ This gets the track model instances with specified properties. """
        model = Tracks_Track.MASTER
        return model.getByProperties(self._getSession(), **kwargs)

#___________________________________________________________________________________________________ getTrackByName
    def getTrackByName(self, name, **kwargs):
        """ This gets the track model instance by name (plus trackway properties). """
        model = Tracks_Track.MASTER
        return model.getByName(name, self._getSession(), **kwargs)

#___________________________________________________________________________________________________ getPreviousTrack
    def getPreviousTrack(self, track):
        """ This method just encapsulates the session getter. """
        return track.getPreviousTrack(self._getSession())

#___________________________________________________________________________________________________ getNextTrack
    def getNextTrack(self, track):
        """ This method just encapsulates the session getter so it is . """
        return track.getNextTrack(self._getSession())

#___________________________________________________________________________________________________ getTrackNode
    def getTrackNode(self, track):
        """ This gets the (transient) node name for this track. """
        if track is None:
            return None
        if track.nodeName is None:
            track.createTrackNode()
        return track.nodeName

# __________________________________________________________________________________________________ getSelectedTracks
    def getSelectedTracks(self):
        """ This returns a list of track model instances corresponding to the track nodes that are
            currently selected.  To achieve this, it first runs a remote script to get a list of
            track UIDs from the selected Maya track nodes. A list of the corresponding track models
            is then returned. """
        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetSelectedUidList)

        # Check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed UID Query',
                'Unable to get selected UID list from Maya', 'Error')
            return None

        selectedUidList = result.payload['selectedUidList']
        if len(selectedUidList) == 0:
            return None
        tracks = list()
        for uid in selectedUidList:
            tracks.append(self.getTrackByUid(uid))
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
        cmds.select(self.getTrackNode(track))
        self.setCameraFocus()

#___________________________________________________________________________________________________ clearTrackwayUI
    def clearTrackwayUI(self):
        """ Clears the banner at the top of the UI. """
        self.siteLE.setText('')
        self.yearLE.setText('')
        self.sectorLE.setText('')
        self.levelLE.setText('')
        self.trackwayTypeLE.setText('')
        self.trackwayNumberLE.setText('')

#___________________________________________________________________________________________________ clearTrackUI
    def clearTrackUI(self):
        """ Clears out the text fields associated with the track parameters in the UI. """
        self.widthLbl.setText('Width  [%4s]' % '')
        self.widthSbx.setValue(0)

        self.lengthLbl.setText('Length [%4s]' % '')
        self.lengthSbx.setValue(0)

        self.rotationSbx.setValue(0)
        self.noteTE.setText(u'')
        self.trackNameLE.setText(u'')
        self.trackIndexLE.setText(u'')

#___________________________________________________________________________________________________ refreshTrackwayUI
    def refreshTrackwayUI(self, dict):
        """ The trackway UI is updated using the values of the passed track model instance. """

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
        self.widthSbx.setValue(100.0*dict[TrackPropEnum.WIDTH.name])
        self.widthLbl.setText('Width  [%2.0f]' % (100.0*dict[TrackPropEnum.WIDTH_MEASURED.name]))

        self.lengthSbx.setValue(100.0*dict[TrackPropEnum.LENGTH.name])
        self.lengthLbl.setText('Length [%2.0f]' % (100.0*dict[TrackPropEnum.LENGTH_MEASURED.name]))

        self.widthUncertaintySbx.setValue(100.0*dict[TrackPropEnum.WIDTH_UNCERTAINTY.maya])
        self.lengthUncertaintySbx.setValue(100.0*dict[TrackPropEnum.LENGTH_UNCERTAINTY.maya])

        self.rotationSbx.setValue(dict[TrackPropEnum.ROTATION.name])
        self.rotationUncertaintySbx.setValue(dict[TrackPropEnum.ROTATION_UNCERTAINTY.name])

        self.xSbx.setValue(dict[TrackPropEnum.X.name])
        self.zSbx.setValue(dict[TrackPropEnum.Z.name])
        self.noteTE.setText(dict[TrackPropEnum.NOTE.name])

        left   = dict[TrackPropEnum.LEFT.name]
        pes    = dict[TrackPropEnum.PES.name]
        number = dict[TrackPropEnum.NUMBER.name]
        index  = dict[TrackPropEnum.INDEX.name]

        name = (u'L' if left else u'R') + (u'P' if pes else u'M') + number if number else u'-'
        self.trackNameLE.setText(name)
        self.trackIndexLE.setText(unicode(index))

#___________________________________________________________________________________________________ getTrackwayPropertiesFromUI
    def getTrackwayPropertiesFromUI(self):
        """ Returns a dictionary of trackway properties, extracted from the UI. """
        return {
            TrackPropEnum.SITE.name:self.siteLE.text(),
            TrackPropEnum.YEAR.name:self.yearLE.text(),
            TrackPropEnum.SECTOR.name:self.sectorLE.text(),
            TrackPropEnum.LEVEL.name:self.levelLE.text(),
            TrackPropEnum.TRACKWAY_TYPE.name:self.trackwayTypeLE.text(),
            TrackPropEnum.TRACKWAY_NUMBER.name:self.trackwayNumberLE.text() }

#___________________________________________________________________________________________________ initializeCadenceCam
    def initializeCadenceCam(self):
        """ This creates an orthographic camera that looks down the Y axis onto the XZ plane, and
            rotated so that the AI file track labels are legible.  This camera is positioned so
            that the given track nodeName is centered in its field by setCameraFocus. """
        if cmds.objExists('CadenceCam'):
            return

        c = cmds.camera(
            orthographic=True,
            nearClipPlane=1,
            farClipPlane=100000,
            orthographicWidth=500)
        cmds.setAttr(c[0] + '.visibility', False)
        cmds.rename(c[0], 'CadenceCam')
        cmds.rotate(-90, 180, 0)
        cmds.move(0, 100, 0, 'CadenceCam', absolute=True)

#___________________________________________________________________________________________________ setCameraFocus
    def setCameraFocus(self):
        """ Center the current camera (CadenceCam or persp) on the currently selected node. """
        cmds.viewFit(fitFactor=0.5, animate=True)

#___________________________________________________________________________________________________ _handleWidthSbx
    def _handleWidthSbx(self):
        """ The width of the selected track is adjusted. Width is stored in the database in
            fractional meters but send to Maya in cm and displayed in integer cm units."""
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.width = self.widthSbx.value()/100.0
        t.updateNode()
        self._closeSession(commit=True)

 #___________________________________________________________________________________________________ _handleLengthSbx
    def _handleLengthSbx(self):
        """ The length of the selected track is adjusted. Length is stored in the database in
            fractional meters but send to Maya in cm and displayed in integer cm units."""
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.length = self.lengthSbx.value()/100.0
        t.updateNode()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleWidthUncertaintySbx
    def _handleWidthUncertaintySbx(self):
        """ The width uncertainty of the selected track is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.widthUncertainty = self.widthUncertaintySbx.value()/100.0
        t.updateNode()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handlengthUncertaintySbx
    def _handleLengthUncertaintySbx(self):
        """ The length uncertainty of the selected track is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.lengthUncertainty = self.lengthUncertaintySbx.value()/100.0
        t.updateNode()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleRotationSBox
    def _handleRotationSbx(self):
        """ The rotation of the selected track (manus or pes) is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.rotation = self.rotationSbx.value()
        t.updateNode()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleRotationUncertaintySbx
    def _handleRotationUncertaintySbx(self):
        """ The track node has a pair of nodes that represent the angular uncertainty (plus or minus
            some value set up in the rotation uncertainty spin box (calibrated in degrees). """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.rotationUncertainty = self.rotationUncertaintySbx.value()
        t.updateNode()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleXSbx
    def _handleXSbx(self):
        """ The x coordinate of the selected track (manus or pes) is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.x = self.xSbx.value()
        t.updateNode()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleZSbx
    def _handleZSbx(self):
        """ The x coordinate of the selected track (manus or pes) is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.z = self.zSbx.value()
        t.updateNode()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleLengthRatioSbx
    def _handleLengthRatioSbx(self):
        """ The ratio from 0.0 to 1.0 representing fraction of distance from the 'anterior' extreme
            of the track to the 'center' (point of greatest width). """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()

        t = selectedTracks[0]
        deltaL = t.lengthRatio*t.length
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.lengthRatio = self.lengthRatioSbx.value()
        deltaS = -100.0*(t.lengthRatio*t.length - deltaL)
        theta  = math.radians(t.rotation)
        deltaX = deltaS*math.sin(theta)
        deltaZ = deltaS*math.cos(theta)
        t.x = t.x + deltaX
        t.z = t.z + deltaZ
        t.updateNode()

        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handlePullBtn
    def _handlePullBtn(self):
        """ The transform data in the selected track node(s) is used to populate the UI. Note that
            if multiple track nodes are selected, the last such track node is used to extract data
            for the trackway UI (but the fields of the track UI are cleared). """
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
            self.setCameraFocus()
        else:
            self.clearTrackUI()
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
        """ The various options for track selection are dispatched from here. """
        if self.selectionMethodCB.currentText() == self.SELECT_BY_NAME:
            name   = self.trackNameLE.text()
            tracks = self.getTrackByName(name, **self.getTrackwayPropertiesFromUI())
            if tracks is None:
                return
            if len(tracks) == 1:
                self.selectTrack(tracks[0])

        elif self.selectionMethodCB.currentText() == self.SELECT_BY_INDEX:
            tracks = self.getTrackByProperties(index=self.trackIndexLE.text())
            if tracks is None:
                return
            if len(tracks) == 1:
                self.selectTrack(tracks[0])

        elif self.selectionMethodCB.currentText() == self.SELECT_ALL_BEFORE:
            print 'selected' + self.SELECT_ALL_BEFORE
            self._handleSelectAllBefore()

        elif self.selectionMethodCB.currentText() == self.SELECT_ALL_AFTER:
            print 'selected' + self.SELECT_ALL_AFTER
            self._handleSelectAllAfter()

        elif self.selectionMethodCB.currentText() == self.SELECT_ALL:
            print 'selected' + self.SELECT_ALL
            self._handleSelectAll()

        else:
            print 'Choose a method by which to select a track (or tracks) then click select'
#___________________________________________________________________________________________________ _handleSelectAllBefore
    def _handleSelectAllBefore(self):
        """ Selects all track nodes up to (but excluding) the first currently selected track. """
        t = self.getFirstSelectedTrack()
        if t is None:
            return

        nodes = list()
        t = self.getPreviousTrack(t)
        while t:
            nodes.append(self.getTrackNode(t))
            t = self.getPreviousTrack(t)
        cmds.select(nodes)

#___________________________________________________________________________________________________ _handleSelectAllAfter
    def _handleSelectAllAfter(self):
        """ Selects all track nodes after the last currently selected track. """
        t = self.getLastSelectedTrack()
        if t is None:
           return

        nodes= list()
        t = self.getNextTrack(t)
        while t:
             nodes.append(self.getTrackNode(t))
             t = self.getNextTrack(t)
        cmds.select(nodes)

#___________________________________________________________________________________________________ _handleSelectAll
    def _handleSelectAll(self):
        """ Select in Maya the nodes for the entire track series based on the given selection. """
        tracks = self.getTrackSeries()
        if tracks is None:
            return

        nodes = list()
        for t in tracks:
            nodes.append(self.getTrackNode(t))
        cmds.select(nodes)

#___________________________________________________________________________________________________ _handleOperation1Btn
    def _handleOperation1Btn(self):
        """ Passes the selected operation to be performed. """
        self._handleOperation(self.operation1CB.currentText())

#___________________________________________________________________________________________________ _handleOperation2Btn
    def _handleOperation2Btn(self):
        """ Passes the selected operation to be performed. """
        self._handleOperation(self.operation2CB.currentText())

#___________________________________________________________________________________________________ _handleOperation3Btn
    def _handleOperation3Btn(self):
        """ Passes the selected operation to be performed. """
        self._handleOperation(self.operation3CB.currentText())

#___________________________________________________________________________________________________ _handleOperation
    def _handleOperation(self, op):
        """ A number of operations can be performed on one or more selected tracks. """
        if op == self.EXTRAPOLATE_TRACK:
            self._handleExtrapolation()

        elif op == self.INTERPOLATE_TRACK:
            self._handleInterpolation()

        elif op == self.LINK_SELECTED:
            self._handleLink()

        elif op == self.UNLINK_SELECTED:
            self._handleUnlink()

        elif op == self.SET_TO_MEASURED:
            self._handleSetToMeasuredDimensions()

        elif op == self.SET_LOW_DIM_UNCERT:
            self._handleSetLowDimensionalUncertainty()

        if op == self.SET_HIGH_DIM_UNCERT:
            self._handleSetHighDimensionalUncertainty()

        elif op == self.SET_LOW_ROT_UNCERT:
            self._handleSetLowRotationalUncertainty()

        if op == self.SET_HIGH_ROT_UNCERT:
            self._handleSetHighRotationalUncertainty()

#___________________________________________________________________________________________________ _handleExtrapolation
    def _handleExtrapolation(self):
        """ Given at least two tracks in a series, this method allows the next track to be placed in
            a straight line extrapolation of the given track and its previous track. The next track
            node is also given the orientation and length and width uncertainties associated with
            the given selected track. If multiple nodes have been selected, this extrapolation is
            based on the last such node. """
        self._getSession()

        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        t = selectedTracks[-1]
        p = self.getPreviousTrack(t)

        if p is None:
            return

        n = self.getNextTrack(t)
        if n is None:
            return

        t.updateFromNode()

        if n.width == 0.0:
            n.width = n.widthMeasured
        if n.length  == 0.0:
            n.length = n.lengthMeasured

        n.x                 = t.x + (t.x - p.x)
        n.z                 = t.z + (t.z - p.z)
        n.rotation          = t.rotation
        n.lengthRatio       = t.lengthRatio
        n.widthUncertainty  = t.widthUncertainty
        n.lengthUncertainty = t.lengthUncertainty

        n.updateNode()
        dict = n.toDict()
        self.selectTrack(n)
        self.refreshTrackUI(dict)
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleInterpolation
    def _handleInterpolation(self):
        """ Based on a (single) selected track node t, this track is interpolated based on the
            previous p and the next track n. This requires both a p and n, of course. """
        self._getSession()

        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        t = selectedTracks[0]
        t.updateFromNode()

        p = self.getPreviousTrack(t)
        if p is None:
            return

        n = self.getNextTrack(t)
        if n is None:
            return

        t.x                 = (p.x + n.x)/2.0
        t.z                 = (p.z + n.z)/2.0
        t.rotation          = (p.rotation + n.rotation)/2.0
        t.lengthRatio       = (p.lengthRatio + n.lengthRatio)/2.0
        t.widthUncertainty  = (p.widthUncertainty + n.widthUncertainty)/2.0
        t.lengthUncertainty = (p.lengthUncertainty + n. lengthUncertainty)/2.0

        # update the Maya node and the UI
        t.updateNode()
        dict = t.toDict()
        self.selectTrack(t)
        self.refreshTrackUI(dict)
        self._closeSession(commit=True)
#___________________________________________________________________________________________________ _handleLink
    def _handleLink(self):
        """ Two or more tracks are linked by first select them in Maya (in the intended order) and
            their models will be linked accordingly.  By convention, the last track node is then
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
        """ The next attribute is simply cleared for one or more selected tracks. Unlinking does not
            attempt to relink tracks automatically (one must do explicit linking instead). """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.next = u''

        self.importFromMaya()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleSetToMeasuredDimnensions
    def _handleSetToMeasuredDimensions(self):
        """ The selected tracks are assigned the length and width values that were measured in the
        field. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.length = t.lengthMeasured
            t.width  = t.widthMeasured
            t.updateNode()

        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleSetLowDimensionalUncertainty
    def _handleSetLowDimensionalUncertainty(self):
        """ The selected tracks are assigned low uncertainty values. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.updateFromNode() # use this opportunity to capture current state of the Maya node
            t.lengthUncertainty   = self.LOW_DIM_UNCERTAINTY
            t.widthUncertainty    = self.LOW_DIM_UNCERTAINTY
            t.updateNode()

        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleSetHighDimensionalUncertainty
    def _handleSetHighDimensionalUncertainty(self):
        """ The selected tracks are assigned high uncertainty values. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.updateFromNode() # use this opportunity to capture current state of the Maya node
            t.lengthUncertainty   = self.HIGH_DIM_UNCERTAINTY
            t.widthUncertainty    = self.HIGH_DIM_UNCERTAINTY
            print 'track %s has uncertainty %s' % (t.name, t.rotationUncertainty)
            t.updateNode()

        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleSetLowRotationalUncertainty
    def _handleSetLowRotationalUncertainty(self):
        """ The selected tracks are assigned low uncertainty values. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.updateFromNode() # use this opportunity to capture current state of the Maya node
            t.rotationUncertainty = self.LOW_ROT_UNCERTAINTY
            t.updateNode()

        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleSetHighRotationalUncertainty
    def _handleSetHighRotationalUncertainty(self):
        """ The selected tracks are assigned high uncertainty values. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.updateFromNode() # use this opportunity to capture current state of the Maya node
            t.rotationUncertainty = self.HIGH_ROT_UNCERTAINTY
            print 'track %s has uncertainty %s' % (t.name, t.rotationUncertainty)
            t.updateNode()

        self._closeSession(commit=True)

#
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

#___________________________________________________________________________________________________ _handleSelectCadenceCamBtn
    def _handleSelectCadenceCamBtn(self):
        priorSelection = MayaUtils.getSelectedTransforms()

        selectedTracks = self.getSelectedTracks()
        cmds.lookThru('CadenceCam')
        if selectedTracks is None:
            return
        cmds.viewFit(fitFactor=0.25, animate=True)

#___________________________________________________________________________________________________ _handleSelectPerspectiveBtn
    def _handleSelectPerspectiveBtn(self):
        cmds.lookThru('persp')
        selectedTracks = self.getSelectedTracks()

        if not selectedTracks:
            return

        cmds.viewFit(fitFactor=0.25, animate=True)

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
        """ When the widget is closed commit any unfinished database changes. """
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
         given session. """
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
