# TrackwayManagerWidget.py
# (C)2012-2016
# Scott Ernst and Kent A. Stevens

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from PySide import QtGui
from pyaid.string.StringUtils import StringUtils
from pyglass.widgets.PyGlassWidget import PyGlassWidget
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enums.TrackPropEnum import TrackPropEnum
from cadence.enums.SourceFlagsEnum import SourceFlagsEnum
from cadence.enums.SourceFlagsEnum import SourceFlagsEnumOps
from cadence.enums.AnalysisFlagsEnum import AnalysisFlagsEnum
from cadence.enums.AnalysisFlagsEnum import AnalysisFlagsEnumOps
from cadence.svg.CadenceDrawing import CadenceDrawing
from cadence.views.tools.trackwayManager.TrackwayManager import TrackwayManager
from cadence.views.tools.trackwayManager.Scenario import Scenario

#_______________________________________________________________________________
class TrackwayManagerWidget(PyGlassWidget):
    """ This widget is the primary GUI for interacting with the Maya scene
        representation of a trackway.  It permits selection of tracks
        interactively in Maya and display and editing of their attributes.
        Tracks in Maya are represented by track nodes, each a transform node
        with an additional attribute specifying the UID of that track.  The
        transform's scale, position, and rotation (about Y) are used to
        intrinsically represent track dimensions, position, and orientation.
        Track models are accessed by query based on the UID. """

#===============================================================================

    NO_OP                  = ''
    FETCH_TRACK_BY_NAME    = 'Fetch Track by NAME  << CAUTION'
    FETCH_TRACK_BY_INDEX   = 'Fetch Track by INDEX << CAUTION'
    FETCH_NEXT_INCOMPLETE  = 'Fetch Next INCOMPLETE << CAUTION'
    SELECT_NEXT_INCOMPLETE = 'Select Next INCOMPLETE'
    SELECT_TRACK_BY_NAME   = 'Select Track by NAME'
    SELECT_TRACK_BY_INDEX  = 'Select Track by INDEX'
    SELECT_TRACK_BY_UID    = 'Select Track by UID'
    SELECT_SERIES_BEFORE   = 'Select Series BEFORE'
    SELECT_SERIES_AFTER    = 'Select Series AFTER'
    SELECT_SERIES          = 'Select Track SERIES'
    SELECT_ALL_COMPLETED   = 'Select All COMPLETED'
    SELECT_ALL_INCOMPLETE  = 'Select All INCOMPLETE'
    SELECT_ALL_MARKED      = 'Select All MARKED'

    EXTRAPOLATE_NEXT     = 'Extrapolate NEXT Track'
    EXTRAPOLATE_PREVIOUS = 'Extrapolate PREVIOUS Track'
    INTERPOLATE_TRACK    = 'Interpolate SELECTED Track'
    LINK_SELECTED        = 'LINK Selected Tracks'
    UNLINK_SELECTED      = 'UNLINK Selected Tracks'
    SET_TO_MEASURED      = 'Set to MEASURED Dimensions'
    SET_COMPLETED        = 'Set Selected Tracks COMPLETE'
    SET_ALL_INCOMPLETE   = 'Set All Tracks INCOMPLETE'
    SET_COMPLETE         = 'Set Complete and Get Next'

    SET_UNCERTAINTY_LOW      = 'Set Uncertainties LOW'
    SET_UNCERTAINTY_MODERATE = 'Set Uncertainties MODERATE'
    SET_UNCERTAINTY_HIGH     = 'Set Uncertainties HIGH'
    REDUCE_ROT_UNCERTAINTY   = 'Reduce Rotational Uncertainty'

    LOW      = 'Low'
    MODERATE = 'Moderate'
    HIGH     = 'High'

    BEFORE   = 'Before'
    AFTER    = 'After'
    SELECTED = 'Selected'
    ALL      = 'All'

    DIMENSION_UNCERTAINTY_LOW      = 0.01
    DIMENSION_UNCERTAINTY_MODERATE = 0.02
    DIMENSION_UNCERTAINTY_HIGH     = 0.08

    ROTATION_UNCERTAINTY_LOW      = 6.0
    ROTATION_UNCERTAINTY_MODERATE = 8.0
    ROTATION_UNCERTAINTY_HIGH     = 30.0

    RESOURCE_FOLDER_PREFIX = ['tools']

#_______________________________________________________________________________
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)

        self._uiLock  = False
        self._session = None

        # create an instance of a TrackwayManager to deal with the database and
        # the Maya scene
        self._trackwayManager = TrackwayManager()

        # create an instance of a Scenario to deal with the reading,
        # modification, and writing of trackway scenario files.
        self._scenario = None

        # provide conventional arrow icons for the navigation buttons
        self.firstBtn.setIcon(
            QtGui.QIcon(self.getResourcePath('mediaIcons', 'first.png')))
        self.prevBtn.setIcon(
            QtGui.QIcon(self.getResourcePath('mediaIcons', 'prev.png')))
        self.nextBtn.setIcon(
            QtGui.QIcon(self.getResourcePath('mediaIcons', 'next.png')))
        self.lastBtn.setIcon(
            QtGui.QIcon(self.getResourcePath('mediaIcons', 'last.png')))

        # in the Track tab:
        self.widthSbx.valueChanged.connect(self.handleWidthSbx)
        self.widthSbx.setAccelerated(True)
        self.lengthSbx.valueChanged.connect(self.handleLengthSbx)
        self.lengthSbx.setAccelerated(True)
        self.widthUncertaintySbx.valueChanged.connect(
            self.handleWidthUncertaintySbx)
        self.lengthUncertaintySbx.valueChanged.connect(
            self.handleLengthUncertaintySbx)
        self.rotationSbx.valueChanged.connect(self.handleRotationSbx)
        self.rotationSbx.setAccelerated(True)
        self.rotationUncertaintySbx.valueChanged.connect(
            self.handleRotationUncertaintySbx)
        self.completedCkbx.clicked.connect(self.handleCompletedCkbx)
        self.hiddenCkbx.clicked.connect(self.handleHiddenCkbx)
        self.lockedCkbx.clicked.connect(self.handleLockedCkbx)
        self.markedCkbx.clicked.connect(self.handleMarkedCkbx)
        self.ignorePaceCkbx.clicked.connect(self.handleIgnorePaceCkbx)
        self.ignoreStrideCkbx.clicked.connect(self.handleIgnoreStrideCkbx)
        self.lengthRatioSbx.valueChanged.connect(self.handleLengthRatioSbx)
        self.noteLE.textChanged.connect(self.handleNoteLE)
        self.countsBtn.clicked.connect(self.handleCountsBtn)
        self.pullBtn.clicked.connect(self.handlePullBtn)
        self.firstBtn.clicked.connect(self.handleFirstBtn)
        self.prevBtn.clicked.connect(self.handlePrevBtn)
        self.nextBtn.clicked.connect(self.handleNextBtn)
        self.lastBtn.clicked.connect(self.handleLastBtn)
        self.selectCadenceCamBtn.clicked.connect(
            self.handleSelectCadenceCamBtn)
        self.selectPerspectiveBtn.clicked.connect(
            self.handleSelectPerspectiveBtn)

        trackSelectionMethods = (
            self.NO_OP,
            self.SELECT_TRACK_BY_NAME,
            self.SELECT_TRACK_BY_INDEX,
            self.SELECT_TRACK_BY_UID,
            self.FETCH_TRACK_BY_NAME,
            self.FETCH_TRACK_BY_INDEX,
            self.FETCH_NEXT_INCOMPLETE,
            self.SELECT_NEXT_INCOMPLETE,
            self.SELECT_SERIES_BEFORE,
            self.SELECT_SERIES_AFTER,
            self.SELECT_SERIES,
            self.SELECT_ALL_COMPLETED,
            self.SELECT_ALL_INCOMPLETE,
            self.SELECT_ALL_MARKED)

        self.selectBy1Cmbx.addItems(trackSelectionMethods)
        self.selectBy1Cmbx.setCurrentIndex(0)
        self.select1Btn.clicked.connect(self.handleSelect1Btn)
        self.selectBy2Cmbx.addItems(trackSelectionMethods)
        self.selectBy2Cmbx.setCurrentIndex(0)
        self.select2Btn.clicked.connect(self.handleSelect2Btn)

        trackOperationMethods = (
            self.NO_OP,
            self.EXTRAPOLATE_NEXT,
            self.EXTRAPOLATE_PREVIOUS,
            self.INTERPOLATE_TRACK,
            self.SET_TO_MEASURED,
            self.SET_UNCERTAINTY_LOW,
            self.SET_UNCERTAINTY_MODERATE,
            self.SET_UNCERTAINTY_HIGH,
            self.REDUCE_ROT_UNCERTAINTY,
            self.LINK_SELECTED,
            self.UNLINK_SELECTED,
            self.SET_COMPLETED,
            self.SET_ALL_INCOMPLETE,
            self.SET_COMPLETE )

        # set up a bank of three combo boxes of operations for convenience
        self.operation1Cmbx.addItems(trackOperationMethods)
        self.operation1Cmbx.setCurrentIndex(0)
        self.operation1Btn.clicked.connect(self.handleOperation1Btn)
        self.operation2Cmbx.addItems(trackOperationMethods)
        self.operation2Cmbx.setCurrentIndex(0)
        self.operation2Btn.clicked.connect(self.handleOperation2Btn)
        self.operation3Cmbx.addItems(trackOperationMethods)
        self.operation3Cmbx.setCurrentIndex(0)
        self.operation3Btn.clicked.connect(self.handleOperation3Btn)

        # next, in the Trackway tab:
        self.showTrackwayBtn.clicked.connect(self.handleShowTrackwayBtn)
        self.hideTrackwayBtn.clicked.connect(self.handleHideTrackwayBtn)
        self.selectTrackwayBtn.clicked.connect(self.handleSelectTrackwayBtn)
        self.updateLayersBtn.clicked.connect(self.handleUpdateLayersBtn)
        self.showAllTrackwaysBtn.clicked.connect(self.handleShowAllTrackwaysBtn)
        self.hideAllTrackwaysBtn.clicked.connect(self.handleHideAllTrackwaysBtn)
        self.selectAllTrackwaysBtn.clicked.connect(
            self.handleSelectAllTrackwaysBtn)
        self.exportAllTrackwaysBtn.clicked.connect(
            self.handleExportAllTrackwaysBtn)
        self.erasePathsBtn.clicked.connect(self.handleErasePathsBtn)

        # and next, in the Tracksite tab:
        self.trackSiteIndexSbx.valueChanged.connect(
            self.handleTrackSiteIndexSbx)
        self.svgFileNameLE.textChanged.connect(self.handleSvgNameLE)
        self.openSvgFileBtn.clicked.connect(self.handleSvgOpenBtn)
        self.saveSvgFileBtn.clicked.connect(self.handleSvgSaveBtn)
        self.addSelectedBtn.clicked.connect(self.handleSvgAddSelectedBtn)

        self.currentDrawing = None

        # populate the tracksite data based on the initial value of the index
        self.handleTrackSiteIndexSbx()

        # set up the UI and support data structures for a trackway scenario
        # first, clone the original navigation in the tracks tab:
        self.firstBtn2.setIcon(QtGui.QIcon(
            self.getResourcePath('mediaIcons', 'first.png')))
        self.prevBtn2.setIcon( QtGui.QIcon(
            self.getResourcePath('mediaIcons', 'prev.png')))
        self.nextBtn2.setIcon( QtGui.QIcon(
            self.getResourcePath('mediaIcons', 'next.png')))
        self.lastBtn2.setIcon( QtGui.QIcon(
            self.getResourcePath('mediaIcons', 'last.png')))

        self.firstBtn2.clicked.connect(self.handleFirstTokenBtn)
        self.prevBtn2.clicked.connect(self.handlePrevTokenBtn)
        self.nextBtn2.clicked.connect(self.handleNextTokenBtn)
        self.lastBtn2.clicked.connect(self.handleLastTokenBtn)

        self.xSbx.valueChanged.connect(self.handleXSbx)
        self.xSbx.setAccelerated(True)
        self.ySbx.valueChanged.connect(self.handleYSbx)
        self.ySbx.setAccelerated(True)
        self.dxSbx.valueChanged.connect(self.handleDxSbx)
        self.dySbx.valueChanged.connect(self.handleDySbx)

        self.pullTokenBtn.clicked.connect(self.handlePullSelectedTokenBtn)
        self.pullAllTokensBtn.clicked.connect(self.handlePullAllTokensBtn)

        self.proxyUncertaintyCmbx.addItems((
            self.LOW, self.MODERATE, self.HIGH))
        self.proxyUncertaintyCmbx.setCurrentIndex(2)
        self.selectedVersusAllCmbx.addItems((self.SELECTED, self.ALL))
        self.selectedVersusAllCmbx.setCurrentIndex(0)
        self.setProxyUncertaintyBtn.clicked.connect(
            self.handleSetProxyUncertaintyBtn)

        self.changeTokenUidBtn.clicked.connect(self.handleChangeTokenUidBtn)

        self.deleteTokenBtn.clicked.connect(self.handleDeleteTokenBtn)

        self.selectCadenceCamBtn2.clicked.connect(
            self.handleSelectCadenceCamBtn)
        self.selectPerspectiveBtn2.clicked.connect(
            self.handleSelectPerspectiveBtn)
        self.pullBtn2.clicked.connect(self.handlePullBtn)

        self.initScenarioBtn.clicked.connect(self.handleInitScenarioBtn)
        self.loadScenarioBtn.clicked.connect(self.handleLoadScenarioBtn)
        self.saveScenarioBtn.clicked.connect(self.handleSaveScenarioBtn)

        self.beforeAfterCmbx.addItems([self.BEFORE, self.AFTER])
        self.insertTokenBtn.clicked.connect(self.handleInsertTokenBtn)

        self.consoleTE.setText('')

