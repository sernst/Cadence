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

from cadence.analysis.shared.CsvWriter import CsvWriter

import csv
import os

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
    SET_DATUM            = 'Set Datum'
    SET_LINKS            = 'Set Links'
    SET_COMPLETED        = 'Set Selected Tracks Complete'
    SET_ALL_INCOMPLETE   = 'Set All Tracks Incomplete'
    SET_COMPLETE         = 'Set Complete & Get Next'

    SET_UNCERTAINTY_LOW      = 'Set Uncertainties LOW'
    SET_UNCERTAINTY_MODERATE = 'Set Uncertainties MODERATE'
    SET_UNCERTAINTY_HIGH     = 'Set Uncertainties HIGH'
    REDUCE_ROT_UNCERTAINTY   = 'Reduce Rotational Uncertainty'

    INITIALIZE_PROXIES = 'Initialize Proxy Tracks'

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

        self.firstBtn.clicked.connect(self.handleFirstTrackBtn)
        self.prevBtn.clicked.connect(self.handlePrevBtn)
        self.nextBtn.clicked.connect(self.handleNextBtn)
        self.lastBtn.clicked.connect(self.handleLastTrackBtn)

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
            self.SET_DATUM,
            self.SET_LINKS,
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
        # access for common tasks
        self.operation1Cmbx.addItems(trackOperationMethods)
        self.operation1Cmbx.setCurrentIndex(0)
        self.operation1Btn.clicked.connect(self.handleOperation1Btn)

        self.operation2Cmbx.addItems(trackOperationMethods)
        self.operation2Cmbx.setCurrentIndex(0)
        self.operation2Btn.clicked.connect(self.handleOperation2Btn)

        self.operation3Cmbx.addItems(trackOperationMethods)
        self.operation3Cmbx.setCurrentIndex(0)
        self.operation3Btn.clicked.connect(self.handleOperation3Btn)

        # in the Trackway tab:
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

        # in the Tracksite tab:
        self.trackSiteIndexSbx.valueChanged.connect(
            self.handleTrackSiteIndexSbx)
        self.svgFileNameLE.textChanged.connect(self.handleSvgNameLE)
        self.openSvgFileBtn.clicked.connect(self.handleSvgOpenBtn)
        self.saveSvgFileBtn.clicked.connect(self.handleSvgSaveBtn)
        self.addSelectedBtn.clicked.connect(self.handleSvgAddSelectedBtn)

        self.currentDrawing = None

        # populate the track site data based on the initial value of the index
        self.handleTrackSiteIndexSbx()

        # set up the UI and support data structures for the proxy tracks

        # in the Proxy Track tab:
        self.firstProxyBtn.setIcon(QtGui.QIcon(
            self.getResourcePath('mediaIcons', 'first.png')))
        self.prevProxyBtn.setIcon( QtGui.QIcon(
            self.getResourcePath('mediaIcons', 'prev.png')))
        self.nextProxyBtn.setIcon( QtGui.QIcon(
            self.getResourcePath('mediaIcons', 'next.png')))
        self.lastProxyBtn.setIcon( QtGui.QIcon(
            self.getResourcePath('mediaIcons', 'last.png')))

        self.longitudeSbx.valueChanged.connect(self.handleLongitudeSbx)
        self.longitudeSbx.setAccelerated(True)

        self.latitudeSbx.valueChanged.connect(self.handleLatitudeSbx)
        self.latitudeSbx.setAccelerated(True)

        self.longitudeUncertaintySbx.valueChanged.connect(
            self.handleLongitudeUncertaintySbx)
        self.latitudeUncertaintySbx.valueChanged.connect(
            self.handleLatitudeUncertaintySbx)

        self.proxyPullBtn.clicked.connect(self.handleProxyPullBtn)

        self.firstProxyBtn.clicked.connect(self.handleFirstProxyBtn)
        self.prevProxyBtn.clicked.connect(self.handlePrevProxyBtn)
        self.nextProxyBtn.clicked.connect(self.handleNextProxyBtn)
        self.lastProxyBtn.clicked.connect(self.handleLastProxyBtn)

        self.selectCadenceCamBtn_2.clicked.connect(
            self.handleSelectCadenceCamBtn)
        self.selectPerspectiveBtn_2.clicked.connect(
            self.handleSelectPerspectiveBtn)
        self.pullBtn_2.clicked.connect(self.handlePullBtn)

        self.initializeProxiesBtn.clicked.connect(
            self.handleInitializeProxiesBtn)
        self.saveProxiesBtn.clicked.connect(self.handleSaveProxiesBtn)

        self.currentTrackwayDictionary = None

