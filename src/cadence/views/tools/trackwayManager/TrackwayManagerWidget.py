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
from cadence.enum.SourceFlagsEnum import SourceFlagsEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.util.maya.MayaUtils import MayaUtils

from cadence.mayan.trackway import GetSelectedUidList
from cadence.mayan.trackway import GetUidList

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

    FETCH_TO_CAMERA   = 'Fetch to Camera'
    SELECT_BY_NAME    = 'Select by Name'
    SELECT_BY_INDEX   = 'Select by Index'
    SELECT_ALL_BEFORE = 'Select All Before'
    SELECT_ALL_AFTER  = 'Select All After'
    SELECT_COMPLETED  = 'Select Completed'
    SELECT_INCOMPLETE = 'Select Incomplete'
    SELECT_MARKED     = 'Select Marked'
    SELECT_ALL        = 'Select All'

    EXTRAPOLATE_TRACK = 'Extrapolate Next Track'
    INTERPOLATE_TRACK = 'Interpolate This Track'
    LINK_SELECTED     = 'Link Selected Tracks'
    UNLINK_SELECTED   = 'Unlink Selected Tracks'
    SET_TO_MEASURED   = 'Set to Measured Dimensions'

    SET_UNCERTAINTY_LOW      = 'Set Uncertainties Low'
    SET_UNCERTAINTY_MODERATE = 'Set Uncertainties Moderate'
    SET_UNCERTAINTY_HIGH     = 'Set Uncertainties High'

    DIMENSION_UNCERTAINTY_LOW      = 0.01
    DIMENSION_UNCERTAINTY_MODERATE = 0.03
    DIMENSION_UNCERTAINTY_HIGH     = 0.08

    ROTATION_UNCERTAINTY_LOW      = 3.0
    ROTATION_UNCERTAINTY_MODERATE = 6.0
    ROTATION_UNCERTAINTY_HIGH     = 30.0

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)

        self._session = None

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

        self.completedCkbx.clicked.connect(self._handleCompletedCkbx)
        self.markedCkbx.clicked.connect(self._handleMarkedCkbx)
        self.missingCkbx.clicked.connect(self._handleMissingCkbx)

        self.lengthRatioSbx.valueChanged.connect(self._handleLengthRatioSbx)
        self.noteLE.textChanged.connect(self._handleNoteLE)

        self.countsBtn.clicked.connect(self._handleCountsBtn)

        self.pullBtn.clicked.connect(self._handlePullBtn)

        self.firstBtn.clicked.connect(self._handleFirstBtn)
        self.prevBtn.clicked.connect(self._handlePrevBtn)
        self.nextBtn.clicked.connect(self._handleNextBtn)
        self.lastBtn.clicked.connect(self._handleLastBtn)

        self.selectCadenceCamBtn.clicked.connect(self._handleSelectCadenceCamBtn)
        self.selectPerspectiveBtn.clicked.connect(self._handleSelectPerspectiveBtn)

        trackSelectionMethods = (
            self.FETCH_TO_CAMERA,
            self.SELECT_BY_NAME,
            self.SELECT_BY_INDEX,
            self.SELECT_ALL_BEFORE,
            self.SELECT_ALL_AFTER,
            self.SELECT_COMPLETED,
            self.SELECT_INCOMPLETE,
            self.SELECT_MARKED,
            self.SELECT_ALL)

        self.selectionMethodCmbx.addItems(trackSelectionMethods)
        self.selectionMethodCmbx.setCurrentIndex(0)
        self.selectBtn.clicked.connect(self._handleSelectBtn)

        trackOperationMethods = (
            self.EXTRAPOLATE_TRACK,
            self.INTERPOLATE_TRACK,
            self.SET_TO_MEASURED,
            self.SET_UNCERTAINTY_LOW,      # for exceptional tracks
            self.SET_UNCERTAINTY_MODERATE, # a reasonable default
            self.SET_UNCERTAINTY_HIGH,     # for incomplete or rotationally ambiguous tracks
            self.LINK_SELECTED,
            self.UNLINK_SELECTED)

        # set up a bank of four combo boxes of operations for convenience access for common tasks
        self.operation1Cmbx.addItems(trackOperationMethods)
        self.operation1Cmbx.setCurrentIndex(0)
        self.operation1Btn.clicked.connect(self._handleOperation1Btn)

        self.operation2Cmbx.addItems(trackOperationMethods)
        self.operation2Cmbx.setCurrentIndex(2)
        self.operation2Btn.clicked.connect(self._handleOperation2Btn)

        self.operation3Cmbx.addItems(trackOperationMethods)
        self.operation3Cmbx.setCurrentIndex(3)
        self.operation3Btn.clicked.connect(self._handleOperation3Btn)

        self.operation4Cmbx.addItems(trackOperationMethods)
        self.operation4Cmbx.setCurrentIndex(4)
        self.operation4Btn.clicked.connect(self._handleOperation4Btn)

        # in the Trackway tab:
        self.showTrackwayBtn.clicked.connect(self._handleShowTrackwayBtn)
        self.hideTrackwayBtn.clicked.connect(self._handleHideTrackwayBtn)
        self.selectTrackwayBtn.clicked.connect(self._handleSelectTrackwayBtn)

        self.showAllTrackwaysBtn.clicked.connect(self._handleShowAllTrackwaysBtn)
        self.hideAllTrackwaysBtn.clicked.connect(self._handleHideAllTrackwaysBtn)
        self.selectAllTrackwaysBtn.clicked.connect(self._handleSelectAllTrackwaysBtn)

     ##   self.refreshTrackCountsUI()

        self.initializeCadenceCam()
        # and start up with the UI displaying data for the current selection (if any).
        MayaUtils.setSelection(priorSelection)

        self._handlePullBtn()
    #    self.setCameraFocus()

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
        """ This method just encapsulates the session getter. """
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
        result = conn.runPythonModule(GetSelectedUidList, runInMaya=True)

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
        self.trackwayLE.setText('')

