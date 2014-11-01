# TrackwayManagerWidget.py
# (C)2012-2014
# Scott Ernst and Kent A. Stevens

import math
import nimble

from nimble import cmds
from PySide import QtGui

from pyglass.widgets.PyGlassWidget import PyGlassWidget
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.enum.SourceFlagsEnum import SourceFlagsEnum
from cadence.models.tracks.Tracks_Track import Tracks_Track

from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.svg.CadenceDrawing import CadenceDrawing

from cadence.util.maya.MayaUtils import MayaUtils

from cadence.mayan.trackway import GetSelectedUidList
from cadence.mayan.trackway import GetUidList
from cadence.mayan.trackway import GetTrackNodeData

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

    FETCH_TRACK_BY_NAME    = 'Fetch Track by NAME'
    FETCH_TRACK_BY_INDEX   = 'Fetch Track by INDEX'
    SELECT_NEXT_INCOMPLETE = 'Select Next INCOMPLETE'
    SELECT_TRACK_BY_NAME   = 'Select Track by NAME'
    SELECT_TRACK_BY_INDEX  = 'Select Track by INDEX'
    SELECT_SERIES_BEFORE   = 'Select Series BEFORE'
    SELECT_SERIES_AFTER    = 'Select Series AFTER'
    SELECT_TRACK_SERIES    = 'Select Track SERIES'
    SELECT_ALL_COMPLETED   = 'Select All COMPLETED'
    SELECT_ALL_INCOMPLETE  = 'Select All INCOMPLETE'
    SELECT_ALL_MARKED      = 'Select All MARKED'

    EXTRAPOLATE_NEXT     = 'Extrapolate NEXT Track'
    EXTRAPOLATE_PREVIOUS = 'Extrapolate PREVIOUS Track'
    INTERPOLATE_TRACK    = 'Interpolate SELECTED Track'
    LINK_SELECTED        = 'LINK Selected Tracks'
    UNLINK_SELECTED      = 'UNLINK Selected Tracks'
    SET_TO_MEASURED      = 'Set to MEASURED Dimensions'

    SET_UNCERTAINTY_LOW      = 'Set Uncertainties LOW'
    SET_UNCERTAINTY_MODERATE = 'Set Uncertainties MODERATE'
    SET_UNCERTAINTY_HIGH     = 'Set Uncertainties HIGH'

    DIMENSION_UNCERTAINTY_LOW      = 0.01
    DIMENSION_UNCERTAINTY_MODERATE = 0.03
    DIMENSION_UNCERTAINTY_HIGH     = 0.08

    ROTATION_UNCERTAINTY_LOW      = 3.0
    ROTATION_UNCERTAINTY_MODERATE = 10.0
    ROTATION_UNCERTAINTY_HIGH     = 30.0

    LAYER_SUFFIX = '_Trackway_Layer'
    PATH_LAYER   = 'Track_Path_Layer'

    FIT_FACTOR  = 0.2
    CADENCE_CAM = 'CadenceCam'

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)

        self._session = None

        self.firstBtn.setIcon(QtGui.QIcon(self.getResourcePath('mediaIcons', 'first.png')))
        self.prevBtn.setIcon( QtGui.QIcon(self.getResourcePath('mediaIcons', 'prev.png')))
        self.nextBtn.setIcon( QtGui.QIcon(self.getResourcePath('mediaIcons', 'next.png')))
        self.lastBtn.setIcon( QtGui.QIcon(self.getResourcePath('mediaIcons', 'last.png')))

        # in the Track tab:
        self.widthSbx.valueChanged.connect(self.handleWidthSbx)
        self.widthSbx.setAccelerated(True)

        self.lengthSbx.valueChanged.connect(self.handleLengthSbx)
        self.lengthSbx.setAccelerated(True)

        self.widthUncertaintySbx.valueChanged.connect(self.handleWidthUncertaintySbx)
        self.lengthUncertaintySbx.valueChanged.connect(self.handleLengthUncertaintySbx)

        self.rotationSbx.valueChanged.connect(self.handleRotationSbx)
        self.rotationSbx.setAccelerated(True)
        self.rotationUncertaintySbx.valueChanged.connect(self.handleRotationUncertaintySbx)

        self.completedCkbx.clicked.connect(self.handleCompletedCkbx)
        self.hiddenCkbx.clicked.connect(self.handleHiddenCkbx)
        self.lockedCkbx.clicked.connect(self.handleLockedCkbx)
        self.lockedCkbx.stateChanged.connect(self.handleLockedCkbx)
        self.markedCkbx.clicked.connect(self.handleMarkedCkbx)

        self.lengthRatioSbx.valueChanged.connect(self.handleLengthRatioSbx)
        self.noteLE.textChanged.connect(self.handleNoteLE)

        self.countsBtn.clicked.connect(self.handleCountsBtn)

        self.pullBtn.clicked.connect(self.handlePullBtn)

        self.firstBtn.clicked.connect(self.handleFirstBtn)
        self.prevBtn.clicked.connect(self.handlePrevBtn)
        self.nextBtn.clicked.connect(self.handleNextBtn)
        self.lastBtn.clicked.connect(self.handleLastBtn)

        self.selectCadenceCamBtn.clicked.connect(self.handleSelectCadenceCamBtn)
        self.selectPerspectiveBtn.clicked.connect(self.handleSelectPerspectiveBtn)

        trackSelectionMethods = (
            self.FETCH_TRACK_BY_NAME,
            self.FETCH_TRACK_BY_INDEX,
            self.SELECT_NEXT_INCOMPLETE,
            self.SELECT_TRACK_BY_NAME,
            self.SELECT_TRACK_BY_INDEX,
            self.SELECT_SERIES_BEFORE,
            self.SELECT_SERIES_AFTER,
            self.SELECT_TRACK_SERIES,
            self.SELECT_ALL_COMPLETED,
            self.SELECT_ALL_INCOMPLETE,
            self.SELECT_ALL_MARKED)

        self.selectionMethod1Cmbx.addItems(trackSelectionMethods)
        self.selectionMethod1Cmbx.setCurrentIndex(0)
        self.select1Btn.clicked.connect(self.handleSelect1Btn)

        self.selectionMethod2Cmbx.addItems(trackSelectionMethods)
        self.selectionMethod2Cmbx.setCurrentIndex(7)
        self.select2Btn.clicked.connect(self.handleSelect2Btn)

        trackOperationMethods = (
            self.EXTRAPOLATE_NEXT,
            self.EXTRAPOLATE_PREVIOUS,
            self.INTERPOLATE_TRACK,
            self.SET_TO_MEASURED,
            self.SET_UNCERTAINTY_LOW,      # for exceptional tracks
            self.SET_UNCERTAINTY_MODERATE, # a reasonable default
            self.SET_UNCERTAINTY_HIGH,     # for incomplete or nearly circular tracks
            self.LINK_SELECTED,
            self.UNLINK_SELECTED)

        # set up a bank of three combo boxes of operations for convenience access for common tasks
        self.operation1Cmbx.addItems(trackOperationMethods)
        self.operation1Cmbx.setCurrentIndex(0)
        self.operation1Btn.clicked.connect(self.handleOperation1Btn)

        self.operation2Cmbx.addItems(trackOperationMethods)
        self.operation2Cmbx.setCurrentIndex(1)
        self.operation2Btn.clicked.connect(self.handleOperation2Btn)

        self.operation3Cmbx.addItems(trackOperationMethods)
        self.operation3Cmbx.setCurrentIndex(3)
        self.operation3Btn.clicked.connect(self.handleOperation3Btn)

        # in the Trackway tab:
        self.showTrackwayBtn.clicked.connect(self.handleShowTrackwayBtn)
        self.hideTrackwayBtn.clicked.connect(self.handleHideTrackwayBtn)
        self.selectTrackwayBtn.clicked.connect(self.handleSelectTrackwayBtn)
        self.updateLayersBtn.clicked.connect(self.handleUpdateLayersBtn)
        self.showAllTrackwaysBtn.clicked.connect(self.handleShowAllTrackwaysBtn)
        self.hideAllTrackwaysBtn.clicked.connect(self.handleHideAllTrackwaysBtn)
        self.selectAllTrackwaysBtn.clicked.connect(self.handleSelectAllTrackwaysBtn)
        self.exportAllTrackwaysBtn.clicked.connect(self.handleExportAllTrackwaysBtn)
        self.erasePathsBtn.clicked.connect(self.handleErasePathsBtn)

        # in the Tracksite tab:
        self.trackSiteIndexSbx.valueChanged.connect(self.handleTrackSiteIndexSbx)
        self.svgFileNameLE.textChanged.connect(self.handleSvgNameLE)
        self.openSvgFileBtn.clicked.connect(self.handleSvgOpenBtn)
        self.saveSvgFileBtn.clicked.connect(self.handleSvgSaveBtn)
        self.addSelectedBtn.clicked.connect(self.handleSvgAddSelectedBtn)

        self.currentDrawing = None

        # populate the track site data based on the initial value of the index
        self.handleTrackSiteIndexSbx()

