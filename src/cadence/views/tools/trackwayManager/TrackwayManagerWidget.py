# TrackwayManagerWidget.py
# (C)2012-2014
# Scott Ernst and Kent A. Stevens

import nimble

from nimble import cmds

from pyaid.json.JSON import JSON

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
     their attributes.  Tracks in Maya are represented by track nodes, each a transform nodeName with
     an additional attribute specifying the UID of that track.  The transform's scale, position, and
     rotation (about Y) are used to intrinsically represent track dimensions, position, and
     orientation.  Track models are accessed by query based on the UID, and for a given session. """
#===================================================================================================
#                                                                                       C L A S S
    RESOURCE_FOLDER_PREFIX = ['tools']

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)

        # in Edit Track tab:
        self.getBtn.clicked.connect(self.getFromMaya)
        self.setBtn.clicked.connect(self.setSelectedTrack)
        self.linkBtn.clicked.connect(self.linkSelectedTracks)
        self.unlinkBtn.clicked.connect(self.unlinkSelectedTracks)

        self.selectPriorBtn.clicked.connect(self.selectPrecursorTracks)
        self.selectLaterBtn.clicked.connect(self.selectSuccessorTracks)
        self.selectSeriesBtn.clicked.connect(self.selectTrackSeries)

        self.firstBtn.clicked.connect(self.goToFirstTrack)
        self.prevBtn.clicked.connect(self.goToPrevTrack)
        self.nextBtn.clicked.connect(self.goToNextTrack)
        self.lastBtn.clicked.connect(self.goToLastTrack)
        self.findBtn.clicked.connect(self.findTrack)

        # in Edit Trackway tab:
        self.showTrackwayBtn.clicked.connect(self.showTrackway)
        self.hideTrackwayBtn.clicked.connect(self.hideTrackway)
        self.selectTrackwayBtn.clicked.connect(self.selectTrackway)

        self.showAllTrackwaysBtn.clicked.connect(self.showAllTrackways)
        self.hideAllTrackwaysBtn.clicked.connect(self.hideAllTrackways)
        self.selectAllTrackwaysBtn.clicked.connect(self.selectAllTrackways)

        self._session = None

#===================================================================================================
#                                                                                     P U B L I C
#

#___________________________________________________________________________________________________ getSession
    def getSession(self):
        """ Access to model instances is based on the current model and session, stored in two
         local instance variables so that multiple operations can be performed before closing this
         given session."""
        if self._session is not None:
            return self._session

        self._session = Tracks_Track.MASTER.getSession()
        return self._session

#___________________________________________________________________________________________________ closeSession
    def closeSession(self, commit =True):
        """ Closing a session and indicating such by nulling out model and session. """
        if self._session is not None:
            if commit:
                self._session.commit()
            self._session.close()
            return True

        self._session = None
        return False

#__________________________________________________________________________________________________ getSelectedTracks
    def getSelectedTracks(self):
        """ This runs a remote script to get a list of the track UID from the selected Maya track
         nodes. The track model instances associated with those UIDs are then assembled into a
         list and returned. """
        conn = nimble.getConnection()
        result = conn.runPythonModule(GetSelectedUidList)
        tracks = list()
        for uid in result.selectedUidList:
            tracks.append(Tracks_Track.getByUid(uid, self.getSession()))
        return tracks

#___________________________________________________________________________________________________ getAllTracks
    def getAllTracks(self):
        """ This returns a list of all track nodes (or None). """
        trackSetNode = self._getTrackSetNode()
        trackNodes = list()
        if not trackSetNode:
            return trackNodes
        trackNodes = cmds.sets(trackSetNode, query=True)
        return trackNodes if len(trackNodes) > 0 else None

#___________________________________________________________________________________________________ getFirstTrack
    def getFirstTrack(self):
        """ Returns the track model corresponding to the first track in a series. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        t = selectedTracks[0]
        p = t.getPreviousTrack(self.getSession())
        while p is not None:
            t = p
            p = p.getPreviousTrack(self.getSession())
        return t

#___________________________________________________________________________________________________ getLastTrack
    def getLastTrack(self):
        """ Returns the track model corresponding to the last track in a series. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        t = selectedTracks[-1]
        n = t.getNextTrack(self.getSession())
        while n is not None:
            t = n
            n = n.getNextTrack(self.getSession())
        return n

#___________________________________________________________________________________________________ getFirstSelectedTrack
    def getFirstSelectedTrack(self):
        """ Returns the track model corresponding to the first of a series of selected tracks. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        s = selectedTracks[0]
        p = s.getPreviousTrack(self.getSession())
        while p in selectedTracks:
            s = p
            p = s.getPreviousTrack(self.getSession())
        return s