#___________________________________________________________________________________________________ clearTrackUI
    def clearTrackUI(self):
        """ Clears out the text fields associated with the track parameters in the UI. """
        self.widthLbl.setText('Width:  [%4s]' % '')
        self.widthSbx.setValue(0)
        self.widthUncertaintySbx.setValue(0)

        self.lengthLbl.setText('Length: [%4s]' % '')
        self.lengthSbx.setValue(0)
        self.lengthUncertaintySbx.setValue(0)

        self.rotationSbx.setValue(0)
        self.rotationUncertaintySbx.setValue(0)

        self.completedCkbx.setChecked(False)
        self.markedCkbx.setChecked(False)
        self.missingCkbx.setChecked(False)

        self.lengthRatioSbx.setValue(0)

        self.noteLE.setText(u'')
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

        type   = dict[TrackPropEnum.TRACKWAY_TYPE.name]
        number = dict[TrackPropEnum.TRACKWAY_NUMBER.name]
        if type and number:
            trackway = type + number
            self.trackwayLE.setText(trackway)

#___________________________________________________________________________________________________ refreshTrackUI
    def refreshTrackUI(self, dict):
        """ The track properties aspect of the UI display is updated based on a dictionary derived
            from a given track model instance. """
        self.widthSbx.setValue(100.0*dict[TrackPropEnum.WIDTH.name])
        self.widthLbl.setText('Width: [%2.0f]' % (100.0*dict[TrackPropEnum.WIDTH_MEASURED.name]))

        self.lengthSbx.setValue(100.0*dict[TrackPropEnum.LENGTH.name])
        self.lengthLbl.setText('Length: [%2.0f]' % (100.0*dict[TrackPropEnum.LENGTH_MEASURED.name]))

        self.widthUncertaintySbx.setValue(100.0*dict[TrackPropEnum.WIDTH_UNCERTAINTY.maya])
        self.lengthUncertaintySbx.setValue(100.0*dict[TrackPropEnum.LENGTH_UNCERTAINTY.maya])

        self.rotationSbx.setValue(dict[TrackPropEnum.ROTATION.name])
        self.rotationUncertaintySbx.setValue(dict[TrackPropEnum.ROTATION_UNCERTAINTY.name])

        # set the checkboxes 'Completed' and 'Marked'
        f = dict[TrackPropEnum.SOURCE_FLAGS.name]
        self.completedCkbx.setChecked(SourceFlagsEnum.get(f, SourceFlagsEnum.COMPLETED))

        self.markedCkbx.setChecked(SourceFlagsEnum.get(f, SourceFlagsEnum.MARKED))
        self.missingCkbx.setChecked(dict[TrackPropEnum.HIDDEN.name])

        self.lengthRatioSbx.setValue(dict[TrackPropEnum.LENGTH_RATIO.name])

        self.noteLE.setText(dict[TrackPropEnum.NOTE.name])

        left   = dict[TrackPropEnum.LEFT.name]
        pes    = dict[TrackPropEnum.PES.name]
        number = dict[TrackPropEnum.NUMBER.name]
        index  = dict[TrackPropEnum.INDEX.name]
        name   = (u'L' if left else u'R') + (u'P' if pes else u'M') + number if number else u'-'
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
            TrackPropEnum.TRACKWAY_TYPE.name:self.trackwayLE.text()[0],
            TrackPropEnum.TRACKWAY_NUMBER.name:self.trackwayLE.text()[1:] }