#===============================================================================
#                                                                    P U B L I C
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

#
#===============================================================================
#                                              T R A C K  U I  U T I L I T I E S

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
        """ The track properties aspect of the UI display is updated based on
            props, a dictionary compiling the properies for a given track model
            instance. """

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

        # compose the trackway name (such as S18 for type 'S' for sauropod and
        # the trackway number
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
#                                                                H A N D L E R S
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

        # if track length or width (or both) were not measured originally, posit
        # high uncertainties
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

        # if track length or width (or both) were not measured originally, posit
        # high uncertainties
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
    def handleFirstTrackBtn(self):
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
    def handleLastTrackBtn(self):
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
    def handleLink(self):
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
    def handleLongitudeSbx(self):
        """ This spinbox shows the longitude of the given track proxy.  Note
            that longitude refers to Z in Maya and X in the simulator. """

        print('in handleLongitudeSbx')

#_______________________________________________________________________________
    def handleLongitudeUncertaintySbx(self):
        """ This spinbox shows the longitude of the given track proxy.  Note
            that longitude refers to Z in Maya and X in the simulator. """

        print('in handleLongitudeUncertaintySbx')

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

        elif op == self.SET_DATUM:
            self.handleSetDatum()

        elif op == self.SET_LINKS:
            self.handleSetNodeLinks()

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

        # make sure this is not an accident
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
    def handleLongitudinalUncertaintySbx(self):
        """ This spinbox shows the CSV dx track proxy.  Note that longitude
            refers to Z in Maya and X in the simulator. """

        print('in handleLongitudeUncertaintySbx')
#_______________________________________________________________________________
    def handleSelect1Btn(self):
        """ The various options for track selection are dispatched from here.
            The UI locking occurs within the specific handlers. """

        if self.selectBy1Cmbx.currentText() == self.FETCH_TRACK_BY_NAME:
            self.handleFetchByName()
        elif self.selectBy1Cmbx.currentText() ==\
                self.FETCH_TRACK_BY_INDEX:
            self.handleFetchByIndex()

        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_TRACK_BY_INDEX:
            self.handleSelectByIndex()
        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_TRACK_BY_NAME:
            self.handleSelectByName()
        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_TRACK_BY_UID:
            self.handleSelectByUid()

        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_SERIES:
            self.handleSelectSeries()
        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_SERIES_AFTER:
            self.handleSelectSeriesAfter()
        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_SERIES_BEFORE:
            self.handleSelectSeriesBefore()

        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_ALL_COMPLETED:
            self.handleSelectCompleted(True)
        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_ALL_INCOMPLETE:
            self.handleSelectCompleted(False)
        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_NEXT_INCOMPLETE:
            self.handleSelectNextIncomplete()
        elif self.selectBy1Cmbx.currentText() ==\
                self.SELECT_ALL_MARKED:
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

        # first get a list of tracks that are either completed or incomplete
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

        # make sure this is not an accident
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

        # now select the track corresponding to the first UID in the list of
        # UIDs
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

        # otherwise update this track from the Maya node and set this track as
        # completed
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
    def handleSetDatum(self):
        """ Set the datum attribute in all nodes for the entire track series
            based on the given selection.  The datum value is the disparity
            etween track width and measured track width. """

        if not self._lock():
            return

        tracks = self._trackwayManager.getSelectedTracks()
        if not tracks:
            self._unlock()
            return

        # set the datum attribute in the track nodes for these tracks
        self._trackwayManager.setNodeDatum(tracks)

        self._trackwayManager.closeSession(commit=True)
        self._unlock()