#___________________________________________________________________________________________________ getLastSelectedTrack
    def getLastSelectedTrack(self):
        """ Returns the track model corresponding to the last of a series of selected tracks. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None

        s = selectedTracks[-1]
        n = s.getNextTrack(self.getSession())
        while n in selectedTracks:
            s = n
            n = s.getNextTrack(self.getSession())
        return s

 #__________________________________________________________________________________________________ getTrackSeries
    def getTrackSeries(self):
        """ Steps back from any selected track to the first track, then creates a list of all
         track models in a given series. """
        series = list()
        t = self.getFirstTrack()
        while t:
            series.append(t)
            t = t.getNextTrack()
        return series

#___________________________________________________________________________________________________ selectTrack
    def selectTrack(self, track):
       track.setCadenceCamFocus()
       cmds.select(track.nodeName)

# __________________________________________________________________________________________________ goToFirstTrack
    def goToFirstTrack(self):
        t = self.getFirstTrack()
        if t is None:
            return
        self.selectTrack(t)
        self.importFromMaya()

#___________________________________________________________________________________________________ gotoPrevTrack
    def goToPrevTrack(self):
        """ Select the previous track node in this track series. """
        t = self.getFirstSelectedTrack()
        if t is None:
            return
        p = t.prevTrack
        self.selectTrack(p if p else t)
        self.importFromMaya()

#___________________________________________________________________________________________________ goToNextTrack
    def goToNextTrack(self):
        """ Select the next track node in this track series. """
        t = self.getLastSelectedTrack()
        if t is None:
            return
        n = t.nextTrack
        self.selectTrack(n if n else t)
        self.importFromMaya()

#___________________________________________________________________________________________________ goToLastTrack
    def goToLastTrack(self):
        """ Select the last track node in this track series. """
        t = self.getLastTrack()
        if t is None:
            return
        self.selectTrack(t)
        self.importFromMaya()

#___________________________________________________________________________________________________ linkSelectedTracks
    def linkSelectedTracks(self):
        """ To link two or more tracks, first select them in Maya in the intended order and their
        models will be linked accordingly.  Note that, by convention, the last track node is
        selected state. Note that we may want to handle the case where a given track is regarded as
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

#___________________________________________________________________________________________________ unlinkSelectedTracks
    def unlinkSelectedTracks(self):
        """ The next attribute is simply cleared for one or more selected tracks. Unlinking does
        not attempt to relink tracks automatically (One must do explicit linking instead). """
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        for t in selectedTracks:
            t.next = u''

        self.importFromMaya()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ getNamefromUI
    def getNameFromUI(self):
        """ Composes a string such as 'LM3' or 'RP4'. """
        return self.rightLeftLE.text() + self.manusPesLE.text() + self.numberLE.text()

#___________________________________________________________________________________________________ getTrackwayPropertiesFromUI
    def getTrackwayPropertiesFromUI(self):
        """ This creates a dictionary of trackway properties, derived from the UI. """
        dictionary = dict()

        dictionary[TrackPropEnum.COMM.name]            = self.communityLE.text()
        dictionary[TrackPropEnum.SITE.name]            = self.siteLE.text()
        dictionary[TrackPropEnum.YEAR.name]            = self.yearLE.text()
        dictionary[TrackPropEnum.SECTOR.name]          = self.sectorLE.text()
        dictionary[TrackPropEnum.LEVEL.name]           = self.levelLE.text()
        dictionary[TrackPropEnum.TRACKWAY_TYPE.name]   = self.trackwayTypeLE.text()
        dictionary[TrackPropEnum.TRACKWAY_NUMBER.name] = self.trackwayNumberLE.text()
        return dictionary

#___________________________________________________________________________________________________ floatLE
    def floatLE(self, string, default =0.0):
        return default if string == '' else float(string)