#===============================================================================
#                                                                   P U B L I C
#
#_______________________________________________________________________________
    def enableTrackUI(self, enable =True):
        """ The track ui is either enabled (if passed True) or disabled (if
            passed False). This is useful for tracks that are locked to prevent
            accidental modification. """

        self.widthLbl.setEnabled(enable)
        self.widthSbx.setEnabled(enable)
        self.widthUncertaintySbx.setEnabled(enable)

        self.lengthLbl.setEnabled(enable)
        self.lengthSbx.setEnabled(enable)
        self.lengthUncertaintySbx.setEnabled(enable)

        self.rotationSbx.setEnabled(enable)
        self.rotationUncertaintySbx.setEnabled(enable)

        self.completedCkbx.setEnabled(enable)
        self.markedCkbx.setEnabled(enable)
        self.hiddenCkbx.setEnabled(enable)
        self.ignorePace.setEnabled(enable)
        self.ignoreStride.setEnabled(enable)

        self.lengthRatioSbx.setEnabled(enable)

        self.noteLE.setEnabled(enable)
        self.trackNameLE.setEnabled(enable)
        self.indexLE.setEnabled(enable)

#===============================================================================
#                                             T R A C K  U I  U T I L I T I E S
#
#_______________________________________________________________________________
    def clearTrackUI(self):
        """ Clears out the text fields associated with the track parameters in
            the UI. This is called by several handlers that invalidate the track
             information in the UI. """
        self.widthLbl.setText('Width:  [%4s]' % '')
        self.widthSbx.setValue(0)
        self.widthUncertaintySbx.setValue(0)

        self.lengthLbl.setText('Length: [%4s]' % '')
        self.lengthSbx.setValue(0)
        self.lengthUncertaintySbx.setValue(0)

        self.rotationSbx.setValue(0)
        self.rotationUncertaintySbx.setValue(0)

        self.completedCkbx.setChecked(False)
        self.lockedCkbx.setChecked(False)
        self.markedCkbx.setChecked(False)
        self.hiddenCkbx.setChecked(False)
        self.ignorePaceCkbx.setChecked(False)
        self.ignoreStrideCkbx.setChecked(False)

        self.lengthRatioSbx.setValue(0)

        self.noteLE.setText(u'')
        self.trackNameLE.setText(u'')
        self.indexLE.setText(u'')
        self.uidLE.setText(u'')

#_______________________________________________________________________________
    def clearTrackSiteUI(self):
        """ This clears the track site data in the Trackways tab. This method is
            used only by handleTrackSiteIndexSbx. """

        self.trackSiteNameLbl.setText(u'')
        self.federalEastLbl.setText(u'')
        self.federalNorthLbl.setText(u'')
        self.mapLeftLbl.setText(u'')
        self.mapTopLbl.setText(u'')
        self.mapWidthLbl.setText(u'')
        self.mapHeightLbl.setText(u'')
        self.xFedLbl.setText(u'')
        self.yFedLbl.setText(u'')
        self.transXLbl.setText(u'')
        self.transZLbl.setText(u'')
        self.rotXLbl.setText(u'')
        self.rotYLbl.setText(u'')
        self.rotZLbl.setText(u'')
        self.scaleLbl.setText(u'')

#_______________________________________________________________________________
    def clearTrackwayUI(self):
        """ Clears the banner at the top of the UI. This is called by a few
            handlers that invalidate the trackway information in the UI (such as
            handleSelectCompleted, which selects all tracks that are completed,
            which might involve multiple trackways. """

        self.siteLE.setText('')
        self.yearLE.setText('')
        self.sectorLE.setText('')
        self.levelLE.setText('')
        self.trackwayLE.setText('')
        self.indexLE.setText('')
        self.uidLE.setText('')

#_______________________________________________________________________________
    def refreshTrackUI(self, props):
        """ The track properties aspect of the UI display are updated based on
            the dictionary props for a given track model instance. """

        width               = props[TrackPropEnum.WIDTH.name]
        widthMeasured       = props[TrackPropEnum.WIDTH_MEASURED.name]
        length              = props[TrackPropEnum.LENGTH.name]
        lengthMeasured      = props[TrackPropEnum.LENGTH_MEASURED.name]
        widthUncertainty    = props[TrackPropEnum.WIDTH_UNCERTAINTY.maya]
        lengthUncertainty   = props[TrackPropEnum.LENGTH_UNCERTAINTY.maya]
        rotation            = props[TrackPropEnum.ROTATION.name]
        rotationUncertainty = props[TrackPropEnum.ROTATION_UNCERTAINTY.name]
        sourceFlags         = props[TrackPropEnum.SOURCE_FLAGS.name]
        analysisFlags       = props[TrackPropEnum.ANALYSIS_FLAGS.name]
        hidden              = props[TrackPropEnum.HIDDEN.name]
        lengthRatio         = props[TrackPropEnum.LENGTH_RATIO.name]
        note                = props[TrackPropEnum.NOTE.name]
        left                = props[TrackPropEnum.LEFT.name]
        pes                 = props[TrackPropEnum.PES.name]
        number              = props[TrackPropEnum.NUMBER.name]
        index               = props[TrackPropEnum.INDEX.name]
        uid                 = props[TrackPropEnum.UID.name]

        self.widthSbx.setValue(100.0*width)
        if widthMeasured is not None:
            self.widthLbl.setText('Width: [%2.0f]' % (100.0*widthMeasured))
        self.lengthSbx.setValue(100.0*length)
        if lengthMeasured is not None:
            self.lengthLbl.setText('Length: [%2.0f]' % (100.0*lengthMeasured))
        self.widthUncertaintySbx.setValue(100.0*widthUncertainty)
        self.lengthUncertaintySbx.setValue(100.0*lengthUncertainty)

        if rotation < 0.0:
            rotation += 360.0
        self.rotationSbx.setValue(rotation)
        self.rotationUncertaintySbx.setValue(rotationUncertainty)

        # set the checkboxes 'Completed', 'Locked', and 'Marked' according to
        # the source flags
        locked    = SourceFlagsEnumOps.get(sourceFlags, SourceFlagsEnum.LOCKED)
        marked    = SourceFlagsEnumOps.get(sourceFlags, SourceFlagsEnum.MARKED)
        completed = SourceFlagsEnumOps.get(
            sourceFlags, SourceFlagsEnum.COMPLETED)
        self.lockedCkbx.setChecked(locked)
        self.markedCkbx.setChecked(marked)
        self.completedCkbx.setChecked(completed)

        # set the ignore pace and stride checkboxes according to the analysis
        # flags
        pace = AnalysisFlagsEnumOps.get(
            analysisFlags, AnalysisFlagsEnum.IGNORE_PACE)
        stride = AnalysisFlagsEnumOps.get(
            analysisFlags, AnalysisFlagsEnum.IGNORE_STRIDE)
        self.ignorePaceCkbx.setChecked(pace)
        self.ignoreStrideCkbx.setChecked(stride)

        # finish off a few more fields
        self.hiddenCkbx.setChecked(hidden)
        self.lengthRatioSbx.setValue(lengthRatio)
        self.noteLE.setText(note)

        name = (u'L' if left else u'R') +\
               (u'P' if pes else u'M') +\
               number if number else u'-'
        self.trackNameLE.setText(name)
        self.indexLE.setText(StringUtils.toUnicode(index))
        self.uidLE.setText(StringUtils.toUnicode(uid))

        # now, depending on whether this track is locked or unlocked,
        # disable/enable the UI
        # locked = SourceFlagsEnumOps.get(f, SourceFlagsEnum.LOCKED)
        # if locked:
        #     self.enableTrackUI(False)
        # else:
        #     self.enableTrackUI(True)

#_______________________________________________________________________________
    def refreshTrackSiteUI(self, siteMap):
        """ The data displayed for the given track site index is updated. Note
            that the siteMap argument is a Tracks_SiteMap model instance. """

        self.trackSiteNameLbl.setText(siteMap.filename)
        self.federalEastLbl.setText(StringUtils.toUnicode(siteMap.federalEast))
        self.federalNorthLbl.setText(
            StringUtils.toUnicode(siteMap.federalNorth))
        self.mapLeftLbl.setText(StringUtils.toUnicode(siteMap.left))
        self.mapTopLbl.setText(StringUtils.toUnicode(siteMap.top))
        self.mapWidthLbl.setText(StringUtils.toUnicode(siteMap.width))
        self.mapHeightLbl.setText(StringUtils.toUnicode(siteMap.height))
        self.xFedLbl.setText(StringUtils.toUnicode(siteMap.xFederal))
        self.yFedLbl.setText(StringUtils.toUnicode(siteMap.yFederal))
        self.transXLbl.setText(StringUtils.toUnicode(siteMap.xTranslate))
        self.transZLbl.setText(StringUtils.toUnicode(siteMap.zTranslate))
        self.rotXLbl.setText(StringUtils.toUnicode(siteMap.xRotate))
        self.rotYLbl.setText(StringUtils.toUnicode(siteMap.yRotate))
        self.rotZLbl.setText(StringUtils.toUnicode(siteMap.zRotate))
        self.scaleLbl.setText(StringUtils.toUnicode(siteMap.scale))