#_______________________________________________________________________________
    def handleSetNodeLinks(self):
        """ Sets the prev and next links in the selected track nodes. """

        if not self._lock():
            return

        tracks = self._trackwayManager.getSelectedTracks()
        if not tracks:
            self._unlock()
            return

        # set the prev and next attributes in the track nodes for these tracks
        self._trackwayManager.setNodeLinks(tracks)

        self._trackwayManager.closeSession(commit=True)
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
        """ With the tracks comprising each trackway (e.g., S18) placed in their
            own layer, with a corresponding layer name (e.g., S18_layer) the
            visibility of each trackway is controlled by the corresponding layer
            visiblity. """

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
            if abs(track.width - track.widthMeasured)/track.widthMeasured\
                    > tolerance:
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
        """ The currently open Cadence drawing (SVG file) is written here after
            pressing "Save". If no Cadence drawing is already open, this
            complains and returns. """

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
#                                          P R O X Y  T R A C K  H A N D L E R S

#_______________________________________________________________________________
    def refreshProxyUI(self, props):
        """ The properties for the proxy UI display is updated based on props, a
            dictionary compiling the properies for a given track model
            instance. """

        width               = props[TrackPropEnum.WIDTH.name]
        widthMeasured       = props[TrackPropEnum.WIDTH_MEASURED.name]
        length              = props[TrackPropEnum.LENGTH.name]

#_______________________________________________________________________________
    def handleFirstProxyBtn(self):
        """ Get the first proxy for this trackway. """

        if not self._lock():
            return

        print('in handleFirstProxyBtn')
        self._unlock()

#_______________________________________________________________________________
    def handleNextProxyBtn(self):
        """ Get the next proxy for this trackway. """

        if not self._lock():
            return

        print('in handleNextProxyBtn')

        self._unlock()

#_______________________________________________________________________________
    def handleLastProxyBtn(self):
        """ Get the last proxy for this trackway. """

        if not self._lock():
            return

        print('in handleLastProxyBtn')

        self._unlock()

#_______________________________________________________________________________
    def handlePrevProxyBtn(self):
        """ Get the previous proxy for this trackway. """

        if not self._lock():
            return

        print('in handlePrevProxyBtn')

        self._unlock()
#_______________________________________________________________________________
    def handleProxyPullBtn(self):
        """ Pull data from the proxy nodes and update the UI. """

        if not self._lock():
            return

        print('in handleProxyPullBtn')

        self._unlock()