#___________________________________________________________________________________________________ getFlaggedTracks
    def getFlaggedTracks(self, uidList, flag, set=True):
        """ Creates a list of all tracks that have a given source flag either set or cleared,
            based on the boolean argument set. """
        model   = Tracks_Track.MASTER
        state   = flag if set else 0
        size    = 200
        iMax    = len(uidList)/size
        i       = 0
        entries = []

        while i < iMax:
            self._getSession()
            session = model.createSession()
            query   = session.query(model)
            batch   = uidList[i*size : (i + 1)*size]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.sourceFlags.op('&')(flag) == state)
            entries += query.all()
            i       += 1
            self._closeSession(commit=False)

        if i*size < len(uidList):
            session = model.createSession()
            query   = session.query(model)
            batch   = uidList[i*size :]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.sourceFlags.op('&')(SourceFlagsEnum.COMPLETED) == state)
            entries += query.all()
            self._closeSession(commit=False)

        return entries
#___________________________________________________________________________________________________ refreshTrackCountsUI
    def refreshTrackCountsUI(self):
        """ Run a script to return a list of all Maya Track Nodes so we can get a count of both the
            total number of tracks in the scene and of those that are completed. """
        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetUidList, runInMaya=True)

        # Check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed UID Query',
                'Unable to get UID list from Maya', 'Error')
            return

        # so we have a list of UIDs, the length of which will be displayed as the totalTrackCount
        # for this Maya scene, and count of those that are completed will be displayed as well.
        uidList = result.payload['uidList']
        totalTrackCount = len(uidList)
        self.totalTrackCountLbl.setText('Total:  ' + unicode(totalTrackCount))

        # Now determine how many tracks have their COMPLETED source flag set.
        entries = self.getFlaggedTracks(uidList, SourceFlagsEnum.COMPLETED, True)
        self.completedTrackCountLbl.setText('Completed:  ' + unicode(len(entries)))

        # And show how many are currently selected.
        self.selectedTrackCountLbl.setText('Selected:  ' + unicode(len(cmds.ls(selection=True))))