#===================================================================================================
#                                                                                        P U B L I C
#
#___________________________________________________________________________________________________ enableTrackUI
    def enableTrackUI(self, value):
        """ The track ui is either enabled (if passed True) or disabled (if passed False). """
        self.widthLbl.setEnabled(value)
        self.widthSbx.setEnabled(value)
        self.widthUncertaintySbx.setEnabled(value)

        self.lengthLbl.setEnabled(value)
        self.lengthSbx.setEnabled(value)
        self.lengthUncertaintySbx.setEnabled(value)

        self.rotationSbx.setEnabled(value)
        self.rotationUncertaintySbx.setEnabled(value)

        self.completedCkbx.setEnabled(value)
        self.markedCkbx.setEnabled(value)
        self.hiddenCkbx.setEnabled(value)

        self.lengthRatioSbx.setEnabled(value)

        self.noteLE.setEnabled(value)
        self.trackNameLE.setEnabled(value)
        self.trackIndexLE.setEnabled(value)

#___________________________________________________________________________________________________ getAllTracksInMaya
    def getAllTracksInMaya(self):
        """ Returns a list of all tracks that are currently loaded into Maya. """
        uidList = self.getUidList()

        # and from this list of UIDs, compile the corresponding list of track instances
        tracks  = []
        for uid in uidList:
            tracks.append(self.getTrackByUid(uid))
        return tracks if len(tracks) > 0 else None

#___________________________________________________________________________________________________ getCompletedTracks
    def getCompletedTracks(self, completed, uidList=None):
        """ Returns a list of all tracks within the scene that are either completed or incomplete,
            depending on the boolean kwarg. """
        if not uidList:
            uidList = self.getUidList()
        # now, given a list of UIDs of those track currently in the Maya scene, determine which
        # are completed (or incomplete), and return those as a list of tracks
        tracks = self.getFlaggedTracks(uidList, SourceFlagsEnum.COMPLETED, completed)
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
            self.getSession()
            session = model.createSession()
            query   = session.query(model)
            batch   = uidList[i*size : (i + 1)*size]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.sourceFlags.op('&')(flag) == state)
            entries += query.all()
            i       += 1
            self.closeSession(commit=False)

        if i*size < len(uidList):
            session = model.createSession()
            query   = session.query(model)
            batch   = uidList[i*size :]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.sourceFlags.op('&')(flag) == state)
            entries += query.all()
            self.closeSession(commit=False)

        return entries if len(entries) > 0 else None

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

#___________________________________________________________________________________________________ getNextTrack
    def getNextTrack(self, track):
        """ This method just encapsulates the session getter. """
        return track.getNextTrack(self.getSession())

#___________________________________________________________________________________________________ getPreviousTrack
    def getPreviousTrack(self, track):
        """ This method just encapsulates the session getter. """
        return track.getPreviousTrack(self.getSession())

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
                'Unable to get selected UID list from Maya',
                'Error')
            return None

        # from this UID list, create the corresponding track list
        selectedUidList = result.payload['selectedUidList']
        if len(selectedUidList) == 0:
            return None

        tracks = []
        for uid in selectedUidList:
            tracks.append(self.getTrackByUid(uid))
        return tracks

#___________________________________________________________________________________________________ getSiteMap
    def getSiteMap(self, index):
        """ If the track site specified by the given index is valid, a Tracks_TrackSite instance is
            returned, otherwise None. """

        model   = Tracks_SiteMap.MASTER
        session = self.getSession()
        siteMap = session.query(model).filter(model.index == index).first()

        # close this session to release the database lock
        session.close()

        # an indicator that the site siteMap table is not yet populated for this index, check the scale
        if not siteMap or siteMap.scale == 0:
            return None
        else:
            return siteMap

#___________________________________________________________________________________________________ getTrackByUid
    def getTrackByUid(self, uid):
        """ This gets the track model instance corresponding to a given uid. """
        model = Tracks_Track.MASTER
        return model.getByUid(uid, self.getSession())

#___________________________________________________________________________________________________ getTracksByUid
    def getTracksByProperties(self, **kwargs):
        """ This gets the track model instances with specified properties. """
        model = Tracks_Track.MASTER
        return model.getByProperties(self.getSession(), **kwargs)

#___________________________________________________________________________________________________ getTrackByName
    def getTrackByName(self, name, **kwargs):
        """ This gets the track model instance by name (plus trackway properties). """
        model = Tracks_Track.MASTER
        return model.getByName(name, self.getSession(), **kwargs)

#___________________________________________________________________________________________________ getTrackNode
    def getTrackNode(self, track):
        """ This gets the (transient) node name corresponding to a given track, or returns None if
            that track has not yet been loaded into Maya. """
        # ask for nothing, then get nothing in return
        if track is None:
            return None

        conn   = nimble.getConnection()
        result = conn.runPythonModule(
            GetTrackNodeData,
            uid=track.uid,
            nodeName=track.nodeName,
            runInMaya=True)

        if result.payload.get('error'):
            print 'Error in updateFromNode:', result.payload.get('message')
            return False

        return result.payload.get('nodeName')

#___________________________________________________________________________________________________ getTrackSetNode
    def getTrackSetNode(cls):
        """ This is redundunt with the version in TrackSceneUtils, but running locally. Note that
            if no TrackSetNode is found, it does not create one. """
        for node in cmds.ls(exactType='objectSet'):
            if node == CadenceEnvironment.TRACKWAY_SET_NODE_NAME:
                return node

        return None

 #__________________________________________________________________________________________________ getTrackSeries
    def getTrackSeries(self):
        """ Steps backward from any selected track to the first track, then creates a list of all
            track models in a given series, in order. """
        series = []
        track  = self.getFirstTrack()

        while track:
            series.append(track)
            track = self.getNextTrack(track)

        return series if len(series) > 0 else None

#___________________________________________________________________________________________________ getTrackway
    def getTrackway(self, uidList, trackwayName):
        """ Creates a list of all tracks that have Maya tracknodes (hence are in the uidList) and
            have the specified trackwayName (hence trackway type and trackway number. """
        model   = Tracks_Track.MASTER
        size    = 200
        iMax    = len(uidList)/size
        i       = 0
        entries = []
        type    = trackwayName[0]
        number  = trackwayName[1:]

        while i < iMax:
            self.getSession()
            session = model.createSession()
            query   = session.query(model)
            batch   = uidList[i*size : (i + 1)*size]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.trackwayType == type)
            query   = query.filter(model.trackwayNumber == number)
            entries += query.all()
            i       += 1
            self.closeSession(commit=False)

        if i*size < len(uidList):
            session = model.createSession()
            query   = session.query(model)
            batch   = uidList[i*size :]
            query   = query.filter(model.uid.in_(batch))
            query   = query.filter(model.trackwayType == type)
            query   = query.filter(model.trackwayNumber == number)
            entries += query.all()
            self.closeSession(commit=False)

        return entries if len(entries) > 0 else None