#_______________________________________________________________________________
    def refreshTrackwayUI(self, dict):
        """ The trackway UI is populated with values based on the specified
            properties. """

        site = dict.get(TrackPropEnum.SITE.name)
        if not site:
            site = ''
        self.siteLE.setText(site)

        level = dict.get(TrackPropEnum.LEVEL.name)
        if not level:
            level = ''
        self.levelLE.setText(level)

        year = dict.get(TrackPropEnum.YEAR.name)
        if not year:
            year = ''
        self.yearLE.setText(year)

        sector = dict.get(TrackPropEnum.SECTOR.name)
        if not sector:
            sector = ''
        self.sectorLE.setText(sector)

        # compose the trackway name (such as S18 for type 'S' for sauropod, plus
        # the trackway number 18)
        type   = dict.get(TrackPropEnum.TRACKWAY_TYPE.name)
        number = dict.get(TrackPropEnum.TRACKWAY_NUMBER.name)
        if type and number:
            trackway = type + number
        else:
            trackway = ''
        self.trackwayLE.setText(trackway)

#_______________________________________________________________________________
    def refreshTrackCountsUI(self):
        """ Run a script to return a list of all Maya Track Nodes so we can get
            a count of both the total number of tracks in the scene and of those
            that are completed. """

        uidList = self._trackwayManager.getUidList()

        if not uidList:
            totalTrackCount = 0
            completedCount  = 0
            selectedCount   = 0
        else:
            totalTrackCount = len(uidList)
            completedTracks = self._trackwayManager.getCompletedTracks(
                True, uidList)
            completedCount  = len(completedTracks) if completedTracks else 0
            selectedTracks  = self._trackwayManager.getSelectedTracks()
            selectedCount   = len(selectedTracks) if selectedTracks else 0

        # Display the total number of tracks currently in the Maya scene
        self.totalTrackCountLbl.setText(
            'Total:  ' + StringUtils.toUnicode(totalTrackCount))

        # Now determine how many tracks have their COMPLETED source flag set
        self.completedTrackCountLbl.setText(
            'Completed:  ' + StringUtils.toUnicode(completedCount))

        # And show how many are currently selected
        self.selectedTrackCountLbl.setText(
            'Selected:  ' + StringUtils.toUnicode(selectedCount))

#_______________________________________________________________________________
    def getTrackwayPropertiesFromUI(self):
        """ Returns a dictionary of trackway properties, extracted from the UI.
            The trackway type and number are included only if the trackway line
            edit field is non-empty."""

        props = {
            TrackPropEnum.SITE.name:self.siteLE.text(),
            TrackPropEnum.YEAR.name:self.yearLE.text(),
            TrackPropEnum.SECTOR.name:self.sectorLE.text(),
            TrackPropEnum.LEVEL.name:self.levelLE.text() }

        trackway = self.trackwayLE.text()
        if trackway:
            props[TrackPropEnum.TRACKWAY_TYPE.name] = self.trackwayLE.text()[0]
            props[TrackPropEnum.TRACKWAY_NUMBER.name] =\
                self.trackwayLE.text()[1:]

        return props

#===============================================================================
#                                                               H A N D L E R S
#_______________________________________________________________________________
    def handleCompletedCkbx(self):
        """ The COMPLETED source flag for the selected track (or tracks) is set
            or cleared, based on the value of the checkbox. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]
        track.updateFromNode()
        track.completed = self.completedCkbx.isChecked()
        track.updateNode()

        self.refreshTrackUI(track.toDict())
        self.refreshTrackCountsUI()

        # finally, if is set to completed, then lock it (and that requires
        # unlocking to set back to uncompleted state, as a safety precaution)
#       if self.completedCkbx.isChecked():
#           self.lockedCkbx.setChecked(True)

        self._trackwayManager.closeSession(commit=True)

        self._unlock()

#_______________________________________________________________________________
    def handleCountsBtn(self):
        """ This updates the total number of tracks in the scene and the number
            completed. """

        if not self._lock():
            return

        self.refreshTrackCountsUI()

        self._unlock()

#_______________________________________________________________________________
    def handleErasePathsBtn(self):
        """ Deletes all curves representing paths (e.g., connecting a given
            track series). """

        if not self._lock():
            return

        self._trackwayManager.deleteAllPaths()

        self._unlock()

#_______________________________________________________________________________
    def handleExportAllTrackwaysBtn(self):
        """ tbd """

        if not self._lock():
            return

        # to be determined

        self._unlock()

#_______________________________________________________________________________
    def handleExtrapolateNext(self):
        """ Given at least two tracks in a series, this method allows the next
            track to be placed in a straight line extrapolation of the given
            track and its previous track. The next track node is also given the
            averaged orientation and length and width uncertainties associated
            with the last two tracks. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        # extrapolate from the last of possibly multiple selected tracks
        t = selectedTracks[-1]
        p = self._trackwayManager.getPreviousTrack(t)

        # complete the current track
        t.completed = True

        # the first track must be in place, but if attempting to extrapolate the
        # second track based on just the first track, there is no displacement
        # yet on which to estimate forward progress (so drag that track manually
        # off of the first track).
        if p is None:
            p = t

        # and make sure there is a next track to extrapolate
        n = self._trackwayManager.getNextTrack(t)
        if n is None:
            PyGlassBasicDialogManager.openOk(
                self,
                'No next track to extrapolate!',
                '%s is the last in this series' % t.name)
            self._unlock()
            return

        # take a linear step forward based on the number of steps in between
        # the last two (p and t) and between t and n.  First, compute tp, the
        # difference in track number from p to t
        tp = int(t.number) - int(p.number)

        # deal with the degenerate case of no previous track p, wherein p had
        # been set to t above
        if tp == 0:
            tp = 1

        # determine the equivalent displacements in x and z for one step (since
        # the distance from p to t might represent multiple intermediate steps
        # that were never recorded) note that if the previous point is at (0, 0)
        # then don't extrapolate n; just make the delta's dx and dy both zero
        # and leave n coincident with t.
        if p.x == 0 and p.z == 0:
            dx = 0
            dz = 0
        else:
            dx = float(t.x - p.x)/tp
            dz = float(t.z - p.z)/tp

        # now to extrapolate from t to n, we also have to be concerned with
        # possible missing intervening steps, so compute the difference in track
        # number from n to t
        nt  = int(n.number) - int(t.number)
        n.x = t.x + nt*dx
        n.z = t.z + nt*dz

        # if track width was not measured originally, inherit t's width and
        # posit high uncertainty but be careful to check if t's values were
        # measured in the first place
        if n.widthMeasured == 0.0:
            n.width            = t.width
            #n.widthUncertainty = self.DIMENSION_UNCERTAINTY_MODERATE
            n.widthUncertainty = t.widthUncertainty
        else:
            n.width            = n.widthMeasured
            n.widthUncertainty = t.widthUncertainty

        # similarly for track length, based on whether it was measured
        # originally
        if n.lengthMeasured == 0.0:
            n.length            = t.length
            #n.lengthUncertainty = self.DIMENSION_UNCERTAINTY_MODERATE
            n.lengthUncertainty = t.lengthUncertainty
        else:
            n.length            = n.lengthMeasured
            n.lengthUncertainty = t.lengthUncertainty

        # and presume rotational uncertainty will be high if both measured
        # values are zero
        if n.widthMeasured == 0.0 and n.lengthMeasured == 0.0:
            #n.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE
            n.rotationUncertainty = t.rotationUncertainty
        else:
            n.rotationUncertainty = t.rotationUncertainty

        # assign to the next track the length ratio and rotation of the current
        # track
        n.lengthRatio = t.lengthRatio
        n.rotation    = t.rotation
        n.completed   = False
        n.locked      = False

        # update the Maya node and the UI
        n.updateNode()
        self._trackwayManager.selectTrack(n)
        self.refreshTrackUI(n.toDict())
        self._trackwayManager.setCameraFocus()

        self.refreshTrackCountsUI()
        self._trackwayManager.closeSession(commit=True)

        self._unlock()