#===================================================================================================
#                                                              H A N D L E R S - for the Track Tab
#___________________________________________________________________________________________________ _handleCompletedCkbx
    def _handleCompletedCkbx(self):
        """ The COMPLETED source flag for the selected track (or tracks) is set or cleared, based
            on the value of the checkbox. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        self._getSession()

        for t in selectedTracks:
            t.updateFromNode() # use this opportunity to capture the current state of the Maya node

            # to remove any leftover flags from the earlier version:  THIS SHOULD BE REMOVED LATER
            # when any leftovers of the first use of flags (not the source flags) are purged.
            t.flags = 0

            # preserve the other flags
            flags = t.sourceFlags & ~SourceFlagsEnum.COMPLETED

            if self.completedCkbx.isChecked():
                f = SourceFlagsEnum.set(flags, SourceFlagsEnum.COMPLETED)
            else:
                f = SourceFlagsEnum.clear(flags, SourceFlagsEnum.COMPLETED)

            t.sourceFlags = flags | f
            t.updateNode()

        self._closeSession(commit=True)
        self.refreshTrackCountsUI()

#___________________________________________________________________________________________________ _handleCountsBtn
    def _handleCountsBtn(self):
        """ This updates the total number of tracks in the scene and the number completed. """
        self.refreshTrackCountsUI()

#___________________________________________________________________________________________________ _handleExtrapolation
    def _handleExtrapolation(self):
        """ Given at least two tracks in a series, this method allows the next track to be placed in
            a straight line extrapolation of the given track and its previous track. The next track
            node is also given the averaged orientation and length and width uncertainties
            associated with the last two selected tracks. """
        self._getSession()

        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        # extrapolate from the last of possibly multiple selected tracks
        t = selectedTracks[-1]
        p = self.getPreviousTrack(t)

        # the first track must be in place, but if attempting to extrapolate the second track based
        # on just the first track, there is no displacement yet on which to estimate forward
        # progress (so drag that track manually off of the first track).
        if p is None:
            p = t

        # and make sure there is a next track to extrapolate
        n = self.getNextTrack(t)
        if n is None:
            return

        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        # take a linear step forward based on the number of steps in between the last two (p and t)
        # and between t and n

        # compute tp, the difference in track number from p to t
        tp = int(t.number) - int(p.number)

        # deal with the degenerate case of no previous track p, wherein p had been set to t above
        if tp == 0:
            tp = 1

        # determine the equivalent displacements in x and z for one step (since the distance from
        # p to t might represent multiple intermediate steps that were never recorded)
        dx = float(t.x - p.x)/tp
        dz = float(t.z - p.z)/tp

        # now to extrapolation from t to n, we also have to be concerned with possible missing
        # intervening steps, so compute the difference in track number from n to t
        nt  = int(n.number) - int(t.number)
        n.x = t.x + nt*dx
        n.z = t.z + nt*dz

        # if length or width (or both) were not measured originally, posit high uncertainties
        if n.widthMeasured == 0.0 or n.lengthMeasured == 0.0:
            n.widthUncertainty    = self.DIMENSION_UNCERTAINTY_HIGH
            n.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_HIGH
            n.rotationUncertainty = self.ROTATION_UNCERTAINTY_HIGH
        else:
            n.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
            n.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
            n.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE

        # assign to the next track the length ratio and rotation of the current track
        n.lengthRatio = t.lengthRatio
        n.rotation    = t.rotation

        # now assign dimensions, using n's measured values or use those from t's values as a backup
        n.width  = t.width  if n.widthMeasured  == 0.0 else n.widthMeasured
        n.length = t.length if n.lengthMeasured == 0.0 else n.lengthMeasured

        # these are reasonable defaults to work from for the pes and manus rotation uncertainty
        if n.pes:
            n.rotationUncertainty = 2*self.ROTATION_UNCERTAINTY_MODERATE
        else:
            n.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE

        # update the Maya node and the UI
        n.updateNode()
        dict = n.toDict()
        self.selectTrack(n)
        self.refreshTrackUI(dict)
        self.setCameraFocus()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleFetch
    def _handleFetch(self):
        """ This fetches the track as specified by the trackwayUI banner, and translates that track
            directly under the CadenceCam. """
        # save any currently-selected track
        selectedTracks = self.getSelectedTracks()
        if selectedTracks and len(selectedTracks) == 1:
            t = selectedTracks[0]
            t.updateFromNode()

        # that out of the way, now get the name for the new trackway and track to be fetched
        name   = self.trackNameLE.text()
        tracks = self.getTrackByName(name, **self.getTrackwayPropertiesFromUI())

        # just give up if it is not found
        if not tracks or len(tracks) > 1:
            return

        # and give up if there is for some strange reason no CadenceCam
        if not cmds.objExists('CadenceCam'):
            return

        # set this track's position to that of the CadenceCam
        t = tracks[0]

        t.x = cmds.getAttr('CadenceCam' + '.translateX')
        t.z = cmds.getAttr('CadenceCam' + '.translateZ')
        t.updateNode()
        cmds.select(self.getTrackNode(t))
        t.updateFromNode()
        self.refreshTrackUI(t.toDict())

# __________________________________________________________________________________________________ _handleFirstBtn
    def _handleFirstBtn(self):
        """ Get the first track, select the corresponding node, and focus the camera on it. """
        t = self.getFirstTrack()
        if t is None:
            return

        self.selectTrack(t)
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        dict = t.toDict()

        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

#___________________________________________________________________________________________________ _handleInterpolation
    def _handleInterpolation(self):
        """ Based on a previous and next tracks to a given (single) selected track node t, the
            parameters are interpolated. """
        self._getSession()

        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        p = self.getPreviousTrack(t)
        if p is None:
            return

        n = self.getNextTrack(t)
        if n is None:
            return

        t.x                   = 0.5*(p.x + n.x)
        t.z                   = 0.5*(p.z + n.z)
        t.width               = 0.5*(p.width + n.width)
        t.length              = 0.5*(p.length + n.length)
        t.rotation            = 0.5*(p.rotation + n.rotation)
        t.lengthRatio         = 0.5*(p.lengthRatio + n.lengthRatio)
        t.widthUncertainty    = 0.5*(p.widthUncertainty + n.widthUncertainty)
        t.lengthUncertainty   = 0.5*(p.lengthUncertainty + n. lengthUncertainty)
        t.rotationUncertainty = 0.5*(p.rotationUncertainty + n. rotationUncertainty)

        # update the Maya node and the UI
        t.updateNode()
        dict = t.toDict()
        self.selectTrack(t)
        self.refreshTrackUI(dict)
        self.setCameraFocus()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleLastBtn
    def _handleLastBtn(self):
        """ Get the last track, select the corresponding node, and focus the camera on it. """
        t = self.getLastTrack()
        if t is None:
            return

        self.selectTrack(t)
        dict = t.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

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
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.length = self.lengthSbx.value()/100.0
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
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.lengthUncertainty = self.lengthUncertaintySbx.value()/100.0
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
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        deltaL = t.lengthRatio*t.length
        t.lengthRatio = self.lengthRatioSbx.value()
        deltaS = -100.0*(t.lengthRatio*t.length - deltaL)
        theta  = math.radians(t.rotation)
        deltaX = deltaS*math.sin(theta)
        deltaZ = deltaS*math.cos(theta)
        t.x = t.x + deltaX
        t.z = t.z + deltaZ
        t.updateNode()

        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleLink
    def _handleLink(self):
        """ Two or more tracks are linked by selecting them in Maya (in the intended order) then,
            for each track, assigning the UID of each successive track to the 'next' attribute for
            that track.  By convention, the last such track node is selected. Note that we may want
            to handle the case where a given track is regarded as the next track by more than one
            'previous' track, i.e., a 'join' in two trackways """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        if len(selectedTracks) < 2:
            return

        i = 0
        iMax = len(selectedTracks) - 1
        while i < iMax:
            selectedTracks[i].updateFromNode()

            # unlink any preexisting 'previous' track to the about-to-be-next track so
            # that each track has at most one previous (and necessarily but one next)
            p = self.getPreviousTrack(selectedTracks[i + 1])
            if p:
                p.next = u''

            # now set this i-th track's next
            selectedTracks[i].next = selectedTracks[i + 1].uid
            i += 1

        t = selectedTracks[-1]
        self.selectTrack(t)
        dict = t.toDict()
        self.refreshTrackUI(dict)
        self.setCameraFocus()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleMarkedCkbx
    def _handleMarkedCkbx(self):
        """ This track has its MARKED source flag set or cleared, based on the value of the
            checkbox. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        # preserve the other flags
        flags = t.sourceFlags & ~SourceFlagsEnum.MARKED

        if self.markedCkbx.isChecked():
            f = SourceFlagsEnum.set(flags, SourceFlagsEnum.MARKED)
        else:
            f = SourceFlagsEnum.clear(flags, SourceFlagsEnum.MARKED)

        t.sourceFlags = flags | f
        t.updateNode()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleMissingCkbx
    def _handleMissingCkbx(self):
        """ The missing track has its HIDDEN flag set (or cleared) according to the state of the
            checkbox. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        result = PyGlassBasicDialogManager.openYesNo(
            self,
            u'CONFIRMATION REQUIRED',
            u'Are you sure you want to set this track to HIDDEN?  It will no longer load.',
            False)

        if not result:
            self.missingCkbx.setChecked(False)
            return

        # if a track is regarded as missing, unlink it's previous track (if any), setting it adrift
        p = self.getPreviousTrack(t)
        if p:
            p.next = u''

        # now further proclaim this track as 'hidden' (so it will not be re-loaded)
        t.hidden = self.missingCkbx.isChecked()

        # and place it back at the origin, and unoriented
        t.x        = 0.0
        t.z        = 0.0
        t.rotation = 0.0

        t.updateNode()
        self._closeSession(commit=True)

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

        self.selectTrack(n)
        n.updateFromNode() # use this opportunity to capture the current state of the Maya node
        dict = n.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

#___________________________________________________________________________________________________ _handleNoteLE
    def _handleNoteLE(self):
        """ The note line edit is handled here. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self._getSession()

        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        t.note = self.noteLE.text()
        t.updateNode()

        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleOperation
    def _handleOperation(self, op):
        """ A number of operations can be performed on one or more selected tracks. """
        if op == self.EXTRAPOLATE_TRACK:
            self._handleExtrapolation()

        elif op == self.INTERPOLATE_TRACK:
            self._handleInterpolation()

        elif op == self.SET_TO_MEASURED:
            self._handleSetToMeasuredDimensions()

        elif op == self.SET_UNCERTAINTY_LOW:
            self._handleSetUncertaintyLow()

        elif op == self.SET_UNCERTAINTY_MODERATE:
            self._handleSetUncertaintyModerate()

        elif op == self.SET_UNCERTAINTY_HIGH:
            self._handleSetUncertaintyHigh()

        elif op == self.LINK_SELECTED:
            self._handleLink()

        elif op == self.UNLINK_SELECTED:
            self._handleUnlink()