#___________________________________________________________________________________________________ getTrackwayNames
    def getTrackwayNames(self, site, level, sector):
        """ Compiles a list of the names of trackways for a specified site/level/sector. In some
            tracksites, for some levels, a given trackway name (such as S1) may appear in two
            sectors. Hence it is necessary to fully qualify the trackway name with site, level, and
            sector. """
        props = { TrackPropEnum.SITE.name:site,
                  TrackPropEnum.LEVEL.name:level,
                  TrackPropEnum.SECTOR.name:sector }
        # now get all tracks in this trackway (that share this combination of site/level/sector)
        tracks = self.getTracksByProperties(**props)

        # that list of track instances will be used to compile all trackway names (with duplicates)
        trackwayNames = []
        for track in tracks:
            trackwayName = '%s%s' % (track.trackwayType, track.trackwayNumber)
            trackwayNames.append(trackwayName)

        # remove the duplicates, sort 'em and return 'em
        trackwayNames = list(set(trackwayNames))
        trackwayNames.sort()

        return trackwayNames if len(trackwayNames) > 0 else None

#___________________________________________________________________________________________________ getTrackwayPropertiesFromUI
    def getTrackwayPropertiesFromUI(self):
        """ Returns a dictionary of trackway properties, extracted from the UI. """
        dict = { TrackPropEnum.SITE.name:self.siteLE.text(),
            TrackPropEnum.YEAR.name:self.yearLE.text(),
            TrackPropEnum.SECTOR.name:self.sectorLE.text(),
            TrackPropEnum.LEVEL.name:self.levelLE.text() }

        trackway = self.trackwayLE.text()
        if trackway:
            dict[TrackPropEnum.TRACKWAY_TYPE.name]   = self.trackwayLE.text()[0]
            dict[TrackPropEnum.TRACKWAY_NUMBER.name] = self.trackwayLE.text()[1:]

        return dict

#___________________________________________________________________________________________________ getUidList
    def getUidList(self):
        """ Returns a list of the UIDs of all track nodes currently loaded into Maya. """
        conn   = nimble.getConnection()
        result = conn.runPythonModule(GetUidList, runInMaya=True)

        # and check to see if the remote command execution was successful
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                self,
                'Failed UID Query',
                'Unable to get UID list from Maya',
                'Error')
            return None

        return result.payload['uidList']
#___________________________________________________________________________________________________ selectTrack
    def selectTrack(self, track):
        """ Select the node corresponding to this track model instance, then focus the camera
            upon this node. """
        cmds.select(self.getTrackNode(track))
        self.setCameraFocus()

#===================================================================================================
#                                                                  T R A C K  U I  U T I L I T I E S

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
        self.lockedCkbx.setChecked(False)
        self.markedCkbx.setChecked(False)
        self.hiddenCkbx.setChecked(False)

        self.lengthRatioSbx.setValue(0)

        self.noteLE.setText(u'')
        self.trackNameLE.setText(u'')
        self.trackIndexLE.setText(u'')

#___________________________________________________________________________________________________ clearTrackSiteUI
    def clearTrackSiteUI(self):
        """ This clears the track site data in the Trackways tab. """
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

#___________________________________________________________________________________________________ clearTrackwayUI
    def clearTrackwayUI(self):
        """ Clears the banner at the top of the UI. """
        self.siteLE.setText('')
        self.yearLE.setText('')
        self.sectorLE.setText('')
        self.levelLE.setText('')
        self.trackwayLE.setText('')

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

        rotation = dict[TrackPropEnum.ROTATION.name]
        if rotation < 0.0:
            rotation += 360.0
        self.rotationSbx.setValue(rotation)

        self.rotationUncertaintySbx.setValue(dict[TrackPropEnum.ROTATION_UNCERTAINTY.name])

        # set the checkboxes 'Completed', 'Locked', and 'Marked' according to the source flags
        f = dict[TrackPropEnum.SOURCE_FLAGS.name]
        self.completedCkbx.setChecked(SourceFlagsEnum.get(f, SourceFlagsEnum.COMPLETED))

        self.lockedCkbx.setChecked(SourceFlagsEnum.get(f, SourceFlagsEnum.LOCKED))
        self.markedCkbx.setChecked(SourceFlagsEnum.get(f, SourceFlagsEnum.MARKED))

        # likewise the special 'Hidden' attribute
        self.hiddenCkbx.setChecked(dict[TrackPropEnum.HIDDEN.name])

        self.lengthRatioSbx.setValue(dict[TrackPropEnum.LENGTH_RATIO.name])

        self.noteLE.setText(dict[TrackPropEnum.NOTE.name])

        left   = dict[TrackPropEnum.LEFT.name]
        pes    = dict[TrackPropEnum.PES.name]
        number = dict[TrackPropEnum.NUMBER.name]
        index  = dict[TrackPropEnum.INDEX.name]
        name   = (u'L' if left else u'R') + (u'P' if pes else u'M') + number if number else u'-'
        self.trackNameLE.setText(name)
        self.trackIndexLE.setText(unicode(index))

        # now, depending on whether this track is locked or unlocked, disable/enable the UI
        locked = SourceFlagsEnum.get(f, SourceFlagsEnum.LOCKED)
        if locked:
            self.enableTrackUI(False)
        else:
            self.enableTrackUI(True)

#___________________________________________________________________________________________________ refreshTrackSiteUI
    def refreshTrackSiteUI(self, siteMap):
        """ The data for the given track site index is updated. """
        self.trackSiteNameLbl.setText(siteMap.filename)

        self.federalEastLbl.setText(unicode(siteMap.federalEast))
        self.federalNorthLbl.setText(unicode(siteMap.federalNorth))

        self.mapLeftLbl.setText(unicode(siteMap.left))
        self.mapTopLbl.setText(unicode(siteMap.top))

        self.mapWidthLbl.setText(unicode(siteMap.width))
        self.mapHeightLbl.setText(unicode(siteMap.height))

        self.xFedLbl.setText(unicode(siteMap.xFederal))
        self.yFedLbl.setText(unicode(siteMap.yFederal))

        self.transXLbl.setText(unicode(siteMap.xTranslate))
        self.transZLbl.setText(unicode(siteMap.zTranslate))
        self.rotXLbl.setText(unicode(siteMap.xRotate))
        self.rotYLbl.setText(unicode(siteMap.yRotate))
        self.rotZLbl.setText(unicode(siteMap.zRotate))
        self.scaleLbl.setText(unicode(siteMap.scale))

#___________________________________________________________________________________________________ refreshTrackwayUI
    def refreshTrackwayUI(self, dict):
        """ The trackway UI is populated with values based on the specified properties. """
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

        type   = dict.get(TrackPropEnum.TRACKWAY_TYPE.name)
        number = dict.get(TrackPropEnum.TRACKWAY_NUMBER.name)
        if type and number:
            trackway = type + number
        else:
            trackway = ''
        self.trackwayLE.setText(trackway)

#___________________________________________________________________________________________________ refreshTrackCountsUI
    def refreshTrackCountsUI(self):
        """ Run a script to return a list of all Maya Track Nodes so we can get a count of both the
            total number of tracks in the scene and of those that are completed. """
        uidList = self.getUidList()

        if not uidList:
            totalTrackCount = 0
            completedCount  = 0
            selectedCount   = 0
        else:
            totalTrackCount = len(uidList)
            completedTracks = self.getCompletedTracks(True, uidList)
            completedCount  = len(completedTracks) if completedTracks else 0
            selectedCount   = len(cmds.ls(selection=True))

        # Display the total number of tracks currently in the Maya scene
        self.totalTrackCountLbl.setText('Total:  ' + unicode(totalTrackCount))

        # Now determine how many tracks have their COMPLETED source flag set
        self.completedTrackCountLbl.setText('Completed:  ' + unicode(completedCount))

        # And show how many are currently selected
        self.selectedTrackCountLbl.setText('Selected:  ' + unicode(selectedCount))