#___________________________________________________________________________________________________ setSelectedTrack
    def setSelectedTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            selectedTracks[0].setProperties(self.getTrackPropertiesFromUI())
        else:
            dictionary = self.getTrackwayPropertiesFromUI()
            dictionary[TrackPropEnum.NOTE.name] = self.noteTE.toPlainText()
            for t in selectedTracks:
                t.setProperties(dictionary)

        self.importFromMaya()
        self.closeSession(commit=True)

#___________________________________________________________________________________________________ clearUI
    def clearUI(self):
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

        self.widthLE.setText('')
        self.widthUncertaintyLE.setText('')
        self.widthMeasuredLE.setText('')

        self.lengthLE.setText('')
        self.lengthUncertaintyLE.setText('')
        self.lengthMeasuredLE.setText('')

        self.rotationLE.setText('')
        self.rotationUncertaintyLE.setText('')

        self.depthMeasuredLE.setText('')
        self.depthUncertaintyLE.setText('')

        self.indexLE.setText('')
        self.idLE.setText('')
        self.noteTE.setPlainText('')

        self.xLE.setText('')
        self.zLE.setText('')

        self.prevTrackLbl.setText(u'')
        self.nextTrackLbl.setText(u'')

#___________________________________________________________________________________________________ importFromMaya
    def importFromMaya(self):
        """ Updates the UI to reflect the attributes of the selected track or tracks in Maya.  Note
        that if more than one track is selected, only the trackway attributes are updated; the
        individual track attributes are cleared to empty strings. Note that if multiple tracks are
        selected, they could be from multiple independent trackways, but the trackway parameters are
        based on those of the first selected track. """
        selectedTracks = self.getSelectedTracks()


        if selectedTracks is None:
            return

#___________________________________________________________________________________________________
        self.clearUI()
        t = selectedTracks[0]
        if len(selectedTracks) == 1:
            t.updateFromNode()


            self.leftLE.setText(u'L'if t.left else u'R')
            self.pesLE.setText(u'P'if t.pes else u'M')
            self.numberLE.setText(unicode(t.number))

            v = t.width
            self.widthLE.setText(u'' if v is None else '%.2f' % v)

            v = t.length
            self.lengthLE.setText(u'' if v is None else '%.2f' % v)

            v = t.lengthUncertainty
            self.lengthUncertaintyLE.setText(u'' if v is None else '%.1f' % v)

            v = t.rotation
            self.rotationLE.setText(u'' if v is None else '%.2f' % v)

            v = t.rotationUncertainty
            self.rotationUncertaintyLE.setText(u'' if v is None else '%.1f' % v)



            v = t.note
            self.noteTE.setPlainText(u'' if v is None else v)

            v = t.x
            self.xLE.setText(u'' if v is None else '%.2f' % v)

            v = t.z
            self.zLE.setText(u'' if v is None else '%.2f' % v)

            v = self.getFirstTrack()
            self.firstTrackLbl.setText(unicode('') if v is None else unicode(v.name))

            v = t.prevTrack
            self.prevTrackLbl.setText(u'' if v is None else unicode(v.name))

            v = t.nextTrack
            self.nextTrackLbl.setText(u'' if v is None else unicode(v.name))

            v = self.getLastTrack()
            self.lastTrackLbl.setText(u'' if v is None else unicode(v.name))

        v = t.comm
        self.communityLE.setText(u'' if v is None else v)

        v = t.site
        self.siteLE.setText(u'' if v is None else v)

        v = t.year
        self.yearLE.setText(u'' if v is None else v)

        v = t.sector
        self.sectorLE.setText(u'' if v is None else v)

        v = t.level
        self.levelLE.setText(u'' if v is None else v)

        v = t.trackwayType
        self.trackwayTypeLE.setText(u'' if v is None else v)

        v = t.trackwayNumber
        self.trackwayNumberLE.setText(u'' if v is None else v)
        if v is not None:
            self.addTrackwayToCB(v)

#___________________________________________________________________________________________________ selectSuccessorTracks
    def selectSuccessorTracks(self):
        """ Selects in Maya all nodes in the given track series after the last selected track. """
        t = self.getLastSelectedTrack()
        if t is None:
            return

        successorNodes = list()
        t = t.getNextTrack(self.getSession())
        while t:
            successorNodes.append(t.nodeName)
            t = t.getNextTrack(self.getSession())
        cmds.select(successorNodes)