#___________________________________________________________________________________________________ _handleOperation1Btn
    def _handleOperation1Btn(self):
        """ Passes the selected operation to be performed. """
        self._handleOperation(self.operation1Cmbx.currentText())

#___________________________________________________________________________________________________ _handleOperation2Btn
    def _handleOperation2Btn(self):
        """ Passes the selected operation to be performed. """
        self._handleOperation(self.operation2Cmbx.currentText())

#___________________________________________________________________________________________________ _handleOperation3Btn
    def _handleOperation3Btn(self):
        """ Passes the selected operation to be performed. """
        self._handleOperation(self.operation3Cmbx.currentText())

#___________________________________________________________________________________________________ _handleOperation4Btn
    def _handleOperation4Btn(self):
        """ Passes the selected operation to be performed. """
        self._handleOperation(self.operation4Cmbx.currentText())

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

        self.selectTrack(p)
        p.updateFromNode() # use this opportunity to capture the current state of the Maya node

        dict = p.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

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
            t.updateFromNode() # use this opportunity to capture current state of the Maya node

        t = selectedTracks[-1]
        dict = t.toDict()
        self.refreshTrackwayUI(dict)

        if len(selectedTracks) == 1:
            self.refreshTrackUI(dict)
        else:
            self.clearTrackUI()

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
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.rotationUncertainty = self.rotationUncertaintySbx.value()
        t.updateNode()
        self._closeSession(commit=True)

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