#===================================================================================================
#                                                                T R A C K   T A B   H A N D L E R S
#___________________________________________________________________________________________________ handleCompletedCkbx
    def handleCompletedCkbx(self):
        """ The COMPLETED source flag for the selected track (or tracks) is set or cleared, based
            on the value of the checkbox. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()

        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        t.completed = self.completedCkbx.isChecked()

        t.updateNode()
        self.closeSession(commit=True)
        self.refreshTrackCountsUI()

        # finally, if is set to completed, then lock it (and that requires unlocking to set back
        # to uncompleted state
        if self.completedCkbx.isChecked():
            self.lockedCkbx.setChecked(True)

#___________________________________________________________________________________________________ handleCountsBtn
    def handleCountsBtn(self):
        """ This updates the total number of tracks in the scene and the number completed. """
        self.refreshTrackCountsUI()

#___________________________________________________________________________________________________ handleErasePathsBtn
    def handleErasePathsBtn(self):
        """ Deletes all curves representing paths (e.g., connecting a given track series). """
        curves = cmds.editDisplayLayerMembers(self.PATH_LAYER, query=True, noRecurse=True)
        for curve in curves:
            cmds.delete(curve)
        cmds.delete(self.PATH_LAYER)

#___________________________________________________________________________________________________ handleExportAllTrackwaysBtn
    def handleExportAllTrackwaysBtn(self):
        """ Creates an svg file (to scale with the tracksite) indicating the position and the
            uncertainty in width and length of each track. """
        layers = cmds.ls( type='displayLayer')
        nodes  = []
        if not layers:
            return
        for layer in layers:
            print 'layer = %s' % layer
            if layer.endswith(self.LAYER_SUFFIX):
                nodes.extend(cmds.editDisplayLayerMembers(layer, query=True, noRecurse=True))
        cmds.select(nodes)
        print "%s-many noders selected" % len(nodes)

#___________________________________________________________________________________________________ handleExtrapolateNext
    def handleExtrapolateNext(self):
        """ Given at least two tracks in a series, this method allows the next track to be placed in
            a straight line extrapolation of the given track and its previous track. The next track
            node is also given the averaged orientation and length and width uncertainties
            associated with the last two tracks. """
        self.getSession()

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
            PyGlassBasicDialogManager.openOk(
                self,
                'No next track to extrapolate!',
                '%s is the last in this series' % t.name)
            return

        t.updateFromNode() # use this opportunity to capture current state of the Maya node

        # take a linear step forward based on the number of steps in between the last two (p and t)
        # and between t and n.  First, compute tp, the difference in track number from p to t
        tp = int(t.number) - int(p.number)

        # deal with the degenerate case of no previous track p, wherein p had been set to t above
        if tp == 0:
            tp = 1

        # determine the equivalent displacements in x and z for one step (since the distance from
        # p to t might represent multiple intermediate steps that were never recorded)
        # note that if the previous point is at (0, 0) then don't extrapolate n; just make the
        # delta's dx and dy both zero and leave n coincident with t.
        if p.x == 0 and p.z == 0:
            dx = 0
            dz = 0
        else:
            dx = float(t.x - p.x)/tp
            dz = float(t.z - p.z)/tp

        # now to extrapolate from t to n, we also have to be concerned with possible missing
        # intervening steps, so compute the difference in track number from n to t
        nt  = int(n.number) - int(t.number)
        n.x = t.x + nt*dx
        n.z = t.z + nt*dz

        # if track width was not measured originally, inherit t's width and posit high uncertainty
        # but be careful to check if t's values were measured in the first place
        if n.widthMeasured == 0.0:
            n.width            = t.width
            n.widthUncertainty = self.DIMENSION_UNCERTAINTY_HIGH
        else:
            n.width            = n.widthMeasured
            n.widthUncertainty = t.widthUncertainty

        # similarly for track length, based on whether it was measured originally
        if n.lengthMeasured == 0.0:
            n.length            = t.length
            n.lengthUncertainty = self.DIMENSION_UNCERTAINTY_HIGH
        else:
            n.length            = n.lengthMeasured
            n.lengthUncertainty = t.lengthUncertainty

        # and presume rotational uncertainty will be high if both measured values are zero
        if n.widthMeasured == 0.0 and n.lengthMeasured == 0.0:
            n.rotationUncertainty = self.ROTATION_UNCERTAINTY_HIGH
        else:
            n.rotationUncertainty = t.rotationUncertainty

        # assign to the next track the length ratio and rotation of the current track
        n.lengthRatio = t.lengthRatio
        n.rotation    = t.rotation
        n.completed   = False
        n.locked      = False

        # update the Maya node and the UI
        n.updateNode()
        self.selectTrack(n)
        self.refreshTrackUI(n.toDict())
        self.setCameraFocus()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleExtrapolatePrevious
    def handleExtrapolatePrevious(self):
        """ Given at least two tracks in a series, this method allows the previous track to be
            placed in a straight line extrapolation of the given track and its next track. The
            previous track node is also given the averaged orientation and length and width
            uncertainties associated with the the next two tracks. """
        self.getSession()

        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        # extrapolate from the first of possibly multiple selected tracks
        t = selectedTracks[0]
        n = self.getNextTrack(t)

        # the first track must be in place, but if attempting to extrapolate the second track based
        # on just the first track, there is no displacement yet on which to estimate forward
        # progress (so drag that track manually off of the first track).
        if n is None:
            n = t

        # and make sure there is a previous track to extrapolate
        p = self.getPreviousTrack(t)
        if p is None:
            PyGlassBasicDialogManager.openOk(
                 self,
                'No previous track',
                '%s is the first in this series' % t.name)
            return

        t.updateFromNode() # use this opportunity to capture current state of the Maya node

        # take a linear step backward based on the number of steps in between the next two (t and n)
        # and between p and t.  First compute nt, the difference in track number from t to n
        nt = int(n.number) - int(t.number)

        # deal with the degenerate case of no next track n, wherein n had been set to t above
        if nt == 0:
            nt = 1

        # determine the equivalent displacements in x and z for one step (since the distance from
        # t to n might represent multiple intermediate steps that were never recorded)
        # note that if the next point is at (0, 0) then don't extrapolate p; just make the
        # delta's dx and dy both zero and leave p coincident with t.
        if n.x == 0 and n.z == 0:
            dx = 0
            dz = 0
        else:
            dx = float(n.x - t.x)/nt
            dz = float(n.z - t.z)/nt

        # now to extrapolate from t back to p, we also have to be concerned with possible missing
        # intervening steps, so compute the difference in track number from p to t
        nt  = int(t.number) - int(p.number)
        p.x = t.x - nt*dx
        p.z = t.z - nt*dz

        # if track width was not measured originally, inherit t's width and posit high uncertainty
        # but be careful to check if t's values were measured in the first place
        if p.widthMeasured == 0.0:
            p.width            = t.width
            p.widthUncertainty = self.DIMENSION_UNCERTAINTY_HIGH
        else:
            p.width            = p.widthMeasured
            p.widthUncertainty = t.widthUncertainty

        # similarly for track length, based on whether it was measured originally
        if p.lengthMeasured == 0.0:
            p.length            = t.length
            p.lengthUncertainty = self.DIMENSION_UNCERTAINTY_HIGH
        else:
            p.length            = p.lengthMeasured
            p.lengthUncertainty = t.lengthUncertainty

        # and presume rotational uncertainty will be high if both measured values are zero
        if p.widthMeasured == 0.0 and p.lengthMeasured == 0.0:
            p.rotationUncertainty = self.ROTATION_UNCERTAINTY_HIGH
        else:
            p.rotationUncertainty = t.rotationUncertainty

        # assign to the next track the length ratio and rotation of the current track
        p.lengthRatio = t.lengthRatio
        p.rotation    = t.rotation

        # update the Maya node and the UI
        p.updateNode()
        self.selectTrack(p)
        self.refreshTrackUI(p.toDict())
        self.setCameraFocus()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleFetchByName
    def handleFetchByName(self):
        """ This fetches the track specified by the trackwayUI banner, and translates that track
            directly under the CadenceCam. """
        # saves state of tracks that may be selected
        selectedTracks = self.getSelectedTracks()
        if selectedTracks and len(selectedTracks) == 1:
            t = selectedTracks[0]
            t.updateFromNode()

        # with that out of the way, now get the name for the new trackway and track to be fetched
        name   = self.trackNameLE.text()
        tracks = self.getTrackByName(name, **self.getTrackwayPropertiesFromUI())

        # just give up if it is not found
        if not tracks or len(tracks) > 1:
            PyGlassBasicDialogManager.openOk(
                self,
                'Unsuccessful',
                'Requested track not found',
                'Error')
            return

        if not cmds.objExists('CadenceCam'):
            self.initializeCadenceCam()

        t = tracks[0]

        # if track length or width (or both) were not measured originally, posit high uncertainties
        if t.widthMeasured == 0.0 or t.lengthMeasured == 0.0:
            t.widthUncertainty    = self.DIMENSION_UNCERTAINTY_HIGH
            t.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_HIGH
            t.rotationUncertainty = self.ROTATION_UNCERTAINTY_HIGH
        else:
            t.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
            t.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
            t.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE

        # set this track's position to that of the CadenceCam
        t.x = cmds.getAttr(self.CADENCE_CAM + '.translateX')
        t.z = cmds.getAttr(self.CADENCE_CAM + '.translateZ')

        t.updateNode()
        cmds.select(self.getTrackNode(t))
        t.updateFromNode()
        self.refreshTrackUI(t.toDict())

#___________________________________________________________________________________________________ handleFetchByIndex
    def handleFetchByIndex(self):
        """ This fetches the track specified by specified index in the trackwayUI banner,
            and translates that track directly under the CadenceCam. """
        # saves state of tracks that may be selected
        selectedTracks = self.getSelectedTracks()
        if selectedTracks and len(selectedTracks) == 1:
            t = selectedTracks[0]
            t.updateFromNode()

        # with that out of the way, now attempt to get the track instance with the specified index
        tracks = self.getTracksByProperties(index=self.trackIndexLE.text())

        # just give up if it is not found
        if not tracks or len(tracks) > 1:
            PyGlassBasicDialogManager.openOk(
                self,
               'Unsuccessful',
               'Requested track not found',
               'Error')
            return

        if not cmds.objExists(self.CADENCE_CAM):
            self. initializeCadenceCam()

        t = tracks[0]

        # if track length or width (or both) were not measured originally, posit high uncertainties
        if t.widthMeasured == 0.0 or t.lengthMeasured == 0.0:
            t.widthUncertainty    = self.DIMENSION_UNCERTAINTY_HIGH
            t.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_HIGH
            t.rotationUncertainty = self.ROTATION_UNCERTAINTY_HIGH
        else:
            t.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
            t.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
            t.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE

        # set this track's position to that of the CadenceCam
        t.x = cmds.getAttr(self.CADENCE_CAM + '.translateX')
        t.z = cmds.getAttr(self.CADENCE_CAM + '.translateZ')

        t.updateNode()
        cmds.select(self.getTrackNode(t))
        t.updateFromNode()
        self.refreshTrackUI(t.toDict())
        self.refreshTrackwayUI(t.toDict())

# __________________________________________________________________________________________________ handleFirstBtn
    def handleFirstBtn(self):
        """ Get the first track, select the corresponding node, and focus the camera on it. """
        t = self.getFirstTrack()
        if t is None:
            return

        self.selectTrack(t)
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        dict = t.toDict()

        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

#___________________________________________________________________________________________________ handleHideAllTrackwaysBtn
    def handleHideAllTrackwaysBtn(self):
        """ This sets all layers invisible. """
        self.handleShowAllTrackwaysBtn(False)

#___________________________________________________________________________________________________ handleHideTrackwayBtn
    def handleHideTrackwayBtn(self):
        """ This hides the layer specified by the current value in the trackway combo box. """
        self.handleShowTrackwayBtn(False)

#___________________________________________________________________________________________________ handleHiddenCkbx
    def handleHiddenCkbx(self):
        """ The selected track has its HIDDEN flag set (or cleared). """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        if not t.hidden:
            # if the selected track is not already hidden, set hidden if confirmed
            result = PyGlassBasicDialogManager.openYesNo(
                self,
                u'CONFIRMATION REQUIRED',
                u'Are you sure you want to set this track to HIDDEN?',
                False)
            if result:
                t.hidden = True
        else:
            # if the selected track is already hidden, set it visible if confirmed
            result = PyGlassBasicDialogManager.openYesNo(
                self,
                u'CONFIRMATION REQUIRED',
                u'This track is currently HIDDEN.  Do you wish to make it visible?',
                False)
            if result:
                t.hidden = False

        # if this leaves the track hidden, place it back at the origin, and unoriented
        if t.hidden:
            t.x        = 0.0
            t.z        = 0.0
            t.rotation = 0.0

        t.updateNode()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleInterpolate
    def handleInterpolate(self):
        """ Based on a previous and next tracks to a given (single) selected track node t, the
            parameters are interpolated. """
        self.getSession()

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
        self.selectTrack(t)
        self.refreshTrackUI(t.toDict())
        self.setCameraFocus()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleLastBtn
    def handleLastBtn(self):
        """ Get the last track, select the corresponding node, focus the camera on it, and update
            the UIs"""
        t = self.getLastTrack()
        if t is None:
            return

        self.selectTrack(t)
        dict = t.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

#___________________________________________________________________________________________________ handleLengthSbx
    def handleLengthSbx(self):
        """ The length of the selected track is adjusted. Length is stored in the database in
            fractional meters but send to Maya in cm and displayed in integer cm units."""
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.length = self.lengthSbx.value()/100.0
        t.updateNode()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleLengthUncertaintySbx
    def handleLengthUncertaintySbx(self):
        """ The length uncertainty of the selected track is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.lengthUncertainty = self.lengthUncertaintySbx.value()/100.0
        t.updateNode()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleLengthRatioSbx
    def handleLengthRatioSbx(self):
        """ The ratio from 0.0 to 1.0 representing fraction of distance from the 'anterior' extreme
            of the track to the 'center' (point of greatest width). """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()

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

        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleLink
    def handleLink(self):
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
        self.refreshTrackUI(t.toDict())
        self.setCameraFocus()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleLockedCkbx
    def handleLockedCkbx(self):
        """ The selected track has its LOCKED flag set (or cleared). """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()

        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        t.locked = self.lockedCkbx.isChecked()

        if t.locked:
            self.enableTrackUI(False)
        else:
            self.enableTrackUI(True)

        dict = t.toDict()
        self.refreshTrackUI(dict)

        t.updateNode()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleMarkedCkbx
    def handleMarkedCkbx(self):
        """ This track has its MARKED source flag set or cleared, based on the value of the
            checkbox. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()

        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        t.marked = self.markedCkbx.isChecked()
        t.updateNode()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleNextBtn
    def handleNextBtn(self):
        """ Get the next track, select its corresponding node, and focus the camera on it. If
            there is no next node, just leave the current node selected. """
        t = self.getLastSelectedTrack()
        if t is None:
            return

        n = self.getNextTrack(t)
        if n is None:
            PyGlassBasicDialogManager.openOk(
                self,
                'No next track',
                '%s is the last in this series' % t.name)
            return

        self.selectTrack(n)
        n.updateFromNode() # use this opportunity to capture the current state of the Maya node
        dict = n.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

#___________________________________________________________________________________________________ handleNoteLE
    def handleNoteLE(self):
        """ The note line edit is handled here. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()

        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        t.note = self.noteLE.text()
        t.updateNode()

        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleOperation
    def handleOperation(self, op):
        """ A number of operations can be performed on (one or more) selected track(s). """
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

        elif op == self.LINK_SELECTED:
            self.handleLink()

        elif op == self.UNLINK_SELECTED:
            self.handleUnlink()