#_______________________________________________________________________________
    def handleInitializeProxiesBtn(self):
        """ This creates all the track proxies for tracks missing from the given
            trackway. """

        if not self._lock():
            return

        trackway = self.trackwayLE.text()
        if not trackway:
            self._unlock()
            return

        # set up a trackway fingerprint (same as track fingerprint up to the
        # track number, e.g., CRO-500-2004-1-S-6)

        self.trackwayFingerprint = self.siteLE.text()        + '-' + \
                                   self.levelLE.text()       + '-' + \
                                   self.yearLE.text()        + '-' + \
                                   self.sectorLE.text()      + '-' + \
                                   self.trackwayLE.text()[0] + '-' + \
                                   self.trackwayLE.text()[1:]

        path = '~/Dropbox/A16/Simulation/data/' + self.trackwayFingerprint +\
                 '/source.csv'
        file = open(os.path.expanduser(path))
        reader = csv.reader(file)

        # open the source file and skip over the header row
        reader.next()
        # these will accumulate the numbers of the first and last tracks
        nMin = 10000
        nMax = -10000

        # entries is a dictionary with key limb_id ('lp', 'rp', 'lm' or 'rm')
        # and a corresponding list of entries

        self.entries = dict(lp=[], rp=[], lm=[], rm=[])

        for row in reader:
            # each row is list of 24 strings, with the first six strings
            # corresponding to the left pes, the next six to the right pes, and
            # so forth.  Note that a missing track is represented by six empty
            # strings.
            lp = row[1:7]
            rp = row[7:13]
            lm = row[13:19]
            rm = row[19:25]

            # add each non-empty entry (lp, rp, lm, or rm) to entries, and
            # update nMin and nMax
            if lp[0]:
                (name, uid, x, dx, y, dy) = lp
                entry = self.createEntry(
                    'lp', name=name, uid=uid, x=x, y=y, dx=dx, dy=dy)
                self.entries['lp'].append(entry)
                n = self.getTrackNumber(name)
                nMin = min(nMin, n)
                nMax = max(nMax, n)
            if rp[0]:
                (name, uid, x, dx, y, dy) = rp
                entry = self.createEntry(
                    'rp', name=name, uid=uid, x=x, y=y, dx=dx, dy=dy)
                self.entries['rp'].append(entry)
                n = self.getTrackNumber(name)
                nMin = min(nMin, n)
                nMax = max(nMax, n)
            if lm[0]:
                (name, uid, x, dx, y, dy) = lm
                entry = self.createEntry(
                    'lm', name=name, uid=uid, x=x, y=y, dx=dx, dy=dy)
                self.entries['lm'].append(entry)
                n = self.getTrackNumber(name)
                nMin = min(nMin, n)
                nMax = max(nMax, n)
            if rm[0]:
                (name, uid, x, dx, y, dy) = rm
                entry = self.createEntry(
                    'rm', name=name, uid=uid, x=x, y=y, dx=dx, dy=dy)
                self.entries['rm'].append(entry)
                n = self.getTrackNumber(name)
                nMin = min(nMin, n)
                nMax = max(nMax, n)

        # now add the proxy entries as needed to fill out each list from nMin to
        # nMax

        for n in range(nMin, nMax + 1):
            entry = self.getEntry('lp', n)
            if not entry:
                 name = format("%s-L-P-%s" % (self.trackwayFingerprint, n))
                 self.entries['lp'].append(self.createEntry('lp', name=name))

        # next, the right pes tracks
        for n in range(nMin, nMax + 1):
            entry = self.getEntry('rp', n)
            if not entry:
                 name = format("%s-R-P-%s" % (self.trackwayFingerprint, n))
                 self.entries['rp'].append(self.createEntry('rp', name=name))

        # then the left manus tracks:
        for n in range(nMin, nMax + 1):
            entry = self.getEntry('lm', n)
            if not entry:
                 name = format("%s-L-M-%s" % (self.trackwayFingerprint, n))
                 self.entries['lm'].append(self.createEntry('lm', name=name))

        # finally, the right manus tracks
        for n in range(nMin, nMax + 1):
            entry = self.getEntry('rm', n)
            if not entry:
                 name = format("%s-R-M-%s" % (self.trackwayFingerprint, n))
                 self.entries['rm'].append(self.createEntry('rm', name=name))

        # path2  = '~/Dropbox/A16/Simulation/data/' + fileName + '/modified.csv'
        # file2  = open(os.path.expanduser(path2),'w')
        # writer = csv.writer(file2)
        #
        # for row in rows:
        #     writer.writerow(row)
        #
        # file2.close()
        #
        # reader2 = csv.reader(file2)
        # print('now reading back again')
        # for row in reader2:
        #     print(row)

        for limb_id in ['lp', 'rp', 'lm', 'rm']:
            for entry in self.entries[limb_id]:
                print(entry)
            print()

        # now create the proxy nodes in Maya
        for entry in self.entries['lp']:
            if entry['lp_uid'] !=  'proxy':
                uid = entry['lp_name'] + '_test'
                x   = int(100*float(entry['lp_y']))
                z   = int(100*float(entry['lp_x']))
                props = dict(uid=uid, x=x, z=z)
                self._trackwayManager.createProxyNode(props)

        # for entry in self.entries['rp']:
        #     if entry['rp_uid'] ==  'proxy':
        #         uid = entry['rp_name'] + '_proxy'
        #         x   = int(100*float(entry['rp_y']))
        #         z   = int(100*float(entry['rp_x']))
        #         props = dict(uid=uid, x=x, z=z)
        #         self._trackwayManager.createProxyNode(props)
        #
        # for entry in self.entries['lm']:
        #     if entry['lm_uid'] ==  'proxy':
        #         uid = entry['lm_name'] + '_proxy'
        #         x   = int(100*float(entry['lm_y']))
        #         z   = int(100*float(entry['lm_x']))
        #         props = dict(uid=uid, x=x, z=z)
        #         self._trackwayManager.createProxyNode(props)


        for entry in self.entries['rm']:
            if entry['rm_uid'] != 'proxy':

                # uid = entry['rm_name'] + '_proxy'


                x   = int(100*float(entry['rm_y']))
                z   = int(100*float(entry['rm_x']))
                props = dict(uid=uid, x=x, z=z)
                print('props = %s' % props)
                # self._trackwayManager.createProxyNode(props)


        self._unlock()