#_______________________________________________________________________________
    def handleExtrapolatePrevious(self):
        """ Given at least two tracks in a series, this method allows the
            previous track to be placed in a straight line extrapolation of the
            given track and its next track. The previous track node is also
            given the averaged orientation and length and width uncertainties
            associated with the the next two tracks. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        # extrapolate from the first of possibly multiple selected tracks
        t = selectedTracks[0]
        n = self._trackwayManager.getNextTrack(t)

        # the first track must be in place, but if attempting to extrapolate the
        # second track based on just the first track, there is no displacement
        # yet on which to estimate forward progress (so drag that track manually
        # off of the first track).
        if n is None:
            n = t

        # and make sure there is a previous track to extrapolate
        p = self._trackwayManager.getPreviousTrack(t)
        if p is None:
            PyGlassBasicDialogManager.openOk(
                 self,
                'No previous track',
                '%s is the first in this series' % t.name)
            self._unlock()
            return

        # take a linear step backward based on the number of steps in between
        # the next two (t and n) and between p and t.  First compute nt, the
        # difference in track number from t to n
        nt = int(n.number) - int(t.number)

        # deal with the degenerate case of no next track n, wherein n had been
        # set to t above
        if nt == 0:
            nt = 1

        # determine the equivalent displacements in x and z for one step (since
        # the distance from t to n might represent multiple intermediate steps
        # that were never recorded) note that if the next point is at (0, 0)
        # then don't extrapolate p; just make the delta's dx and dy both zero
        # and leave p coincident with t.
        if n.x == 0 and n.z == 0:
            dx = 0
            dz = 0
        else:
            dx = float(n.x - t.x)/nt
            dz = float(n.z - t.z)/nt

        # now to extrapolate from t back to p, we also have to be concerned with
        # possible missing intervening steps, so compute the difference in track
        # number from p to t
        nt  = int(t.number) - int(p.number)
        p.x = t.x - nt*dx
        p.z = t.z - nt*dz

        # if track width was not measured originally, inherit t's width and
        # posit high uncertainty but be careful to check if t's values were
        # measured in the first place
        if p.widthMeasured == 0.0:
            p.width            = t.width
            p.widthUncertainty = self.DIMENSION_UNCERTAINTY_MODERATE
        else:
            p.width            = p.widthMeasured
            p.widthUncertainty = t.widthUncertainty

        # similarly for track length, based on whether it was measured
        # originally
        if p.lengthMeasured == 0.0:
            p.length            = t.length
            p.lengthUncertainty = self.DIMENSION_UNCERTAINTY_MODERATE
        else:
            p.length            = p.lengthMeasured
            p.lengthUncertainty = t.lengthUncertainty

        # and presume rotational uncertainty will be high if both measured
        # values are zero
        if p.widthMeasured == 0.0 and p.lengthMeasured == 0.0:
            p.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE
        else:
            p.rotationUncertainty = t.rotationUncertainty

        # assign to the next track the length ratio and rotation of the current
        # track
        p.lengthRatio = t.lengthRatio
        p.rotation    = t.rotation

        # update the Maya node and the UI
        p.updateNode()
        self._trackwayManager.selectTrack(p)
        self.refreshTrackUI(p.toDict())
        self._trackwayManager.setCameraFocus()
        p.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleFetchByName(self):
        """ This fetches the track specified by the trackwayUI banner, and
            translates that track directly under the CadenceCam. """

        if not self._lock():
            return

        # get the track based on name from the UI and its trackway properties
        # (should be unique)
        name   = self.trackNameLE.text()
        tracks = self._trackwayManager.getTrackByName(
            name, **self.getTrackwayPropertiesFromUI())

        # give up if the specified track is not found
        if not tracks or len(tracks) > 1:
            PyGlassBasicDialogManager.openOk(
                self,
                'Unsuccessful',
                'Requested track not found',
                'Error')
            self._unlock()
            return

        track = tracks[0]

        # if track length or width (or both) were not measured originally,
        # indicate high uncertainties
        if track.widthMeasured == 0.0 or track.lengthMeasured == 0.0:
            track.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
            track.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
            track.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE
        else:
            track.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
            track.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
            track.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE

        # set this track's position to that of the CadenceCam
        track.x, track.z = self._trackwayManager.getCadenceCamLocation()
        track.updateNode()

        # and select it
        self._trackwayManager.selectTrack(track, setFocus=False)

        # and refresh the UI
        self.refreshTrackUI(track.toDict())
        self.refreshTrackwayUI(track.toDict())

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleFetchByIndex(self):
        """ This fetches the track specified by the index in the trackwayUI
            banner, and translates that track to place it directly under the
            CadenceCam. """

        if not self._lock():
            return

        # with that out of the way, now attempt to get the track instance with
        # the specified index
        tracks = self._trackwayManager.getTracksByProperties(
            index=self.indexLE.text())

        # just give up if no unique track with that specified index is found
        if not tracks or len(tracks) > 1:
            PyGlassBasicDialogManager.openOk(
                self,
               'Unsuccessful',
               'Requested track not found',
               'Error')
            self._unlock()
            return

        track = tracks[0]

        # if track length or width (or both) were not measured originally,
        # posit high uncertainties
        if track.widthMeasured == 0.0 or track.lengthMeasured == 0.0:
            track.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
            track.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
            track.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE
        else:
            track.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
            track.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
            track.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE

        # set this track's position to that of the CadenceCam
        track.x, track.z = self._trackwayManager.getCadenceCamLocation()

        track.updateNode()
        props = track.toDict()

        # and refresh the UI
        self.refreshTrackwayUI(props)
        self.refreshTrackUI(props)

        # and select it
        self._trackwayManager.selectTrack(track, setFocus=False)

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleFetchNextIncomplete(self):
        """ The next incomplete track is translated to place that track directly
            under the CadenceCam. """

        if not self._lock():
            return

        incompleteTracks = self._trackwayManager.getCompletedTracks(False)

        if not incompleteTracks:
            PyGlassBasicDialogManager.openOk(
                self,
               'None',
               'All tracks are complete')
            self._unlock()
            return

        track = incompleteTracks[0]
        # set this track's position to that of the CadenceCam
        track.x, track.z = self._trackwayManager.getCadenceCamLocation()

        track.updateNode()
        props = track.toDict()

        # and refresh the UI
        self.refreshTrackwayUI(props)
        self.refreshTrackUI(props)

        # and select it
        self._trackwayManager.selectTrack(track, setFocus=False)
        self._unlock()

#_______________________________________________________________________________
    def handleFirstBtn(self):
        """ Get the first track, select the corresponding node, and focus the
            camera on it. """

        if not self._lock():
            return

        track = self._trackwayManager.getFirstTrack()
        if track is None:
            self._unlock()
            return

        self._trackwayManager.selectTrack(track)

        dict = track.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleHideAllTrackwaysBtn(self):
        """ This sets all layers invisible. """

        if not self._lock():
            return

        self._trackwayManager.setAllLayersVisible(False)
        self._unlock()

#_______________________________________________________________________________
    def handleHideTrackwayBtn(self):
        """ This hides the layer specified by the current value in the trackway
            combo box. """

        if not self._lock():
            return

        trackwayName = self.trackwayCmbx.currentText()
        self._trackwayManager.showTrackway(trackwayName, visible=False)

        self._unlock()

#_______________________________________________________________________________
    def handleHiddenCkbx(self):
        """ The selected track has its HIDDEN flag set (or cleared). """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        if not track.hidden:
            # if the selected track is not already hidden, set hidden if
            # confirmed
            result = PyGlassBasicDialogManager.openYesNo(
                self,
                u'CONFIRMATION REQUIRED',
                u'Are you sure you want to set this track to HIDDEN?',
                False)
            if result:
                track.hidden = True
        else:
            # if the selected track is already hidden, set it visible if
            # confirmed
            result = PyGlassBasicDialogManager.openYesNo(
                self,
                u'CONFIRMATION REQUIRED',
                u'This track is HIDDEN.  Do you wish to make it visible?',
                False)
            if result:
                track.hidden = False

        # if this leaves the track hidden, place it back at the origin, and
        # unoriented
        if track.hidden:
            track.x        = 0.0
            track.z        = 0.0
            track.rotation = 0.0

        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()


#_______________________________________________________________________________
    def handleIgnorePaceCkbx(self):
        """ This track has its IGNORE_PACE analysis flag set or cleared, based
            on the value of the checkbox. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        track.ignorePace = self.ignorePaceCkbx.isChecked()
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleIgnoreStrideCkbx(self):
        """ This track has its IGNORE_STRIDE analysis flag set or cleared, based
            on the value of the checkbox. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        track.ignoreStride = self.ignoreStrideCkbx.isChecked()
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleInterpolate(self):
        """ Based on a previous and next tracks to a given (single) selected
            track node t, the parameters are interpolated. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        track = selectedTracks[0]
        # use this opportunity to capture the current state of the Maya node        
        track.updateFromNode()

        p = self._trackwayManager.getPreviousTrack(track)
        if p is None:
            self._unlock()
            return

        next = self._trackwayManager.getNextTrack(track)
        if next is None:
            self._unlock()
            return

        track.x = 0.5*(p.x + next.x)
        track.z = 0.5*(p.z + next.z)
        track.width = 0.5*(p.width + next.width)
        track.length = 0.5*(p.length + next.length)
        track.rotation = 0.5*(p.rotation + next.rotation)
        track.lengthRatio = 0.5*(p.lengthRatio + next.lengthRatio)
        track.widthUncertainty = 0.5*(
            p.widthUncertainty + next.widthUncertainty)
        track.lengthUncertainty = 0.5*(
            p.lengthUncertainty + next. lengthUncertainty)
        track.rotationUncertainty = 0.5*(
            p.rotationUncertainty + next. rotationUncertainty)

        # update the Maya node and the UI
        track.updateNode()
        self._trackwayManager.selectTrack(track)
        self.refreshTrackUI(track.toDict())
        self._trackwayManager.setCameraFocus()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleLastBtn(self):
        """ Get the last track, select the corresponding node, focus the camera
            on it, and update the UIs"""

        if not self._lock():
            return

        track = self._trackwayManager.getLastTrack()
        if track is None:
            self._unlock()
            return

        self._trackwayManager.selectTrack(track)
        dict = track.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleLengthSbx(self):
        """ The length of the selected track is adjusted. Length is stored in
            the database in fractional meters but send to Maya in cm and
            displayed in integer cm units."""

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        track.length = self.lengthSbx.value()/100.0
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleLengthUncertaintySbx(self):
        """ The length uncertainty of the selected track is adjusted. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]
        track.lengthUncertainty = self.lengthUncertaintySbx.value()/100.0
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleLengthRatioSbx(self):
        """ The ratio from 0.0 to 1.0 representing fraction of distance from the
            anterior' extreme of the track to the 'center' (point of greatest
            width). """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        track.lengthRatio = self.lengthRatioSbx.value()

        # I used to like this relative motion (but now I think it is better
        # to keep x, z fixed
        # deltaL = t.lengthRatio*t.length
        # deltaS = -100.0*(t.lengthRatio*t.length - deltaL)
        # theta  = math.radians(t.rotation)
        # deltaX = deltaS*math.sin(theta)
        # deltaZ = deltaS*math.cos(theta)
        # t.x = t.x + deltaX
        # t.z = t.z + deltaZ
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def  handleLink(self):
        """ Two or more tracks are linked by selecting them in Maya (in the
            intended order) then, for each track, assigning the UID of each
            successive track to the 'next' attribute for that track.  By
            convention, the last such track node is selected. Note that we may
            want to handle the case where a given track is regarded as the next
            track by more than one 'previous' track, i.e., a 'join' in two
            trackways """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        if len(selectedTracks) < 2:
            self._unlock()
            return

        i = 0
        iMax = len(selectedTracks) - 1
        while i < iMax:
            # unlink any preexisting 'previous' track to the about-to-be-next
            # track so that each track has at most one previous (and necessarily
            # but one next)
            prev = self._trackwayManager.getPreviousTrack(selectedTracks[i + 1])
            if prev:
                prev.next = u''

            # now set this i-th track's next
            selectedTracks[i].next = selectedTracks[i + 1].uid
            i += 1

        track = selectedTracks[-1]
        self._trackwayManager.selectTrack(track)
        self.refreshTrackUI(track.toDict())
        self._trackwayManager.setCameraFocus()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleLockedCkbx(self):
        """ The selected track has its LOCKED flag set (or cleared). """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        track.locked = self.lockedCkbx.isChecked()
        #
        # if track.locked:
        #     self.enableTrackUI(False)
        # else:
        #     self.enableTrackUI(True)

        self.refreshTrackUI(track.toDict())

        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleMarkedCkbx(self):
        """ This track has its MARKED source flag set or cleared, based on the
            value of the checkbox. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        track.marked = self.markedCkbx.isChecked()
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleNextBtn(self):
        """ Get the next track, select its corresponding node, and focus the
            camera on it. If there is no next node, just leave the current node
            selected. """

        if not self._lock():
            return

        track = self._trackwayManager.getLastSelectedTrack()

        if track is None:
            self._unlock()
            return

        next = self._trackwayManager.getNextTrack(track)
        if next is None:
            PyGlassBasicDialogManager.openOk(
                self,
                'No next track',
                '%s is the last in this series' % track.name)
            self._unlock()
            return

        self._trackwayManager.selectTrack(next)
        dict = next.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleNoteLE(self):
        """ The note line edit is handled here. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        track.note = self.noteLE.text()
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleOperation(self, op):
        """ A number of operations can be performed on (one or more) selected
            track(s). """

        if op == self.EXTRAPOLATE_NEXT:
            self.handleExtrapolateNext()
        if op == self.EXTRAPOLATE_PREVIOUS:
            self.handleExtrapolatePrevious()
        elif op == self.INTERPOLATE_TRACK:
            self.handleInterpolate()
        elif op == self.SET_TO_MEASURED:
            self.handleSetToMeasuredDimensions()
        elif op == self.SET_UNCERTAINTY_LOW:
            self.handleSetUncertaintyLow()
        elif op == self.SET_UNCERTAINTY_MODERATE:
            self.handleSetUncertaintyModerate()
        elif op == self.SET_UNCERTAINTY_HIGH:
            self.handleSetUncertaintyHigh()
        elif op == self.REDUCE_ROT_UNCERTAINTY:
            self.handleReduceRotationalUncertainty()
        elif op == self.LINK_SELECTED:
            self.handleLink()
        elif op == self.UNLINK_SELECTED:
            self.handleUnlink()
        elif op == self.SET_COMPLETED:
            self.handleSetCompleted()
        elif op == self.SET_ALL_INCOMPLETE:
            self.handleSetAllIncompleted()
        elif op == self.SET_COMPLETE:
            self.handleSetTrackCompleted()

#_______________________________________________________________________________
    def handleOperation1Btn(self):
        """ Passes the selected operation to be performed. """

        self.handleOperation(self.operation1Cmbx.currentText())

#_______________________________________________________________________________
    def handleOperation2Btn(self):
        """ Passes the selected operation to be performed. """

        self.handleOperation(self.operation2Cmbx.currentText())

#_______________________________________________________________________________
    def handleOperation3Btn(self):
        """ Passes the selected operation to be performed. """

        self.handleOperation(self.operation3Cmbx.currentText())

#_______________________________________________________________________________
    def handlePrevBtn(self):
        """ Get the previous track, select its corresponding node, and focus the
            camera on it. If here is no previous node, just leave the current
            node selected. """

        if not self._lock():
            return

        track = self._trackwayManager.getFirstSelectedTrack()
        if track is None:
            self._unlock()
            return

        prev = self._trackwayManager.getPreviousTrack(track)
        if prev is None:
            PyGlassBasicDialogManager.openOk(
                self,
                'No previous track',
                '%s is the first in this series' % track.name)
            self._unlock()
            return

        self._trackwayManager.selectTrack(prev)

        dict = prev.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handlePullBtn(self):
        """ The transform data in the selected track node(s) is used to populate
            the UI. Note that if multiple track nodes are selected, the last
            such track node is used to extract data for the trackway UI (but the
            fields of the track UI are cleared). """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self.clearTrackwayUI()
            self.clearTrackUI()
            self._unlock()
            return

        track = selectedTracks[-1]

        props = track.toDict()
        self.refreshTrackwayUI(props)

        if len(selectedTracks) == 1:
            self.refreshTrackUI(props)
        else:
            self.clearTrackUI()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleReduceRotationalUncertainty(self):
        """ The selected tracks are assigned a lower uncertainty value for
            rotation. """
        #
        # if not self._lock():
        #     return
        #
        # selectedTracks = self._trackwayManager.getSelectedTracks()
        # if selectedTracks is None:
        #     self._unlock()
        #     return
        #
        # track = selectedTracks[0]
        #
        # track.rotationUncertainty -= 2.0
        # track.updateNode()
        #
        # # update the Maya node and the UI
        # dict = track.toDict()
        # self.refreshTrackUI(dict)
        #
        # self._trackwayManager.closeSession(commit=True)
        # self._unlock()

        if not self._lock():
            return

        # make sure this was not an accident
        result = PyGlassBasicDialogManager.openYesNo(
                self,
                u'CONFIRMATION REQUIRED',
                u'Are you sure you want to set reduce uncertainty of all \
                uncompleted tracks?',
                False)
        if not result:
            self._unLock()
            return

        uids = self._trackwayManager.getUidList()

        if not uids:
            self._unLock()
            return

        for uid in uids:
            track = self._trackwayManager.getTrackByUid(uid)
            if not track.completed:
                track.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_LOW
                track.widthUncertainty    = self.DIMENSION_UNCERTAINTY_LOW
                track.rotationUncertainty = self.ROTATION_UNCERTAINTY_LOW


        # now select the track corresponding to the first UID in the list of
        # UIDs
        self._trackwayManager.selectTrack(
            self._trackwayManager.getTrackByUid(uids[0]))

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleRotationSbx(self):
        """ The rotation of the selected track (manus or pes) is adjusted. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
             self._unlock()
             return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        track.rotation = self.rotationSbx.value()
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleRotationUncertaintySbx(self):
        """ The track node has a pair of nodes that represent the angular
            uncertainty (plus or minus some value set up in the rotation
            uncertainty spin box (calibrated in degrees). """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        t = selectedTracks[0]
        # use this opportunity to capture the current state of the Maya node        
        t.updateFromNode()
        t.rotationUncertainty = self.rotationUncertaintySbx.value()
        t.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSelect1Btn(self):
        """ The various options for track selection are dispatched from here.
            The UI locking occurs within the specific handlers. """

        if self.selectBy1Cmbx.currentText() == self.FETCH_TRACK_BY_NAME:
            self.handleFetchByName()
        elif self.selectBy1Cmbx.currentText() == self.FETCH_TRACK_BY_INDEX:
            self.handleFetchByIndex()
        elif self.selectBy1Cmbx.currentText() == self.SELECT_TRACK_BY_INDEX:
            self.handleSelectByIndex()
        elif self.selectBy1Cmbx.currentText() == self.SELECT_TRACK_BY_NAME:
            self.handleSelectByName()
        elif self.selectBy1Cmbx.currentText() == self.SELECT_TRACK_BY_UID:
            self.handleSelectByUid()
        elif self.selectBy1Cmbx.currentText() == self.SELECT_SERIES:
            self.handleSelectSeries()
        elif self.selectBy1Cmbx.currentText() == self.SELECT_SERIES_AFTER:
            self.handleSelectSeriesAfter()
        elif self.selectBy1Cmbx.currentText() == self.SELECT_SERIES_BEFORE:
            self.handleSelectSeriesBefore()
        elif self.selectBy1Cmbx.currentText() == self.SELECT_ALL_COMPLETED:
            self.handleSelectCompleted(True)
        elif self.selectBy1Cmbx.currentText() == self.SELECT_ALL_INCOMPLETE:
            self.handleSelectCompleted(False)
        elif self.selectBy1Cmbx.currentText() == self.SELECT_NEXT_INCOMPLETE:
            self.handleSelectNextIncomplete()
        elif self.selectBy1Cmbx.currentText() == self.SELECT_ALL_MARKED:
            self.handleSelectMarked(True)

        self.refreshTrackCountsUI()
        self._trackwayManager.closeSession(commit=True)