#___________________________________________________________________________________________________ handleOperation1Btn
    def handleOperation1Btn(self):
        """ Passes the selected operation to be performed. """
        self.handleOperation(self.operation1Cmbx.currentText())

#___________________________________________________________________________________________________ handleOperation2Btn
    def handleOperation2Btn(self):
        """ Passes the selected operation to be performed. """
        self.handleOperation(self.operation2Cmbx.currentText())

#___________________________________________________________________________________________________ handleOperation3Btn
    def handleOperation3Btn(self):
        """ Passes the selected operation to be performed. """
        self.handleOperation(self.operation3Cmbx.currentText())

#___________________________________________________________________________________________________ handlePrevBtn
    def handlePrevBtn(self):
        """ Get the previous track, select its corresponding node, and focus the camera on it. If
            there is no previous node, just leave the current node selected. """
        t = self.getFirstSelectedTrack()
        if t is None:
            return

        p = self.getPreviousTrack(t)
        if p is None:
            PyGlassBasicDialogManager.openOk(
                self,
                'No previous track',
                '%s is the first in this series' % t.name)
            return

        self.selectTrack(p)
        p.updateFromNode() # use this opportunity to capture the current state of the Maya node

        dict = p.toDict()
        self.refreshTrackUI(dict)
        self.refreshTrackwayUI(dict)