#___________________________________________________________________________________________________ selectPrecursorTracks
    def selectPrecursorTracks(self):
         """ Selects in Maya all nodes in the given track series up to but not including the first
          selected track. """
         t = self.getFirstSelectedTrack()
         if t is None:
             return

         precursorNodes = list()
         t = t.getPrevTrack(self.getSession())
         while t:
            precursorNodes.append(t.nodeName)
            t = t.prevTrack(self.getSession())
         cmds.select(precursorNodes)

#___________________________________________________________________________________________________ selectTrackSeries
    def selectTrackSeries(self):
        """ Select in Maya the nodes for the entire track series based on the given selection. """
        tracks = self.getTrackSeries()
        if tracks is None:
            return

        print "Selected series consists of %s tracks" % len(tracks)
        nodes = list()
        for t in tracks:
            nodes.append(t.nodeName)
        cmds.select(nodes)

#___________________________________________________________________________________________________ selectAllTracks
    def selectAllTracks(self):
        """ Select in Maya the nodes for all the tracks in the scene. """
        tracks = self.getAllTracks()
        if len(tracks) == 0:
            return

        nodes = list()
        for t in tracks:
            nodes.append(t.nodeName)
        cmds.select(nodes)

#___________________________________________________________________________________________________ exportSelected
    def exportSelected(self):
        tracks = self.getSelectedTracks()

        if tracks is None:
            return

        l = list()
        for t in tracks:
            l.append(t.getProperties())

        JSON.toFile('../../sandbox/test.json', l)

        return tracks

#___________________________________________________________________________________________________ addTrackwayToCB
    def addTrackwayToCB(self, trackwayNumber):
        trackway = "S" + trackwayNumber.zfill(2)
        i = self.trackwayCB.findText(trackway)

        if i != -1:
            return

        trackways = [self.trackwayCB.itemText(i) for i in range(self.trackwayCB.count())]
        trackways.append(trackway)
        trackways.sort()

        self.trackwayCB.clear()
        self.trackwayCB.addItems(trackways)
        i = self.trackwayCB.findText(trackway)
        self.trackwayCB.setCurrentIndex(i)

#___________________________________________________________________________________________________ showTrackway
    def showTrackway(self, visible=True):
        trackway = self.trackwayCB.currentText()
        print('trackway = %s' % trackway)
        if trackway == '':
            return
        layer = trackway + '_Layer'
        if cmds.objExists(layer):
            cmds.setAttr('%s.visibility' % layer, visible)

#___________________________________________________________________________________________________ hideTrackway
    def hideTrackway(self):
        self.showTrackway(False)

#___________________________________________________________________________________________________ findTrack
    def findTrack(self):
        targetName = self.getNameFromUI()
        targetTrackway = self.trackwayLE.text()
        for node in cmds.ls('track*', exactType='transform'):
            if self.isTrackNode(node):
                name = cmds.getAttr('%s.name' % node)
                trackway = cmds.getAttr('%s.trackway' % node)
                if name == targetName and trackway == targetTrackway:
                    t = None # Track(nodeName)
                    self.selectTrack(t)
                    return

#___________________________________________________________________________________________________ selectTrackway
    def selectTrackway(self, trackway=None):
        if not trackway:
            trackway = self.trackwayCB.currentText()
            print('trackway = %s' % trackway)
        if trackway == '':
            return
        targetType   = trackway[0]
        targetNumber = trackway[1:]
        tracks = self.getAllTracks()
        nodes = list()
        for t in tracks:
            if t.trackwayType == targetType and t.trackwayNumber == targetNumber:
                nodes.append(t.nodeName)
        print "and now nodes has %s instances" % len(nodes)
        cmds.select(nodes, add=True)

#___________________________________________________________________________________________________ showAllTrackways
    def showAllTrackways(self, visible=True):
        for i in range(100):
            layer = 'S' + str(i).zfill(2) + '_Layer'
            if cmds.objExists(layer):
                cmds.setAttr('%s.visibility' % layer, visible)

#___________________________________________________________________________________________________ hideAllTrackways
    def hideAllTrackways(self):
        self.showAllTrackways(False)

#___________________________________________________________________________________________________ selectAllTrackways
    def selectAllTrackways(self):
        for i in range(100):
            trackway = 'S' + str(i).zfill(2)
            self.selectTrackway(trackway)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _activateWidgetDisplayImpl
    def _activateWidgetDisplayImpl(self, **kwargs):
        if CadenceEnvironment.NIMBLE_IS_ACTIVE:
            self.importFromMaya()
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