#___________________________________________________________________________________________________ _handleSelectAllAfter
    def _handleSelectAllAfter(self):
        """ Selects all track nodes after the last of the currently-selected track(s). """
        t = self.getLastSelectedTrack()
        if t is None:
           return

        nodes = []
        track = self.getNextTrack(t)
        while track:
             nodes.append(self.getTrackNode(track))
             track = self.getNextTrack(track)

        if len(nodes) > 0:
            cmds.select(nodes)

#___________________________________________________________________________________________________ _handleSelectAllBefore
    def _handleSelectAllBefore(self):
        """ Selects all track nodes up to (but excluding) the first currently-selected track(s). """
        track = self.getFirstSelectedTrack()
        if track is None:
            return

        nodes = []
        track = self.getPreviousTrack(track)
        while track:
            nodes.append(self.getTrackNode(track))
            track = self.getPreviousTrack(track)

        if len(nodes) > 0:
            cmds.select(nodes)

#___________________________________________________________________________________________________ _handleSelectBtn
    def _handleSelectBtn(self):
        """ The various options for track selection are dispatched from here. """
        self._getSession()

        if self.selectionMethodCmbx.currentText() == self.FETCH_TO_CAMERA:
            self._handleFetch()

        elif self.selectionMethodCmbx.currentText() == self.SELECT_BY_NAME:
            self._handleSelectByName()

        elif self.selectionMethodCmbx.currentText() == self.SELECT_BY_INDEX:
            self._handleSelectByIndex()

        elif self.selectionMethodCmbx.currentText() == self.SELECT_ALL_BEFORE:
            self._handleSelectAllBefore()

        elif self.selectionMethodCmbx.currentText() == self.SELECT_ALL_AFTER:
            self._handleSelectAllAfter()

        elif self.selectionMethodCmbx.currentText() == self.SELECT_COMPLETED:
            self._handleSelectCompleted(True)

        elif self.selectionMethodCmbx.currentText() == self.SELECT_INCOMPLETE:
            self._handleSelectCompleted(False)

        elif self.selectionMethodCmbx.currentText() == self.SELECT_MARKED:
            self._handleSelectMarked(True)

        elif self.selectionMethodCmbx.currentText() == self.SELECT_ALL:
            print 'selected' + self.SELECT_ALL
            self._handleSelectAll()

        self.refreshTrackCountsUI()