#___________________________________________________________________________________________________ handlePullBtn
    def handlePullBtn(self):
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

        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleRotationSBox
    def handleRotationSbx(self):
        """ The rotation of the selected track (manus or pes) is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture current state of the Maya node
        t.rotation = self.rotationSbx.value()
        t.updateNode()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleRotationUncertaintySbx
    def handleRotationUncertaintySbx(self):
        """ The track node has a pair of nodes that represent the angular uncertainty (plus or minus
            some value set up in the rotation uncertainty spin box (calibrated in degrees). """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.rotationUncertainty = self.rotationUncertaintySbx.value()
        t.updateNode()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleSelect1Btn
    def handleSelect1Btn(self):
        """ The various options for track selection are dispatched from here. """
        self.getSession()

        if self.selectionMethod1Cmbx.currentText() == self.FETCH_TRACK_BY_NAME:
            self.handleFetchByName()

        elif self.selectionMethod1Cmbx.currentText() == self.FETCH_TRACK_BY_INDEX:
            self.handleFetchByIndex()

        elif self.selectionMethod1Cmbx.currentText() == self.SELECT_NEXT_INCOMPLETE:
            self.handleSelectNextIncomplete()

        elif self.selectionMethod1Cmbx.currentText() == self.SELECT_TRACK_BY_NAME:
            self.handleSelectByName()

        elif self.selectionMethod1Cmbx.currentText() == self.SELECT_TRACK_BY_INDEX:
            self.handleSelectByIndex()

        elif self.selectionMethod1Cmbx.currentText() == self.SELECT_SERIES_BEFORE:
            self.handleSelectSeriesBefore()

        elif self.selectionMethod1Cmbx.currentText() == self.SELECT_SERIES_AFTER:
            self.handleSelectSeriesAfter()

        elif self.selectionMethod1Cmbx.currentText() == self.SELECT_TRACK_SERIES:
            self.handleSelectSeries()

        elif self.selectionMethod1Cmbx.currentText() == self.SELECT_ALL_COMPLETED:
            self.handleSelectCompleted(True)

        elif self.selectionMethod1Cmbx.currentText() == self.SELECT_ALL_INCOMPLETE:
            self.handleSelectCompleted(False)

        elif self.selectionMethod1Cmbx.currentText() == self.SELECT_ALL_MARKED:
            self.handleSelectMarked(True)

        self.refreshTrackCountsUI()

#___________________________________________________________________________________________________ handleSelect2Btn
    def handleSelect2Btn(self):
        """ The various options for track selection are dispatched from here. """
        self.getSession()

        if self.selectionMethod2Cmbx.currentText() == self.FETCH_TRACK_BY_NAME:
            self.handleFetchByName()

        elif self.selectionMethod2Cmbx.currentText() == self.SELECT_NEXT_INCOMPLETE:
            self.handleSelectNextIncomplete()

        elif self.selectionMethod2Cmbx.currentText() == self.SELECT_TRACK_BY_NAME:
            self.handleSelectByName()

        elif self.selectionMethod2Cmbx.currentText() == self.SELECT_TRACK_BY_INDEX:
            self.handleSelectByIndex()

        elif self.selectionMethod2Cmbx.currentText() == self.SELECT_SERIES_BEFORE:
            self.handleSelectSeriesBefore()

        elif self.selectionMethod2Cmbx.currentText() == self.SELECT_SERIES_AFTER:
            self.handleSelectSeriesAfter()

        elif self.selectionMethod2Cmbx.currentText() == self.SELECT_TRACK_SERIES:
            self.handleSelectSeries()

        elif self.selectionMethod2Cmbx.currentText() == self.SELECT_ALL_COMPLETED:
            self.handleSelectCompleted(True)

        elif self.selectionMethod2Cmbx.currentText() == self.SELECT_ALL_INCOMPLETE:
            self.handleSelectCompleted(False)

        elif self.selectionMethod2Cmbx.currentText() == self.SELECT_ALL_MARKED:
            self.handleSelectMarked(True)

        self.refreshTrackCountsUI()

#___________________________________________________________________________________________________ handleSelectAllTrackwaysBtn
    def handleSelectAllTrackwaysBtn(self):
        """ A list of all members (track nodes) across all layers is compiled and sent off to be
            selected. """
        layers = cmds.ls( type='displayLayer')
        nodes  = []
        for layer in layers:
            if layer.endswith(self.LAYER_SUFFIX):
               nodes.extend(cmds.editDisplayLayerMembers(layer, query=True, noRecurse=True))
        cmds.select(nodes)
        print "%s nodes selected" %len(nodes)

#___________________________________________________________________________________________________ handleSelectByIndex
    def handleSelectByIndex(self):
        """ Handles the selection of a track by the index of its catalog entry. """
        tracks = self.getTracksByProperties(index=self.trackIndexLE.text())
        if not tracks:
            return

        if len(tracks) != 1:
            return

        t = tracks[0]
        self.selectTrack(t)

        self.setCameraFocus()
        dict = t.toDict()
        self.refreshTrackwayUI(dict)
        self.refreshTrackUI(dict)

#___________________________________________________________________________________________________ handleSelectByName
    def handleSelectByName(self):
        """ Handles the selection of a track by name. """
        tracks = self.getTrackByName(self.trackNameLE.text(), **self.getTrackwayPropertiesFromUI())
        if not tracks:
            return

        if len(tracks) != 1:
            return

        t = tracks[0]
        self.selectTrack(t)
        self.setCameraFocus()
        self.refreshTrackUI(t.toDict())
#___________________________________________________________________________________________________ handleSelectCadenceCamBtn
    def handleSelectCadenceCamBtn(self):
        """ Handles the selection of the CadenceCam. """
        self.initializeCadenceCam()
        cmds.lookThru(self.CADENCE_CAM)

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

        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleSelectCompleted
    def handleSelectCompleted(self, completed=True):
        """ Selects all completed track nodes (those with UIDs in the scene that have their
            COMPLETED source flag set).  Batch this task into sublists due to limitations. This is
            also used with False passed in to select those tracks that are not yet completed. """
        # turn off all current selections
        cmds.select(clear=True)

        # first get a list of tracks that are either completed or incomplete
        tracks = self.getCompletedTracks(completed=completed)

        if len(tracks) == 0:
            PyGlassBasicDialogManager.openOk(
                 self,
                'None',
                'No %s tracks selected' % 'completed' if completed else 'incomplete')
            return

        # now get a list of the nodes for those tracks, so they can be selected in Maya
        nodes= []
        for t in tracks:
            nodes.append(self.getTrackNode(t))

        # and pass that list to Maya to be selected
        if nodes:
            cmds.select(nodes)
        self.clearTrackUI()
        self.clearTrackwayUI()

#___________________________________________________________________________________________________ handleSelectMarked
    def handleSelectMarked(self, marked=True):
        """ Selects all marked track nodes (those with UIDs in the scene that have their
            MARKED source flag set).  Batch this task into sublists due to limitations. """
        uidList = self.getUidList()

        # so we have a list of UIDs of those track currently in the Maya scene
        tracks = self.getFlaggedTracks(uidList, SourceFlagsEnum.MARKED, marked)

        if not tracks:
            PyGlassBasicDialogManager.openOk(
                self,
                'None',
                'There are no marked tracks in this scene.')
            return

        nodes= []
        for t in tracks:
            nodes.append(self.getTrackNode(t))

        if nodes:
            cmds.select(nodes)

        self.clearTrackUI()
        self.clearTrackwayUI()

#___________________________________________________________________________________________________ handleSelectNextIncomplete
    def handleSelectNextIncomplete(self):
        """ The next incomplete track is selected, focussed upon, and ready to edit. """
        incompleteTracks = self.getCompletedTracks(False)

        if not incompleteTracks:
            PyGlassBasicDialogManager.openOk(
                self,
               'None',
               'All tracks in this series are complete')
            return

        t = incompleteTracks[0]
        t.updateNode()
        cmds.select(self.getTrackNode(t))
        self.refreshTrackwayUI(t.toDict())
        self.refreshTrackUI(t.toDict())
        self.setCameraFocus()

#___________________________________________________________________________________________________ handleSelectPerspectiveBtn
    def handleSelectPerspectiveBtn(self):
        """ This selects the persp camera. """
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

        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleSelectSeries
    def handleSelectSeries(self):
        """ Select in Maya the nodes for the entire track series based on the given selection. """
        tracks = self.getTrackSeries()
        if tracks is None:
            return

        # The path of track series is visualized as a piecewise-linear curve added to the PATH_LAYER
        path  = self.createPathFromTrackSeries(tracks)
        curve = self.createCurve(path)
        layer = self.PATH_LAYER
        self.createLayer(layer)
        cmds.editDisplayLayerMembers(layer, curve, noRecurse=True)

        # Next, select the Maya track nodes
        nodes = list()
        for t in tracks:
            nodes.append(self.getTrackNode(t))
        if len(nodes) == 0:
            return

        cmds.select(nodes)

#___________________________________________________________________________________________________ handleSelectSeriesAfter
    def handleSelectSeriesAfter(self):
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

#___________________________________________________________________________________________________ handleSelectSeriesBefore
    def handleSelectSeriesBefore(self):
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

#___________________________________________________________________________________________________ handleSelectTrackwayBtn
    def handleSelectTrackwayBtn(self, trackway=None):
        """ Trackways are selected by Trackway type and number (such as S18). First put the trackway
            into a layer if it is not already, then select the members of that track. """
        # compose the name of the layer from the trackway name in the combo box
        layer = self.trackwayCmbx.currentText() + self.LAYER_SUFFIX

        # get the members (which are track nodes)
        nodes = cmds.editDisplayLayerMembers(layer, query=True, noRecurse=True)

        # and select 'em
        cmds.select(nodes)

#___________________________________________________________________________________________________ handleSetToMeasuredDimensions
    def handleSetToMeasuredDimensions(self):
        """ The selected track is assigned the length and width as measured in the field. """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        t = selectedTracks[0]

        t.updateFromNode() # use this opportunity to capture the current state of the Maya node

        # override the width and length to reset it to the measured values
        t.width  = t.widthMeasured
        t.length = t.lengthMeasured

        # provide default uncertainty values
        t.widthUncertainty    = self.DIMENSION_UNCERTAINTY_MODERATE
        t.lengthUncertainty   = self.DIMENSION_UNCERTAINTY_MODERATE
        t.rotationUncertainty = self.ROTATION_UNCERTAINTY_MODERATE

        # update the Maya node and the UI
        t.updateNode()
        dict = t.toDict()
        self.selectTrack(t)
        self.refreshTrackUI(dict)
        self.setCameraFocus()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleSetUncertaintyHigh
    def handleSetUncertaintyHigh(self):
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
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleSetUncertaintyLow
    def handleSetUncertaintyLow(self):
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
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleSetUncertaintyModerate
    def handleSetUncertaintyModerate(self):
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
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleShowAllTracksBtn
    def handleShowAllTracksBtn(self):
        """ This creates an svg drawing of all tracks (
        """
#___________________________________________________________________________________________________ handleShowAllTrackwaysBtn
    def handleShowAllTrackwaysBtn(self, visible=True):
        """ This straightforwardly sets all layers either visible (default) or invisible. """
        layers = cmds.ls( type='displayLayer')
        for layer in layers:
            if layer.endswith(self.LAYER_SUFFIX):
                cmds.setAttr('%s.visibility' % layer, visible)

#___________________________________________________________________________________________________ handleShowTrackwayBtn
    def handleShowTrackwayBtn(self, visible=True):
        """ With the tracks comprising each trackway (e.g., S18) placed in their own layer, the
            visibility of each trackway is controlled by the corresponding layer visiblity. """

        # compose the name of the layer from the trackway name in the combo box
        layer = self.trackwayCmbx.currentText() + self.LAYER_SUFFIX

        # then set this layer either visible or invisible according to the kwarg
        cmds.setAttr('%s.visibility' % layer, visible)

#___________________________________________________________________________________________________ handleSvgAddSelectedBtn
    def handleSvgAddSelectedBtn(self):
        """ The current selection of tracks (if non-empty) is added to the current SVG file """
        tracks = self.getSelectedTracks()

        if tracks is None:
            return

        for track in tracks:
            x = track.x
            z = track.z

            # The track dimensions stored in the database are in fractional meters, so multiply by
            # 100 to convert to cm.
            r = 100*0.5*(track.width/2.0 + track.length/2.0)

            self.currentDrawing.circle(
                (x, z),
                r,
                scene=True,
                fill='none',
                stroke='blue',
                stroke_width=1)

            # compute the averge uncertainty in cm (also stored in fractional meters)
            u = 100*(track.widthUncertainty + track.lengthUncertainty)/2.0

            self.currentDrawing.circle(
                (x, z),
                u,
                scene=True,
                fill='red',
                stroke='red',
                stroke_width=1)

#___________________________________________________________________________________________________ handleSvgOpenBtn
    def handleSvgOpenBtn(self):
        """ A file name is specified relative to the local root. This file is then explicitly
            opened by a separate button press "Open", followed by compilation of the SVG drawing by
            incrementally adding objects (e.g., one can interactively compose a specific SVG drawing
            based on successive rounds of first selecting sceen content then pressing the
            "Add Selected" button, finally completing by pressing "Save".  When the "Open" button
            is pressed, the fresh svg file is created if there is a valid row (completed columns)
            for the track site of specified index.  Otherwise it warns and returns. """

        # get the current index again and from this, get the site map
        index = self.trackSiteIndexSbx.value()

        # check if there is a valid (completed) site map for that particular tracksite index
        siteMap = self.getSiteMap(index)
        if not siteMap:
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'Invalid Site Map',
                message=u'Tracksite index %s empty' % index,
                windowTitle=u'Tool Error')
            return

        # ok, so then make sure there is a file name specified
        fileName = self.svgFileNameLE.text()
        if not fileName:
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'Invalid SVG file name',
                message=u'Edit name and retry.',
                windowTitle=u'Tool Error')
            return

        # if there is already an open Cadence drawing, offer to close it before continuing with new
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

#___________________________________________________________________________________________________ handleSvgSaveBtn
    def handleSvgSaveBtn(self):
        """ The currently open Cadence drawing (SVG file) is written here after pressing "Save". If
            no Cadence drawing is already open, this complains and returns. """

        # complain if this button is pressed and no Cadence SVG drawing is currently open
        if not self.currentDrawing:
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'Error',
                message=u'No SVG file open.',
                windowTitle=u'Tool Error')
            return

        print 'saving svg file'

        # place the federal coordinates as a text string 20 cm above the marker
        site = self.currentDrawing.siteMap
        t    = "(%s, %s)" % (site.federalEast, site.federalNorth)
        self.currentDrawing.text(t, (0, 20), scene=True)

        # place a 2 cm green unfilled circle atop the federal coordinate marker
        self.currentDrawing.circle(
            (0, 0),
            2,
            scene=True,
            fill='none',
            stroke='green',
            stroke_width=1)
        self.currentDrawing.save()
        self.currentDrawing = None

#___________________________________________________________________________________________________ handleSvgNameLE
    def handleSvgNameLE(self):
        """ A file name is specified, which is later used in responding to the button press 'Open'
            to create an SVG file. """
        pass

#___________________________________________________________________________________________________ handleTrackSiteIndexSbx
    def handleTrackSiteIndexSbx(self):
        """ The tracksites are indexed in a table (see Tracks_SiteMap).  That index provides a
            means to select a given tracksite from the UI. """

        index   = self.trackSiteIndexSbx.value()
        siteMap = self.getSiteMap(index)

        if siteMap is None:
            self.clearTrackSiteUI()
            return

        # now populate the tracksite information in the UI
        self.refreshTrackSiteUI(siteMap)

#___________________________________________________________________________________________________ handleUnlink
    def handleUnlink(self):
        """ The 'next' attribute is cleared for the selected track. Unlinking does not
            attempt to relink tracks automatically (one must do it explicitly; see handleLink). """

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
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleUpdateLayersBtn
    def handleUpdateLayersBtn(self):
        """ The layers are initialized automatically by the initializer but if one loads additional
            trackways, this adds the corresponding layers and populates them. """
        self.initializeLayers()

#___________________________________________________________________________________________________ handleWidthSbx
    def handleWidthSbx(self):
        """ The width of the selected track is adjusted. Width is stored in the database in
            fractional meters but send to Maya in cm and displayed in integer cm units."""
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.width = self.widthSbx.value()/100.0
        t.updateNode()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ handleWidthUncertaintySbx
    def handleWidthUncertaintySbx(self):
        """ The width uncertainty of the selected track is adjusted. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) != 1:
            return

        self.getSession()
        t = selectedTracks[0]
        t.updateFromNode() # use this opportunity to capture the current state of the Maya node
        t.widthUncertainty = self.widthUncertaintySbx.value()/100.0
        t.updateNode()
        self.closeSession(commit=True)


#===================================================================================================
#                                                      D I S P L A Y   L A Y E R  U T I L I T I E S

#___________________________________________________________________________________________________ addTrackwayToLayer
    def addTrackwayToLayer(self, layer, tracks):
        """ Populates the specified display layer with the track nodes corresponding to the
            specified tracks. """
        nodes = []
        for track in tracks:
            trackNode = self.getTrackNode(track)
            if trackNode:
                nodes.append(trackNode)

        if len(nodes) == 0:
            return

        cmds.editDisplayLayerMembers(layer, nodes, noRecurse=True)

#___________________________________________________________________________________________________ createLayer
    def createLayer(self, layer, useExisting=True):
        """ Creates a layer with the specified name. """
        if useExisting and cmds.objExists(layer):
            return
        # Since nothing should be selected when creating a new display layer, save selection
        priorSelection = MayaUtils.getSelectedTransforms()
        cmds.select(clear=True)
        cmds.createDisplayLayer(name=layer)
        #  Restore the prior state of selection
        MayaUtils.setSelection(priorSelection)

#___________________________________________________________________________________________________ deleteLayer
    def deleteLayer(self, layer):
        """ Removes a display layer. """
        if not cmds.objExists(layer):
            cmds.delete(layer)

#___________________________________________________________________________________________________ initializeLayers
    def initializeLayers(self):
        """ Creates a new layer for each trackway in this site/level/sector, based on the first UID
            found (returned by getUidList).  It is important to load into the Maya scene only
            trackways from a common combination of site, level, and sector, since a given trackway
            may be redundantly defined in different sectors for a given site and level. """
        # first delete any current display layers
        layers = cmds.ls( type='displayLayer')
        for layer in layers:
            if (layer.endswith(self.LAYER_SUFFIX)):
                cmds.delete(layer)

        # get the current UID list so we can extract the site, year, sector, and level information
        uidList = self.getUidList()

        if not uidList:
            return

        # we'll use the first track as representative of the site/level/sector presumed to be
        # in common with all tracks in this scene.
        track         = self.getTrackByUid(uidList[0])
        trackwayNames = self.getTrackwayNames(track.site, track.level, track.sector)

        # then for each trackway name (such as 'S1') create a corresponding layer with the
        # LAYER_SUFFIX, then populate it with the track nodes of the tracks comprising that trackway
        for trackwayName in trackwayNames:
            layer = '%s%s' % (trackwayName, self.LAYER_SUFFIX)

            # then make the layer
            self.createLayer(layer)

            # get the list of tracks for this trackway (filtering on site, level, sector and name)
            trackway = self.getTrackway(uidList, trackwayName)
            if trackway and len(trackway) > 0:
                self.addTrackwayToLayer(layer, trackway)

        # add those trackway names to the combo box
        self.trackwayCmbx.addItems(trackwayNames)


        # and finally, refresh the trackway UI
        props = { TrackPropEnum.SITE.name:track.site,
                  TrackPropEnum.LEVEL.name:track.level,
                  TrackPropEnum.YEAR.name:track.year,
                  TrackPropEnum.SECTOR.name:track.sector }

        self.refreshTrackwayUI(props)


#===================================================================================================
#                                                                          M I S C E L L A N E O U S

#___________________________________________________________________________________________________ createCurve
    def createCurve(self, points, degree=1):
        """ Creates a named curve through the given list of points, of given degree, and added to
            the given layer. """
        return cmds.curve(point=points, degree=degree)

#___________________________________________________________________________________________________ createPathFromTrackSeries
    def createPathFromTrackSeries(self, tracks):
        """ Creates a list of the (x, z) track coordinates from a given track series.  Note that
            hidden tracks are not included, nor are tracks that are still at the origin. The
            path is specified as a list of 3D points, with the y coordinate zeroed out."""
        path = []
        for track in tracks:
            if not track.hidden and track.x != 0.0 and track.z != 0.0:
                path.append((track.x, 0.0, track.z))
        return path

#___________________________________________________________________________________________________ initializeCadenceCam
    def initializeCadenceCam(self):
        """ This creates an orthographic camera that looks down the Y axis onto the XZ plane, and
            rotated so that the AI file track labels are legible.  This camera is positioned so
            that the given track nodeName is centered in its field by setCameraFocus. """
        if cmds.objExists(self.CADENCE_CAM):
            return

        c = cmds.camera(
            orthographic=True,
            nearClipPlane=1,
            farClipPlane=100000,
            orthographicWidth=500)
        cmds.setAttr(c[0] + '.visibility', False)
        cmds.rename(c[0], self.CADENCE_CAM)
        cmds.rotate(-90, 180, 0)
        cmds.move(0, 100, 0, self.CADENCE_CAM, absolute=True)

#___________________________________________________________________________________________________ setCameraFocus
    def setCameraFocus(self):
        """ Center the current camera (CadenceCam or persp) on the currently selected node. If
            using the CadenceCam, the view is fitted to FIT_FACTOR; with the persp camera, it is
            not so contrained. """
        cmds.viewFit(fitFactor=self.FIT_FACTOR, animate=True)

#___________________________________________________________________________________________________ _activateWidgetDisplayImpl
    def _activateWidgetDisplayImpl(self, **kwargs):
        if not CadenceEnvironment.NIMBLE_IS_ACTIVE:
            self.setVisible(False)
            PyGlassBasicDialogManager.openOk(
                self,
                header=u'No Nimble Connection',
                message=u'This tool requires an active Nimble server connection running in Maya',
                windowTitle=u'Tool Error')
            return

        # in case there was an earlier failure, set this visible
        self.setVisible(True)

        # now that Nimble is active, get Maya ready for Cadence, starting with the CadenceCam
        priorSelection = MayaUtils.getSelectedTransforms()
        self.initializeCadenceCam()

        # then have the Trackway Manager's UI display data for the current Maya selection (if any)
        MayaUtils.setSelection(priorSelection)

        # update the track UI and trackway UI based on what might be selected already
        self.handlePullBtn()

        # display summary counts of loaded, completed, and selected tracks
        self.refreshTrackCountsUI()

#___________________________________________________________________________________________________ _deactivateWidgetDisplayImpl
    def _deactivateWidgetDisplayImpl(self, **kwargs):
        """ When the widget is closed commit any unfinished database changes. """
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ getSession
    def getSession(self):
        """ Access to model instances is based on the current model and session, stored in two
            local instance variables so that multiple operations can be performed before closing this
            given session. """
        if self._session is not None:
            return self._session

        self._session = Tracks_Track.MASTER.createSession()
        return self._session

#___________________________________________________________________________________________________ closeSession
    def closeSession(self, commit =True):
        """ Closes a session and indicates such by nulling out model and session. """
        if self._session is not None:
            if commit:
                self._session.commit()
            self._session.close()
            return True

        self._session = None
        return False