#_______________________________________________________________________________
    def handleSelect2Btn(self):
        """ The various options for track selection are dispatched here. """

        if self.selectBy2Cmbx.currentText() == self.FETCH_TRACK_BY_NAME:
            self.handleFetchByName()
        elif self.selectBy2Cmbx.currentText() == self.FETCH_TRACK_BY_INDEX:
            self.handleFetchByIndex()
        elif self.selectBy2Cmbx.currentText() == self.SELECT_TRACK_BY_INDEX:
            self.handleSelectByIndex()
        elif self.selectBy2Cmbx.currentText() == self.SELECT_TRACK_BY_NAME:
            self.handleSelectByName()
        elif self.selectBy2Cmbx.currentText() == self.SELECT_TRACK_BY_UID:
            self.handleSelectByUid()
        elif self.selectBy2Cmbx.currentText() == self.SELECT_SERIES:
            self.handleSelectSeries()
        elif self.selectBy2Cmbx.currentText() == self.SELECT_SERIES_AFTER:
            self.handleSelectSeriesAfter()
        elif self.selectBy2Cmbx.currentText() == self.SELECT_SERIES_BEFORE:
            self.handleSelectSeriesBefore()
        elif self.selectBy2Cmbx.currentText() == self.SELECT_ALL_COMPLETED:
            self.handleSelectCompleted(True)
        elif self.selectBy2Cmbx.currentText() == self.SELECT_ALL_INCOMPLETE:
            self.handleSelectCompleted(False)
        elif self.selectBy2Cmbx.currentText() == self.SELECT_NEXT_INCOMPLETE:
            self.handleSelectNextIncomplete()
        elif self.selectBy2Cmbx.currentText() == self.SELECT_ALL_MARKED:
            self.handleSelectMarked(True)

        self.refreshTrackCountsUI()
        self._trackwayManager.closeSession(commit=True)

#_______________________________________________________________________________
    def handleSelectAllTrackwaysBtn(self):
        """ A list of all track nodes across all layers is compiled and
            selected. """

        if not self._lock():
            return

        self._trackwayManager.selectAllTracks()

        self._unlock()

#_______________________________________________________________________________
    def handleSelectByIndex(self):
        """ Handles the selection of a track by the index of its catalog
            entry. """

        if not self._lock():
            return

        tracks = self._trackwayManager.getTracksByProperties(
            index=self.indexLE.text())
        if not tracks:
            self._unlock()
            return

        if len(tracks) != 1:
            self._unlock()
            return

        t = tracks[0]
        self._trackwayManager.selectTrack(t)

        self._trackwayManager.setCameraFocus()
        dict = t.toDict()
        self.refreshTrackwayUI(dict)
        self.refreshTrackUI(dict)
        self._unlock()

#_______________________________________________________________________________
    def handleSelectByName(self):
        """ Handles the selection of a track by name. """

        if not self._lock():
            return

        tracks = self._trackwayManager.getTrackByName(
            self.trackNameLE.text(),
            **self.getTrackwayPropertiesFromUI())
        if not tracks:
            PyGlassBasicDialogManager.openOk(
                self,
                'None',
                'No track found with that name.')
            self._unlock()
            return

        if len(tracks) != 1:
            self._unlock()
            return

        track = tracks[0]
        self._trackwayManager.selectTrack(track)
        self._trackwayManager.setCameraFocus()
        self.refreshTrackUI(track.toDict())

        self._unlock()

#_______________________________________________________________________________
    def handleSelectByUid(self):
        """ Handles the selection of a track by its UID. """

        if not self._lock():
            return

        tracks = self._trackwayManager.getTracksByProperties(
            uid=self.uidLE.text())
        if not tracks or len(tracks) != 1:
            self._unlock()
            return

        t = tracks[0]

        self._trackwayManager.selectTrack(t)

        self._trackwayManager.setCameraFocus()
        dict = t.toDict()
        self.refreshTrackwayUI(dict)
        self.refreshTrackUI(dict)
        self._unlock()

#_______________________________________________________________________________
    def handleSelectCadenceCamBtn(self):
        """ Handles the selection of the CadenceCam. """

        if not self._lock():
            return

        self._trackwayManager.initializeCadenceCam()
        self._trackwayManager.selectCadenceCam()

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self.clearTrackwayUI()
            self.clearTrackUI()
            self._unlock()
            return

        if len(selectedTracks) == 1:
            dict = selectedTracks[0].toDict()
            self.refreshTrackwayUI(dict)
            self.refreshTrackUI(dict)
            self._trackwayManager.setCameraFocus()
        else:
            self.clearTrackUI()

        self._unlock()

#_______________________________________________________________________________
    def handleSelectCompleted(self, completed=True):
        """ Selects all completed track nodes (those with UIDs in the scene that
            have their COMPLETED source flag set).  Batch this task into
            sublists due to limitations. This is also used with False passed in
            to select those tracks that are not yet completed. """

        if not self._lock():
            return

        # turn off all current selections
        self._trackwayManager.selectTrack(None)

        # first get the list of tracks (either completed or incomplete)
        tracks = self._trackwayManager.getCompletedTracks(completed=completed)

        if not tracks:
            PyGlassBasicDialogManager.openOk(
                 self,
                'None',
                'No %s tracks selected' % 'completed'\
                if completed else 'incomplete')
            self._unlock()
            return

        self._trackwayManager.selectTracks(tracks)

        self.clearTrackUI()
        self.clearTrackwayUI()

        self._unlock()

#_______________________________________________________________________________
    def handleSelectMarked(self, marked=True):
        """ Selects all marked track nodes (those with UIDs in the scene that
            have their MARKED source flag set).  Batch this task into sublists
            due to limitations. """

        if not self._lock():
            return

        tracks = self._trackwayManager.getMarkedTracks()
        if not tracks:
            PyGlassBasicDialogManager.openOk(
                self,
                'None',
                'There are no marked tracks in this scene.')
            self._unlock()
            return

        self._trackwayManager.selectTracks(tracks)

        self.clearTrackUI()
        self.clearTrackwayUI()

        self._unlock()

#_______________________________________________________________________________
    def handleSelectNextIncomplete(self):
        """ The next incomplete track is selected, focussed upon, and ready to
            edit. """

        if not self._lock():
            return

        incompleteTracks = self._trackwayManager.getCompletedTracks(False)

        if not incompleteTracks:
            PyGlassBasicDialogManager.openOk(
                self,
               'None',
               'All tracks are complete')
            self._unlock()
            return

        track = incompleteTracks[0]
        track.updateNode()
        self._trackwayManager.selectTrack(track)

        # update the UIs accordingly
        self.refreshTrackwayUI(track.toDict())
        self.refreshTrackUI(track.toDict())
        self._trackwayManager.setCameraFocus()

        self._unlock()

#_______________________________________________________________________________
    def handleSelectPerspectiveBtn(self):
        """ This selects the persp camera. """

        if not self._lock():
            return

        self._trackwayManager.selectPerspectiveCam()

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self.clearTrackwayUI()
            self.clearTrackUI()
            self._unlock()
            return

        if len(selectedTracks) == 1:
            dict = selectedTracks[0].toDict()
            self.refreshTrackwayUI(dict)
            self.refreshTrackUI(dict)
            self._trackwayManager.setCameraFocus()
        else:
            self.clearTrackUI()

        self._unlock()