#___________________________________________________________________________________________________ _handleSelectCadenceCamBtn
    def _handleSelectCadenceCamBtn(self):
        """ Handles the 'CadenceCam' selection. """
        priorSelection = MayaUtils.getSelectedTransforms()

        self.initializeCadenceCam()
        cmds.lookThru('CadenceCam')

        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            self.clearTrackwayUI()
            self.clearTrackUI()
            return

        for t in selectedTracks:
            t.updateFromNode() # use this opportunity to capture current state of the Maya node

        if len(selectedTracks) == 1:
            dict = selectedTracks[0].toDict()
            self.refreshTrackwayUI(dict)
            self.refreshTrackUI(dict)
            self.setCameraFocus()
        else:
            self.clearTrackUI()

        self._closeSession(commit=True)
        MayaUtils.setSelection(priorSelection)

#___________________________________________________________________________________________________ _handleSelectByIndex
    def _handleSelectByIndex(self):
        """ Handles the selection of a gtrack by the index of its catalog entry. """
        tracks = self.getTrackByProperties(index=self.trackIndexLE.text())

        if tracks is None:
            return

        if len(tracks) != 1:
            return

        t = tracks[0]
        self.selectTrack(t)
        self.setCameraFocus()
        self.refreshTrackUI(t.toDict())
#___________________________________________________________________________________________________ _handleSelectByName
    def _handleSelectByName(self):
        """ Handles the selection of a track by name. """
        name   = self.trackNameLE.text()
        tracks = self.getTrackByName(name, **self.getTrackwayPropertiesFromUI())

        if tracks is None:
            return

        if len(tracks) != 1:
            return

        t = tracks[0]
        self.selectTrack(t)
        self.setCameraFocus()
        self.refreshTrackUI(t.toDict())

#___________________________________________________________________________________________________ _handleSelectCompleted
    def _handleSelectCompleted(self, completed=True):
        """ Selects all completed track nodes (those with UIDs in the scene that have their
            COMPLETED source flag set).  Batch this task into sublists due to limitations. This is
            also used with False passed in to select those tracks that are not yet completed. """

        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetUidList, runInMaya=True)

        # turn off all selections
        cmds.select(clear=True)

        # Check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed UID Query',
                'Unable to get UID list from Maya', 'Error')
            return

        # so given a list of UIDs of those track currently in the Maya scene, determine which are
        # completed (or incomplete, as specified by the kwarg), returned as a list of tracks
        uidList = result.payload['uidList']
        tracks = self.getFlaggedTracks(uidList, SourceFlagsEnum.COMPLETED, completed)

        # now get the nodes for those tracks and select them in Maya
        nodes= []
        for t in tracks:
            nodes.append(self.getTrackNode(t))

        if nodes:
            cmds.select(nodes)

#___________________________________________________________________________________________________ _handleSelectMarked
    def _handleSelectMarked(self, marked=True):
        """ Selects all marked track nodes (those with UIDs in the scene that have their
            MARKED source flag set).  Batch this task into sublists due to limitations. """
        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetUidList, runInMaya=True)

        # Check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed UID Query',
                'Unable to get UID list from Maya', 'Error')
            return

        # so we have a list of UIDs of those track currently in the Maya scene
        uidList = result.payload['uidList']
        tracks = self.getFlaggedTracks(uidList, SourceFlagsEnum.MARKED, marked)

        nodes= []
        for t in tracks:
            nodes.append(self.getTrackNode(t))

        if nodes:
            cmds.select(nodes)