#_______________________________________________________________________________
    def handleLatitudeSbx(self):
        """ This spinbox shows the latitude of the given track proxy.  Note that
            latitude refers to X in Maya and Y in the simulator. """

        print('in handleLatitudeSbx')

#_______________________________________________________________________________
    def handleLatitudeUncertaintySbx(self):
        """ This spinbox shows the latitude of the given track proxy.  Note that
            latitude refers to X in Maya and Y in the simulator. """

        print('in handleLatitudeUncertaintySbx')

#_______________________________________________________________________________
    def handleSaveProxiesBtn(self):
        """ This writes the cvs file into the same folder, but as
            'modified.csv' """
        pass

#_______________________________________________________________________________
    def writeSimfile(self, entries):
        """ Saves the CSV-format simulation file for a given trackway, after
            editing the proxies in that trackway.  It creates an instance of a
            CsvWriter, matching the format used in reading csv simulation files.
            Based on SimulationExporterStage. """

        csv = CsvWriter(
            autoIndexFieldName='Index',
            fields=[
                'lp_name', 'lp_uid', 'lp_x', 'lp_dx', 'lp_y', 'lp_dy',
                'rp_name', 'rp_uid', 'rp_x', 'rp_dx', 'rp_y', 'rp_dy',
                'lm_name', 'lm_uid', 'lm_x', 'lm_dx', 'lm_y', 'lm_dy',
                'rm_name', 'rm_uid', 'rm_x', 'rm_dx', 'rm_y', 'rm_dy'
            ]
        )

        length = max(
            len(self.entries['lp']),
            len(self.entries['rp']),
            len(self.entries['lm']),
            len(self.entries['rm']),
        )

        for index in range(length):
            items = []
            for limb_id, entries in self.entries.items():
                if index < len(entries):
                    items += entries[index].items()
                else:
                    items += self._create_entry(limb_id).items()
            csv.addRow(dict(items))

        path = '~/Dropbox/A16/Simulation/data/' + self.trackwayFingerprint +\
               '/modified.csv'
        if csv.save(path):
            print('writeSimFile:  Successfully wrote:', path)
        else:
            print('writeSimFile:  Unable to save CSV at "{}"'.format(path))

#_______________________________________________________________________________
    def getTrackNumber(self, name):
        """ returns the track number from a given track name (i.e.,
            fingerprint), else None. """

        return int(name.split("-")[-1]) if name else None

#_______________________________________________________________________________
    def createFingerprint(self, limb_id, trackNumber):
        """ Given a limb_id (e.g., 'lp'), and a track number (e.g., 2), returns
            a string based on the trackway fingerprint (e.g.,
            'CRO-500-2004-1-S-6'), returns a complete fingerprint, e.g.,
            CRO-500-2004-1-S-6-L-P-2. """

        return self.trackwayFingerprint + '-' + limb_id[0] + '-' +\
               limb_id[1] + '-' + trackNumber

#_______________________________________________________________________________
    def createEntry(
            self, limb_id, name, uid ='proxy', x ='', dx ='', y ='', dy =''):
        """  A dictionary is created for a given limb_id (either lp, rp, lm, or
            rm). If creating the dictionary for a proxy, note that it is given a
            complete fingerprint for the name, but the uid is simply
            'proxy'. """
        return dict([
            (limb_id + '_name', name),
            (limb_id + '_uid',  uid),
            (limb_id + '_x',    x),
            (limb_id + '_dx',   dx),
            (limb_id + '_y',    y),
            (limb_id + '_dy',   dy)])

#_______________________________________________________________________________
    def getEntry(self, limb_id, trackNumber):
        """ For the entries for a given limb_id (e.g., self.leftPesTracks),
            this returns the either the entry (dictionary) corresponding to the
            specified track number, or None. """

        for entry in self.entries[limb_id]:
            n = self.getTrackNumber(entry[limb_id + '_name'])
            if n == trackNumber:
                return entry
        return None

#===============================================================================
#                                                                  P R I V A T E

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