#_______________________________________________________________________________
    def handleSelectSeries(self):
        """ Select in Maya the nodes for the entire track series based on the
        given selection. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        tracks = self._trackwayManager.getTrackSeries(selectedTracks[0])
        if tracks is None:
            self._unlock()
            return

        # select the Maya track nodes
        self._trackwayManager.selectTracks(tracks)

        # The path of track series is visualized as a piecewise-linear curve
        # added to the PATH_LAYER
        # self._trackwayManager.addPath(tracks)

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSelectSeriesBefore(self):
        """ Selects all track nodes up to (but excluding) the first
            currently-selected track(s). """

        if not self._lock():
            return

        track = self._trackwayManager.getFirstSelectedTrack()
        if track:
            self._trackwayManager.selectSeriesBefore(track)

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSelectSeriesAfter(self):
        """ Selects all track nodes after the last of the currently-selected
            track(s). """

        if not self._lock():
            return

        tracks = self._trackwayManager.getSelectedTracks()
        if tracks:
            self._trackwayManager.selectSeriesAfter(tracks[0])

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSelectTrackwayBtn(self):
        """ Trackways are selected by Trackway type and number (such as S18).
            First put the trackway into a layer if it is not already, then
            select the members of that track. """

        if not self._lock():
            return

        # compose the name of the layer from the trackway name in the combo box
        layer = self.trackwayCmbx.currentText() +\
                self._trackwayManager.LAYER_SUFFIX

        self._trackwayManager.selectTracksInLayer(layer)

        self._unlock()

#_______________________________________________________________________________
    def handleSetCompleted(self):
        """ This sets all selected tracks to be complete. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        for track in selectedTracks:
                track.completed = True
                track.hidden    = True
        self._trackwayManager.selectTrack(track)
        self.refreshTrackUI(track.toDict())
        self._trackwayManager.setCameraFocus()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSetAllIncompleted(self):
        """ This sets all tracks to be incomplete, so that they can be examined
            individually using selectNextIncomplete. """

        if not self._lock():
            return

        # make sure this is intentional
        result = PyGlassBasicDialogManager.openYesNo(
                self,
                u'CONFIRMATION REQUIRED',
                u'Are you sure you want to set ALL tracks to INCOMPLETED?',
                False)
        if not result:
            self._unLock()
            return

        uids = self._trackwayManager.getUidList()

        if not uids:
            self._unLock()
            return

        for uid in uids:
            track = self._trackwayManager.getTrackByUid(uid)
            track.completed = False

        # now select the track corresponding to the first UID
        self._trackwayManager.selectTrack(
            self._trackwayManager.getTrackByUid(uids[0]))

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSetTrackCompleted(self):
        """ The currently selected track is set as completed and the next
            incomplete track is selected, focussed upon, and ready to edit. """

        if not self._lock():
            return

        # just return if no track is currently selected
        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        # otherwise update this track from the Maya node and set it completed
        track = selectedTracks[0]
        track.updateFromNode()
        track.completed = True
        track.updateNode()

        self.refreshTrackUI(track.toDict())
        self.refreshTrackCountsUI()

        # and then get the next incomplete track
        incompleteTracks = self._trackwayManager.getCompletedTracks(False)

        # return if we are finally finished
        if not incompleteTracks:
            PyGlassBasicDialogManager.openOk(
                self,
               'None',
               'All tracks are complete')
            self._unlock()
            return

        # not finished, so get the next incomplete track and select it
        track = incompleteTracks[0]
        track.updateNode()
        self._trackwayManager.selectTrack(track)

        # update the UIs accordingly
        self.refreshTrackwayUI(track.toDict())
        self.refreshTrackUI(track.toDict())
        self._trackwayManager.setCameraFocus()

        self._unlock()

#_______________________________________________________________________________
    def handleSetToMeasuredDimensions(self):
        """ The selected track is assigned the length and width as measured in
            the field. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
          self._unlock()
          return

        track = selectedTracks[0]

        # override the width and length to reset it to the measured values
        track.width  = track.widthMeasured
        track.length = track.lengthMeasured

        # provide default uncertainty values
        track.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
        track.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
        track.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE

        # update the Maya node and the UI
        track.updateNode()
        dict = track.toDict()
        self.selectTrack(track)
        self.refreshTrackUI(dict)
        self._trackwayManager.setCameraFocus()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSetUncertaintyHigh(self):
        """ The selected tracks are assigned high uncertainty values. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        track = selectedTracks[0]

        track.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_HIGH
        track.widthUncertainty    = self.DIMENSION_UNCERTAINTY_HIGH
        track.rotationUncertainty = self.ROTATION_UNCERTAINTY_HIGH
        track.updateNode()

        # update the Maya node and the UI
        dict = track.toDict()
        self._trackwayManager.selectTrack(track)
        self.refreshTrackUI(dict)
        self._trackwayManager.setCameraFocus()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSetUncertaintyLow(self):
        """ The selected track is assigned low uncertainty values. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        track = selectedTracks[0]

        track.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_LOW
        track.widthUncertainty    = self.DIMENSION_UNCERTAINTY_LOW
        track.rotationUncertainty = self.ROTATION_UNCERTAINTY_LOW

        track.updateNode()

        # update the Maya node and the UI
        dict = track.toDict()
        self._trackwayManager.selectTrack(track)
        self.refreshTrackUI(dict)
        self._trackwayManager.setCameraFocus()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSetUncertaintyModerate(self):
        """ The selected tracks are assigned moderate uncertainty values. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        track = selectedTracks[0]
        track.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
        track.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
        track.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE
        track.updateNode()

        # update the Maya node and the UI
        dict = track.toDict()
        self._trackwayManager.selectTrack(track)
        self.refreshTrackUI(dict)
        self._trackwayManager.setCameraFocus()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleShowAllTrackwaysBtn(self):
        """ This straightforwardly sets all layers visible. """

        if not self._lock():
            return

        self._trackwayManager.setAllLayersVisible(True)
        self._unlock()

#_______________________________________________________________________________
    def handleShowTrackwayBtn(self, visible=True):
        """ The visibility of each trackway is controlled by placing tracks in
            a corresponding layer (e.g., S18_layer). """

        if not self._lock():
            return

        trackwayName = self.trackwayCmbx.currentText()
        self._trackwayManager.showTrackway(trackwayName)

        self._unlock()

#_______________________________________________________________________________
    def handleSvgAddSelectedBtn(self):
        """ The current selection of tracks (if non-empty) is added to the
            current SVG file """

        if not self._lock():
            return

        tracks = self._trackwayManager.getSelectedTracks()

        if tracks is None:
            self._unlock()
            return

        # create a pointer indicating the rotation angle, to be translated,
        # scaled, and rotated
        self.currentDrawing.createGroup('pointer')
        self.currentDrawing.line(
            (0, 0), (0, -20), scene=False, groupId='pointer')

        for track in tracks:
            self.drawTrack(track, self.currentDrawing, 'pointer')

            # compute the averge uncertainty in cm (also stored in fractional
            # meters). The track dimensions stored in the database are in
            # fractional meters, so multiply by 100 to convert to cm.
            # u = 100*(track.widthUncertainty + track.lengthUncertainty)/2.0
            # self.currentDrawing.circle(
            #     (track.x, track.z),
            #     u,
            #     scene=True,
            #     fill='red',
            #     stroke='red')

        self._unlock()

#_______________________________________________________________________________
    def drawTrack(self, track, drawing, group, thickness =1.0, tolerance =0.1):
        """ The dimensions of a given track is drawn, and added to a given
            drawing, using the given CadenceDrawing group (a line oriented with
            the SVG positive Y direction. """

        # indicate the length (per track.length)
        drawing.use(group,
                    (track.x, track.z),
                    scale=2.0,
                    scaleY=track.lengthRatio*track.length,
                    rotation=track.rotation,
                    scene=True,
                    fill='none',
                    stroke='blue',
                    stroke_width=2.0,
                    stroke_opacity= 1.0,
                    fill_opacity=1.0)
        drawing.use(group,
                    (track.x, track.z),
                    scale=2.0,
                    scaleY=(1.0 - track.lengthRatio)*track.length,
                    rotation=track.rotation + 180.0,
                    scene=True,
                    fill='none',
                    stroke='blue',
                    stroke_width=2.0,
                    stroke_opacity=1.0,
                    fill_opacity=1.0)

        # and the same for the width (per track.width)
        drawing.use(group,
                    (track.x, track.z),
                    scale=2.0,
                    scaleY=track.width/2.0,
                    rotation=track.rotation + 90.0,
                    scene=True,
                    fill='none',
                    stroke='blue',
                    stroke_width=2.0,
                    stroke_opacity=1.0,
                    fill_opacity=1.0)
        drawing.use(group,
                    (track.x, track.z),
                    scale=2.0,
                    scaleY=track.width/2.0,
                    rotation=track.rotation - 90.0,
                    scene=True,
                    fill='none',
                    stroke='blue',
                    stroke_width=2.0,
                    stroke_opacity=1.0,
                    fill_opacity=1.0)

        # now render the measured dimensions, if provided, starting with
        # lengthMeasured
        if track.lengthMeasured != 0:
            if abs(track.length - track.lengthMeasured)/track.lengthMeasured\
                    > tolerance:
                strokeWidth = 8
                opacity     = 0.5
                color       = 'red'
            else:
                strokeWidth = 8
                opacity     = 0.25
                color       = 'green'
            drawing.use(group,
                        (track.x, track.z),
                        scale=thickness,
                        scaleY=track.lengthRatio*track.lengthMeasured,
                        rotation=track.rotation,
                        scene=True,
                        fill='none',
                        stroke=color,
                        stroke_width=strokeWidth,
                        stroke_opacity=opacity,
                        fill_opacity=opacity)
            drawing.use('pointer',
                        (track.x, track.z),
                        scale=thickness,
                        scaleY=(1.0 - track.lengthRatio)*track.lengthMeasured,
                        rotation=track.rotation + 180.0,
                        scene=True,
                        fill='none',
                        stroke=color,
                        stroke_width=strokeWidth,
                        stroke_opacity=opacity,
                        fill_opacity=opacity)

        # and likewise for widthMeasured
        if track.widthMeasured != 0:
            difference = track.width - track.widthMeasured
            if abs(difference)/track.widthMeasured > tolerance:
                strokeWidth = 8
                opacity     = 0.5
                color       = 'red'
            else:
                strokeWidth = 8
                opacity     = 0.25
                color       = 'green'
            drawing.use('pointer',
                        (track.x, track.z),
                        scale=2.0*thickness,
                        scaleY=track.widthMeasured/2.0,
                        rotation=track.rotation + 90.0,
                        scene=True,
                        fill='none',
                        stroke=color,
                        stroke_width=strokeWidth,
                        stroke_opacity=opacity,
                        fill_opacity=opacity)
            drawing.use('pointer',
                        (track.x, track.z),
                        scale=2.0*thickness,
                        scaleY=track.widthMeasured/2.0,
                        rotation=track.rotation - 90.0,
                        scene=True,
                        fill='none',
                        stroke=color,
                        stroke_width=strokeWidth,
                        stroke_opacity=opacity,
                        fill_opacity=opacity)