#___________________________________________________________________________________________________ _handleSelectPerspectiveBtn
    def _handleSelectPerspectiveBtn(self):
        priorSelection = MayaUtils.getSelectedTransforms()

        cmds.lookThru('persp')

        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            self.clearTrackwayUI()
            self.clearTrackUI()
            return

        for t in selectedTracks:
            t.updateFromNode() # use this opportunity to capture current state of the Maya node

        if len(selectedTracks) == 1:
            dict = selectedTracks[0].toDict()
            self.refreshTrackwayUI(dict)
            self.refreshTrackUI(dict)
            self.setCameraFocus()
        else:
            self.clearTrackUI()

        self._closeSession(commit=True)
        MayaUtils.setSelection(priorSelection)
        self.setCameraFocus()

#___________________________________________________________________________________________________ _handleSetToMeasuredDimnensions
    def _handleSetToMeasuredDimensions(self):
        """ The selected track is assigned the length and width values that were measured in the
        field. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        t = selectedTracks[0]

        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.width  = t.widthMeasured
        t.length = t.lengthMeasured

        # provide default uncertainty values
        t.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
        t.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
        t.rotationUncertainty = self.MODERATE_ROTATiONAL_UNCERTAINTY

        # update the Maya node and the UI
        t.updateNode()
        dict = t.toDict()
        self.selectTrack(t)
        self.refreshTrackUI(dict)
        self.setCameraFocus()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleSetUncertaintyHigh
    def _handleSetUncertaintyHigh(self):
        """ The selected tracks are assigned high uncertainty values. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya nodeb
        t.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_HIGH
        t.widthUncertainty    = self.DIMENSION_UNCERTAINTY_HIGH
        t.rotationUncertainty = self.ROTATION_UNCERTAINTY_HIGH
        t.updateNode()

        # update the Maya node and the UI
        dict = t.toDict()
        self.selectTrack(t)
        self.refreshTrackUI(dict)
        self.setCameraFocus()
        self._closeSession(commit=True)
#___________________________________________________________________________________________________ _handleSetUncertaintyLow
    def _handleSetUncertaintyLow(self):
        """ The selected track is assigned low uncertainty values. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        t = selectedTracks[0]

        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_LOW
        t.widthUncertainty    = self.DIMENSION_UNCERTAINTY_LOW
        t.rotationUncertainty = self.ROTATION_UNCERTAINTY_LOW

        t.updateNode()

        # update the Maya node and the UI
        dict = t.toDict()
        self.selectTrack(t)
        self.refreshTrackUI(dict)
        self.setCameraFocus()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleSetUncertaintyModerate
    def _handleSetUncertaintyModerate(self):
        """ The selected tracks are assigned moderate uncertainty values. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya nodeb
        t.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
        t.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
        t.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE
        t.updateNode()

        # update the Maya node and the UI
        dict = t.toDict()
        self.selectTrack(t)
        self.refreshTrackUI(dict)
        self.setCameraFocus()
        self._closeSession(commit=True)

#___________________________________________________________________________________________________ _handleUnlink
    def _handleUnlink(self):
        """ The 'next' attribute is cleared for the selected track. Unlinking does not
            attempt to relink tracks automatically (one must do it explicitly; see _handleLink). """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.updateFromNode()
            t.next = u''

        t = selectedTracks[-1]
        self.selectTrack(t)
        dict = t.toDict()
        self.refreshTrackUI(dict)
        self.setCameraFocus()
        self._closeSession(commit=True)

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
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.width = self.widthSbx.value()/100.0
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
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.widthUncertainty = self.widthUncertaintySbx.value()/100.0
        t.updateNode()
        self._closeSession(commit=True)

#===================================================================================================
#                                                          H A N D L E R S  - for the Trackway Tab
#___________________________________________________________________________________________________ _handleShowTrackwayBtn
    def _handleShowTrackwayBtn(self, visible=True):
        """ The tracks comprising a trackway are grouped (e.g., into S18_group) and the group is
            added to a corresponding display layer S18_Layer (created if not already available). """
        trackway = self.trackwayCB.currentText()
        print('trackway = %s' % trackway)
        if trackway == '':
            return
        layer = trackway + '_Layer'
        if not cmds.objExists(layer):
            cmds.createDisplayLayer()

            cmds.setAttr('%s.visibility' % layer, visible)

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


#===================================================================================================
#                                                                        M I S C E L L A N E O U S

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
        cmds.viewFit(fitFactor=0.2, animate=True)

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
        """ Closes a session and indicates such by nulling out model and session. """
        if self._session is not None:
            if commit:
                self._session.commit()
            self._session.close()
            return True

        self._session = None
        return False