#_______________________________________________________________________________
    def handleSvgOpenBtn(self):
        """ A file name is specified relative to the local root. This file is
            then explicitly opened by a separate button press "Open", followed
            by compilation of the SVG drawing by incrementally adding objects
            (e.g., one can interactively compose a specific SVG drawing based
            on successive rounds of first selecting sceen content then pressing
            the "Add Selected" button, finally completing by pressing "Save".
            When the "Open" button is pressed, the fresh svg file is created if
            there is a valid row (completed columns) for the track site of
            specified index.  Otherwise it warns and returns. """

        if not self._lock():
            return

        # get the current index again and from this, get the site map
        index = self.trackSiteIndexSbx.value()

        # check if there is a valid site map for that particular tracksite index
        siteMap = self._trackwayManager.getSiteMap(index)
        if not siteMap:
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'Invalid Site Map',
                message=u'Tracksite index %s empty' % index,
                windowTitle=u'Tool Error')
            self._unlock()
            return

        # then make sure there is a file name specified
        fileName = self.svgFileNameLE.text()
        if not fileName:
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'Invalid SVG file name',
                message=u'Edit name and retry.',
                windowTitle=u'Tool Error')
            self._unlock()
            return

        # if there is already an open Cadence drawing, offer to close it before
        # continuing with new
        if self.currentDrawing:
            save = PyGlassBasicDialogManager.openYesNo(
                    self,
                    'SVG File already open.',
                    'Do you wish to save?')
            if save:
                self.currentDrawing.save()

        # now open a new drawing file
        self.currentDrawing = CadenceDrawing(fileName, siteMap)

        # place a grid in the drawing file
        self.currentDrawing.grid()

        self._unlock()

#_______________________________________________________________________________
    def handleSvgSaveBtn(self):
        """ The currently open Cadence drawing (SVG file) is written. If no
            Cadence drawing is already open, this complains and returns. """

        if not self._lock():
            return

        # complain if this button is pressed and no Cadence SVG drawing is
        # currently open
        if not self.currentDrawing:
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'Error',
                message=u'No SVG file open.',
                windowTitle=u'Tool Error')
            self._unlock()
            return

        print('saving svg file')

        # place the federal coordinates as a text string 20 cm above the marker
        site = self.currentDrawing.siteMap
        text = "(%s, %s)" % (site.federalEast, site.federalNorth)
        self.currentDrawing.text(text, (0, 20), scene=True)

        # place a 2 cm green unfilled circle atop the federal coordinate marker
        self.currentDrawing.circle(
            (0, 0),
            2,
            scene=True,
            fill='none',
            stroke='green',
            stroke_width=1)
        self.currentDrawing.grid()
        self.currentDrawing.save()
        self.currentDrawing = None

        self._unlock()

#_______________________________________________________________________________
    def handleSvgNameLE(self):
        """ Simply a file name is specified in the ui, which is later used in
            responding to the button press 'Open' in order to create an SVG
            file. """

        if not self._lock():
            return

        self._unlock()

#_______________________________________________________________________________
    def handleTrackSiteIndexSbx(self):
        """ Tracksites are indexed in a database table (see Tracks_SiteMap).
            That same index provides a convenient but slightly arcane means to
            select a given tracksite by selection of a spinbox integer value in
            the UI. """

        if not self._lock():
            return

        index   = self.trackSiteIndexSbx.value()
        siteMap = self._trackwayManager.getSiteMap(index)

        if siteMap is None:
            self.clearTrackSiteUI()
            self._unlock()
            return

        # now populate the tracksite information in the UI
        self.refreshTrackSiteUI(siteMap)

        self._unlock()

#_______________________________________________________________________________
    def handleUnlink(self):
        """ The 'next' attribute is cleared for the selected track. Unlinking
            does not attempt to relink tracks automatically (one must do it
            explicitly; see handleLink). """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if selectedTracks is None:
            self._unlock()
            return

        for t in selectedTracks:
            t.next = u''

        track = selectedTracks[-1]
        self._trackwayManager.selectTrack(track)
        dict = track.toDict()
        self.refreshTrackUI(dict)
        self._trackwayManager.setCameraFocus()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleUpdateLayersBtn(self):
        """ A set of Maya display layers is constructed, one for each trackway,
            and the names ofthese trackways (e.g. S18) are placed in a combo
            box, permitting selection of a specific trackways from the UI. """

        if not self._lock():
            return

        # the method that initializes the layers returns a list of the names of
        # all trackways
        trackwayNames = self._trackwayManager.initializeLayers()

        # add those trackway names to the combo box
        self.trackwayCmbx.addItems(trackwayNames)

        self._unlock()

#_______________________________________________________________________________
    def handleWidthSbx(self):
        """ The width of the selected track is adjusted. Width is stored in the
            database in fractional meters but send to Maya in cm and displayed
            in integer cm units."""

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]
        # use this opportunity to capture the current state of the Maya node
        track.updateFromNode()
        track.width = self.widthSbx.value()/100.0
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleWidthUncertaintySbx(self):
        """ The width uncertainty of the selected track is adjusted. """

        if not self._lock():
            return

        selectedTracks = self._trackwayManager.getSelectedTracks()
        if not selectedTracks:
            self._unlock()
            return

        if len(selectedTracks) != 1:
            self._unlock()
            return

        track = selectedTracks[0]

        track.widthUncertainty = self.widthUncertaintySbx.value()/100.0
        track.updateNode()

        self._trackwayManager.closeSession(commit=True)
        self._unlock()


#===============================================================================
#                                             S C E N A R I O   H A N D L E R S
#
#_______________________________________________________________________________
    def handleInitScenarioBtn(self):
        """ This makes a new trackway scenario file, initializing the proxies
            as necessary, and creating and displaying the tokens. """

        if not self._lock():
            return

        # if trackwayLE field in the UI is blank, apparently no trackway has
        # been selected, so abort
        if not self.trackwayLE.text():
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'Error',
                message=u'No trackway specified in UI.',
                windowTitle=u'Error')
            self._unlock()
            return

        # compose the trackway (e.g., CRO-500-2004-1-S-6) from the UI.
        trackway = (
            self.siteLE.text() + '-' +
            self.levelLE.text() + '-' +
            self.yearLE.text() + '-' +
            self.sectorLE.text() + '-' +
            self.trackwayLE.text()[0] + '-' +
            self.trackwayLE.text()[1:]).upper()

        text = 'loading scenario:  %s' % trackway
        self.consoleTE.append(text)
        print(text)

        if self._scenario:
            agree = PyGlassBasicDialogManager.openYesNo(
                self,
                format('Replace current scenario with %s?' % trackway))
            if not agree:
                self._unlock()
                return

        # delete any pre-existing tokens in the scene
        self._trackwayManager.deleteTokens()

        # now read the scenario file, which converts the CSV-format contents
        # into an instance of a scenario.
        path = format('%s/%s/%s' % (
            '~/Dropbox/A16/Simulation/data', trackway, 'source.csv'))

        try:
            self._scenario = Scenario(trackway, path)
        except Exception as err:
            print(err)
            self.consoleTE.append(str(err))
            self._unlock()
            return False

        text = "scenario %s successfully loaded" % trackway
        self.consoleTE.append(text)
        print(text)

        self._scenario.createPesProxies()
        text = "pes proxies successfully created"
        self.consoleTE.append(text)
        print(text)

        self._scenario.createManusProxies()
        text = "manus proxies successfully created"
        self.consoleTE.append(text)
        print(text)

        self._scenario.completeSequences()
        text = "sequences successfully completed"
        self.consoleTE.append(text)
        print(text)

        self._trackwayManager.createTokens(
            self._scenario.getEntries(tracks=True, proxies=True))

        text = "tokens successfully created"
        self.consoleTE.append(text)
        print(text)

        self._unlock()

#_______________________________________________________________________________
    def handleLoadScenarioBtn(self):
        """ This loads a trackway scenario file via the scenario manager. """

        if not self._lock():
            return

        # if the UI is blank, apparently no trackway has been selected
        if not self.trackwayLE.text():
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'Error',
                message=u'No trackway specified in UI.',
                windowTitle=u'Error')
            self._unlock()
            return

        # compose the requested trackway, e.g., CRO-500-2004-1-S-6, from the UI.
        trackway = (
            self.siteLE.text() + '-' +
            self.levelLE.text() + '-' +
            self.yearLE.text() + '-' +
            self.sectorLE.text() + '-' +
            self.trackwayLE.text()[0] + '-' +
            self.trackwayLE.text()[1:]).upper()

        self.consoleTE.append('loading scenario:  %s' % trackway)

        # delete any previously-generated tokens in the scene as necessary
        self._trackwayManager.deleteTokens()

        if self._scenario:
            current = self._scenario.trackway
            agree = PyGlassBasicDialogManager.openYesNo(
                self,
                format('Replace current scenario with %s?' % trackway))
            if not agree:
                self._unlock()
                return

        # now read the scenario file, which converts the CSV-format contents
        # into an instance of a scenario.
        path = format('%s/%s/%s' % (
            '~/Dropbox/A16/Simulation/scenarios',
            trackway,
            'scenario.csv'))

        try:
            self._scenario = Scenario(trackway, path)
        except Exception as err:
            print(err)
            self.consoleTE.append(str(err))
            self._unlock()
            return False

        text = "scenario %s successfully loaded" % trackway
        self.consoleTE.append(text)
        print(text)

        self._trackwayManager.createTokens(
            self._scenario.getEntries(tracks=True, proxies=True))

        text = "tokens successfully created"
        self.consoleTE.append(text)
        print(text)

        self._unlock()

#_______________________________________________________________________________
    def handleSaveScenarioBtn(self):
        """ This updates the scenario based on the current state of the Maya
            tokens then writes the scenario file. """

        if not self._lock():
            return

        # first pull all token props to make sure all is current then write it.
        self._trackwayManager.updateScenario(self._scenario)

        path = (
                '~/Dropbox/A16/Simulation/scenarios/' +
                self._scenario.trackway +
                '/scenario.csv' )
        self._scenario.write(path)

        text = format('tokens successfully written to %s' % path)
        self.consoleTE.append(text)
        print(text)

        self._unlock()

#_______________________________________________________________________________
    def handleCreateProxies(self):
        """ This adds proxy entries for missing pes entries.  Only the proxy
            entries are created, not their tokens. """

        if not self._lock():
            return

        self._scenario.createPesProxies()
        text = 'pes proxies successfully created'
        self.consoleTE.append(text)
        print(text)

        self._scenario.createManusProxies()
        text = 'Manus proxies successfully created'
        self.consoleTE.append(text)
        print(text)

        self._unlock()

#_______________________________________________________________________________
    def handleCreateTokens(self, tracks =True, proxies =True):
        """ This creates tokens for entries in the trackway scenario, for
            tracks, or proxies, or both. """

        if not self._lock():
            return

        for entry in self._scenario.getEntries(tracks, proxies):
            self._trackwayManager.createToken(entry)

        self._unlock()

#_______________________________________________________________________________
    def handleXSbx(self):
        """ This spinbox displays the (scenario) X coordinate of the given token
            (which corresponds to Z in Maya). """

        if not self._lock():
            return

        print('in handleXSbx')

        self._unlock()

#_______________________________________________________________________________
    def handleFirstTokenBtn(self):
        """ Get the last token, select the corresponding node, focus the camera
            on it, and update the UIs"""

        if not self._lock():
            return

        uid = self._trackwayManager.getSelectedTokenUid()

        if not uid:
            self._unlock()
            return

        if not self._scenario:
            self._unlock()
            return

        first    = self._scenario.getFirst(uid)
        firstUid = first.value['uid']
        self._trackwayManager.selectToken(firstUid)
        props = self._trackwayManager.getTokenProps(firstUid)
        self.refreshTokenUI(props)

        self._unlock()

#_______________________________________________________________________________
    def handleLastTokenBtn(self):
        """ Get the last token, select the corresponding node, focus the camera
            on it, and update the UIs"""

        if not self._lock():
            return

        uid = self._trackwayManager.getSelectedTokenUid()

        if not uid:
            self._unlock()
            return

        if not self._scenario:
            self._unlock()
            return

        last    = self._scenario.getLast(uid)
        lastUid = last.value['uid']
        self._trackwayManager.selectToken(lastUid)
        props = self._trackwayManager.getTokenProps(lastUid)
        self.refreshTokenUI(props)

        self._unlock()

#_______________________________________________________________________________#_______________________________________________________________________________
    def handleNextTokenBtn(self):
        """ Get the previous token and focus the camera on it. If there is no
            previous token, just leave the current node selected. """

        if not self._lock():
            return

        uid = self._trackwayManager.getSelectedTokenUid()

        if not uid:
            self._unlock()
            return

        if not self._scenario:
            self._unlock()
            return

        next = self._scenario.getNextNode(uid)
        if not next:
            self._unlock()
            return

        nextUid = next.value['uid']
        self._trackwayManager.selectToken(nextUid)
        props = self._trackwayManager.getTokenProps(nextUid)
        self.refreshTokenUI(props)

        self._unlock()

#_______________________________________________________________________________
    def handlePrevTokenBtn(self):
        """ Get the previous token and focus the camera on it. If there is no
            previous token, just leave the current node selected. """

        if not self._lock():
            return

        uid = self._trackwayManager.getSelectedTokenUid()

        if not uid:
            self._unlock()
            return

        if not self._scenario:
            self._unlock()
            return

        prev = self._scenario.getPrevNode(uid)
        if not prev:
            self._unlock()
            return

        prevUid = prev.value['uid']
        self._trackwayManager.selectToken(prevUid)
        props = self._trackwayManager.getTokenProps(prevUid)
        self.refreshTokenUI(props)

        self._unlock()

#_______________________________________________________________________________
    def handleYSbx(self):
        """ This spinbox displays the (scenario) Y coordinate of the given token
            (which corresponds to X in Maya). """

        if not self._lock():
            return

        print('in handleYSbx')

        self._unlock()

#_______________________________________________________________________________
    def handleDxSbx(self):
        """ This spinbox shows dx, the uncertainty in X, of the given token. """

        if not self._lock():
            return

        print('in handleDxSbx')

        self._unlock()

#_______________________________________________________________________________
    def handleDySbx(self):
        """ This spinbox shows dy, the uncertainty in Y, of the given token. """

        if not self._lock():
            return

        print('in handleDySbx')

        self._unlock()

#_______________________________________________________________________________
    def handlePullAllTokensBtn(self):
        """ This updates the scenario based on the props of all tokens in the
            scene. """

        if not self._lock():
            return

        self._trackwayManager.updateScenario(self._scenario)

        self._unlock()
#_______________________________________________________________________________
    def handlePullSelectedTokenBtn(self):
        """ The transform data in the selected token node is used to populate
            the token UI.  The corresponding scenario entry is also updated. """

        if not self._lock():
            return

        uid = self._trackwayManager.getSelectedTokenUid()

        if not uid:
            self._unlock()
            return

        # update the UI and the entry based on the token
        props = self._trackwayManager.getTokenProps(uid)
        self.refreshTokenUI(props)
        self._scenario.setProps(uid, props)

        self._unlock()

#_______________________________________________________________________________
    def handleChangeTokenUidBtn(self):
        """ Allows the token's UID to be changed from the UI. """

        uid = self._trackwayManager.getSelectedTokenUid()
        props = self._scenario.getProps(uid=uid)
        props['uid'] = self.uidLE.text()
        self._scenario.setProps(uid, props)
        self._trackwayManager.setTokenProps(uid, props)

#_______________________________________________________________________________
    def handleInsertTokenBtn(self):
        """ For the selected token, a new proxy is inserted either before or
            after that token. """

        if not self._lock():
            return

        uid = self._trackwayManager.getSelectedTokenUid()
        if not uid:
            self._unlock()
            return

        props = self._trackwayManager.getTokenProps(uid)

        # update the entry for the selected token
        self._scenario.setProps(uid, props)

        # determine where to place the new proxy
        before = self.beforeAfterCmbx.currentText() == self.BEFORE

        # the new proxy will have a number interpolated (float with 2 decimal
        # places) between the selected number and that of the previous token
        # or one less than the selected, if it is the first token in the
        # sequence.  So an interpolated new proxy between LM1 and LM2 would be
        # LM1.5, and have a fingerprint name CRO-500-2004-3-S-2-L-M-1.5_proxy.
        # Another interpolated between that new proxy and LM2 would be LM1.75,
        # and so forth.
        name     = props['name']
        parts    = self._scenario.decomposeName(name)
        number   = parts['number']
        left     = parts['left']
        pes      = parts['pes']
        trackway = parts['trackway']

        if before:
            prev = self._scenario.getPrevNode(uid)
            if prev:
                prevName   = prev.value['name']
                prevNumber = self._scenario.decomposeName(prevName)['number']
                # use integral numbering in gap if possible
                if number - prevNumber > 1.0:
                    newNumber = number - 1
                else:
                    newNumber = (prevNumber + number)/2.0
            else:
                newNumber = number - 1
        # if not before, the new proxy will be after the selected token
        else:
            next = self._scenario.getNextNode(uid)
            if next:
                # make the number an interpolate
                nextName   = next.value['name']
                nextNumber = self._scenario.decomposeName(nextName)['number']
                if nextNumber - number > 1.0:
                    newNumber = number + 1
                else:
                    newNumber  = (number + nextNumber)/2.0
            else:
                # it's at the end of the sequence
                newNumber = number + 1
        newName = self._scenario.composeName(
            newNumber,
            left=left,
            pes=pes,
            trackway=trackway)
        newUid = newName + '_proxy'

        # now decide on the position for the new proxy
        if before:
            prev = self._scenario.getPrevNode(uid)
            if prev:
                x = 0.5*(prev.value['x'] + props['x'])
                y = 0.5*(prev.value['y'] + props['y'])
            else:
                # put it only 10 cm away from the selected token
                x = props.value['x'] + 0.1
                y = props.value['y'] + 0.1
        # alternatively, the new proxy is supposd to be after the selected token
        else:
            next = self._scenario.getNextNode(uid)
            if next:
                x = 0.5*(props['x'] + next.value['x'])
                y = 0.5*(props['y'] + next.value['y'])
            else:
                x = props['x'] + 0.1
                y = props['y'] + 0.1

        # now compose the properties for the new proxy
        newProps = {'name':newName,
                    'uid':newUid,
                    'x':x,
                    'dx':self._scenario.PROXY_UNCERTAINTY_MODERATE,
                    'y':y,
                    'dy':self._scenario.PROXY_UNCERTAINTY_MODERATE,
                    'assumed':True }

        # and now insert the proxy into the sequence
        if before:
            self._scenario.insertEntryBefore(uid, newProps)
        else:
            self._scenario.insertEntryAfter(uid, newProps)

        # and make its token in the scene
        self._trackwayManager.createToken(newProps)
        self._unlock()

#_______________________________________________________________________________
    def handleSetProxyUncertaintyBtn(self):
        """ Sets the uncertainty level (for either a selection of proxy tokens,
            or for all proxies) to the specified amount. """

        if not self._lock():
            return

        value = None
        if self.proxyUncertaintyCmbx.currentText() == self.LOW:
            value = self._scenario.PROXY_UNCERTAINTY_LOW
        elif self.proxyUncertaintyCmbx.currentText() == self.MODERATE:
            value = self._scenario.PROXY_UNCERTAINTY_MODERATE
        elif self.proxyUncertaintyCmbx.currentText() == self.HIGH:
            value = self._scenario.PROXY_UNCERTAINTY_HIGH

        # use this opportunity to refresh the entries in the scenario based on
        # the values of the tokens prior to making any othe changes to the proxy
        # uncertainties in the scenario
 #       self._trackwayManager.updateScenario(self._scenario)

        if self.selectedVersusAllCmbx.currentText() == self.ALL:
            self._scenario.setUncertainties(value)
            self._trackwayManager.refreshAllTokens(self._scenario)
        else:
            uidList = self._trackwayManager.getSelectedTokenUids()
            self._scenario.setUncertainties(value, uidList)
            self._trackwayManager.refreshTokens(uidList, self._scenario)

        self._unlock()
        return

#_______________________________________________________________________________
    def handleDeleteTokenBtn(self):

        if not self._lock():
            return

        uid = self._trackwayManager.getSelectedTokenUid()
        if not uid:
            self._unlock()
            return

        prev = self._scenario.getPrevNode(uid)
        prevUid = prev.value['uid'] if prev else None

        if prevUid:
            self._trackwayManager.selectToken(prevUid)
        else:
            next = self._scenario.getNextNode(uid)
            nextUid = next.value['uid'] if next else None
            if nextUid:
                self._trackwayManager.selectToken(nextUid)

        self._scenario.deleteEntry(uid)
        self._trackwayManager.deleteToken(uid)

        self._unlock()
        return

#_______________________________________________________________________________
    def clearTokenUI(self):
        """ The token UI is cleared to all zeroes. """

        self.xSbx.setValue(0)
        self.dxSbx.setValue(0)
        self.ySbx.setValue(0)
        self.dySbx.setValue(0)

#_______________________________________________________________________________
    def refreshTokenUI(self, props):
        """ The token UI is updated from properties taken from the props.  The
            units are the same as used in the scenario manager's entries, based
            on meters, not the centimeters of the Maya scene."""

        self.xSbx.setValue(props['x'])
        self.dxSbx.setValue(props['dx'])
        self.ySbx.setValue(props['y'])
        self.dySbx.setValue(props['dy'])

        self.trackNameLE.setText('')
        self.uidLE.setText(self.shortName(props['uid']))
        self.indexLE.setText('')
        self.uidLE.setText(props['uid'])

#_______________________________________________________________________________
    def shortName(self, uid):
        """ A UID (e.g., CRO-500-2004-1-S-6-R-P-6, or the simpler form R-P-6
            with no trackway information provided), may also have the suffix
            '_proxy'.  This function returns the short name RP6. """

        uid = uid.split('_')[0]
        components = uid.split('-')
        if len(components) > 2:
            return (components[-3] + components[-2] + components[-1])
        return None


#===============================================================================
#                                                                 P R I V A T E
#
#_______________________________________________________________________________
    def _activateWidgetDisplayImpl(self, **kwargs):
        if not CadenceEnvironment.NIMBLE_IS_ACTIVE:
            self.setVisible(False)
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'No Nimble Connection',
                message=u'An active Nimble server connection is required',
                windowTitle=u'Tool Error')
            return

        # in case there was an earlier failure, set this visible
        self.setVisible(True)

        # now that Nimble is active, get Maya ready for Cadence, starting with
        # the CadenceCam
        self._trackwayManager.initializeCadenceCam()

        # update the track UI and trackway UI based on what might be selected
        # already
        self.handlePullBtn()

        # display summary counts of loaded, completed, and selected tracks
        self.refreshTrackCountsUI()

#_______________________________________________________________________________
    def _deactivateWidgetDisplayImpl(self, **kwargs):
        """ Commit any unfinished database changes when the widget is
            closed. """

        self._trackwayManager.closeSession(commit=True)

#_______________________________________________________________________________
    def _lock(self):
        """ Used to prevent chain reactions of UI widget handlers calling other
            handlers.  Each handler sets the lock by calling this, and if
            successful, the code continues in that handler else makes an early
            return."""

        if self._uiLock:
            return False

        self._uiLock = True
        return True

#_______________________________________________________________________________
    def _unlock(self):
        """ Each UI widget handler must unlock on exit. """

        self._uiLock = False

#_______________________________________________________________________________
    def _closeSession(self):
        """ Used to close the database session from the TrackwayManagerWidget,
            when necessary. """

        self._trackwayManager.closeSession()
