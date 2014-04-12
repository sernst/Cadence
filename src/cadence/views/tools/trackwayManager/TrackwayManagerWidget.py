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

        self.refreshBtn.clicked.connect(self.refreshUI)

        # in Edit Track tab:
        self.selectPriorBtn.clicked.connect(self.selectPrecursorTracks)
        self.selectLaterBtn.clicked.connect(self.selectSuccessorTracks)
        self.selectSeriesBtn.clicked.connect(self.selectTrackSeries)
        self.linkBtn.clicked.connect(self.linkSelectedTracks)
        self.unlinkBtn.clicked.connect(self.unlinkSelectedTracks)
        self.renameBtn.clicked.connect(self.renameSelected)
        self.setSelectedBtn.clicked.connect(self.setSelected)
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
        self.setSelectedTrackwayBtn.clicked.connect(self.setSelectedTrackway)

        self._model   = None
        self._session = None
        self.createSession()

#===================================================================================================
#                                                                                     P U B L I C
#

#___________________________________________________________________________________________________ createSession
    def createSession(self):
        """ Access to model instances is based on the current model and session, stored in two
         local instance variables so that multiple operations can be performed before closing this
         given session."""
        if self._session is not None:
            self._model   = Tracks_Track.MASTER
            self._session = self._model.createSession()

#___________________________________________________________________________________________________ closeSession
    def closeSession(self):
        """ Closing a session and indicating such by nulling out model and session. """
        if self._session is not None:
            self._session.close()

        self._model   = None
        self._session = None

#__________________________________________________________________________________________________ getSelectedTracks
    def getSelectedTracks(self):
        """ This runs a remote script to get a list of the track UID from the selected Maya track
         nodes. The track model instances associated with those UIDs are then assembled into a
         list and returned. """
        conn = nimble.getConnection()
        result = conn.runPythonModule(GetSelectedUidList)
        tracks = list()
        for uid in result.selectedUidList:
            tracks.append(Tracks_Track.getByUid(uid, self._session))
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
        """ Returns the track model of the first track in a series. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        prev = selectedTracks[0].getPreviousTrack(self._session)
        while prev is not None:
            p = prev.getPreviousTrack(self._session)
            if p is None:
                return prev
            prev = p
        return None

#___________________________________________________________________________________________________ getLastTrack
    def getLastTrack(self):
        """ Returns the track model of the last track in a series. """
        selectedTracks = self.getSelectedTracks()
        # if not selectedTracks:
        #     return None
        # t = selectedTracks[-1]
        # n = t.getNextTrack(self._session)
        # while n is not None:
        #     n = n.getNextTrack(self._session)
        # return n

#___________________________________________________________________________________________________ getFirstSelectedTrack
    def getFirstSelectedTrack(self):
        """ Returns the track model of the first track in a series of selected tracks. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        # s = selectedTracks[0]
        # while s.getPreviousTrack(self._session) in selectedTracks:
        #     s = s.getPreviousTrack(self._session)
        # return s

#___________________________________________________________________________________________________ getLastSelectedTrack
    def getLastSelectedTrack(self):
        """ Returns the track model of the last track in a series of selected tracks. """
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        # s = selectedTracks[-1]
        # while s.getNextTrack(self._session) in selectedTracks:
        #     s = s.getNextTrack(self._session)
        # return s

 #__________________________________________________________________________________________________ getTrackSeries
    def getTrackSeries(self):
        """ Steps back to the first track then lists all track models in a given series. """
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
        self.refreshUI()

#___________________________________________________________________________________________________ gotoPrevTrack
    def goToPrevTrack(self):
        t = self.getFirstSelectedTrack()
        if t is None:
            return
        p = t.prevTrack
        self.selectTrack(p if p else t)
        self.refreshUI()

#___________________________________________________________________________________________________ goToNextTrack
    def goToNextTrack(self):
        t = self.getLastSelectedTrack()
        if t is None:
            return
        n = t.nextTrack
        self.selectTrack(n if n else t)
        self.refreshUI()

#___________________________________________________________________________________________________ goToLastTrack
    def goToLastTrack(self):
        t = self.getLastTrack()
        if t is None:
            return
        self.selectTrack(t)
        self.refreshUI()

#___________________________________________________________________________________________________ linkSelectedTracks
    def linkSelectedTracks(self):
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return
        i = 0
        while i < len(selectedTracks) - 1:
            selectedTracks[i].next = selectedTracks[i + 1]
            i += 1
        cmds.select(selectedTracks[-1].nodeName) # the last selected Maya nodeName is selected
        self.refreshUI()

#___________________________________________________________________________________________________ unlinkSelectedTracks
    def unlinkSelectedTracks(self):
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
            return

        s1 = self.getFirstSelectedTrack()
        s2 = self.getLastSelectedTrack()
        p = s1.getPreviousTrack()
        n = s2.getNextTrack()

        if p and n:              # if track(s) to be unlinked are within
            p.next = n            # connect previous to next, bypassing the selected track(s)
            cmds.select(p.nodeName)  # select the track just prior to the removed track(s)
        elif n and not p:        # selection includes the first track
            cmds.select(n.nodeName)  # and select the track just after the selection
        elif p and not n:        # selection includes the last track
            s2.next = ''
            cmds.select(p.nodeName)  # and bump selection back to the previous track
        for s in selectedTracks:
            s.next = ''
        self.refreshUI()

#___________________________________________________________________________________________________ getNamefromUI
    def getNameFromUI(self):
        return self.rightLeftLE.text() + self.manusPesLE.text() + self.numberLE.text()

#___________________________________________________________________________________________________ getTrackwayPropertiesFromUI
    def getTrackwayPropertiesFromUI(self):
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

#___________________________________________________________________________________________________ getTrackPropertiesFromUI
    def getTrackPropertiesFromUI(self):
        """ Get UI values (except for WIDTH, LENGTH, ROTATION, X and Z """
        d = self.getTrackwayPropertiesFromUI() # first get the trackway properties
        # then add to the dictionary the specifics of a given track
        d[TrackPropEnum.NAME.name]  = self.getNameFromUI()
        d[TrackPropEnum.INDEX.name] = self.indexLE.text()
        d[TrackPropEnum.UID.name]    = self.idLE.text()
        d[TrackPropEnum.NOTE.name]  = self.noteTE.toPlainText()

        d[TrackPropEnum.WIDTH_UNCERTAINTY.name]    = self.floatLE(self.widthUncertaintyLE.text())
        d[TrackPropEnum.WIDTH_MEASURED.name]       = self.floatLE(self.widthMeasuredLE.text())
        d[TrackPropEnum.LENGTH_UNCERTAINTY.name]   = self.floatLE(self.lengthUncertaintyLE.text())
        d[TrackPropEnum.LENGTH_MEASURED.name]      = self.floatLE(self.lengthMeasuredLE.text())
        d[TrackPropEnum.ROTATION_UNCERTAINTY.name] = self.floatLE(self.rotationUncertaintyLE.text())
        d[TrackPropEnum.DEPTH_MEASURED.name]       = self.floatLE(self.depthMeasuredLE.text())
        d[TrackPropEnum.DEPTH_UNCERTAINTY.name]    = self.floatLE(self.depthUncertaintyLE.text())

        return d

#___________________________________________________________________________________________________ setSelected
    def setSelected(self):
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
        self.refreshUI()

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

#___________________________________________________________________________________________________ refreshUI
    def refreshUI(self):
        """ Updates the UI to reflect the attributes of the selected track or tracks in Maya.  Note
        that if more than one track is selected, only the trackway attributes are updated; the
        individual track attributes are cleared to empty strings. Note that if multiple tracks are
        selected, they could be from multiple independent trackways, but the trackway parameters are
        based on those of ht efirst selected track. """
        selectedTracks = self.getSelectedTracks()
        self.clearUI()

        if selectedTracks is None:
            return

        t = selectedTracks[0]
        if len(selectedTracks) == 1:
            self.leftLE.setText(u'L'if t.left else u'R')
            self.pesLE.setText(u'P'if t.pes else u'M')
            self.numberLE.setText(unicode(t.number))

            v = t.width
            self.widthLE.setText(u'' if v is None else '%.2f' % v)

            v = t.widthMeasured
            self.widthMeasuredLE.setText(u'' if v is None else '%.2f' % v)

            v = t.widthUncertainty
            self.widthUncertaintyLE.setText(u'' if v is None else '%.1f' % v)

            v = t.length
            self.lengthLE.setText(u'' if v is None else '%.2f' % v)

            v = t.lengthMeasured
            self.lengthMeasuredLE.setText(u'' if v is None else '%.2f' % v)

            v = t.lengthUncertainty
            self.lengthUncertaintyLE.setText(u'' if v is None else '%.1f' % v)

            v = t.rotation
            self.rotationLE.setText(u'' if v is None else '%.2f' % v)

            v = t.rotationUncertainty
            self.rotationUncertaintyLE.setText(u'' if v is None else '%.1f' % v)

            v = t.depthMeasured
            self.depthMeasuredLE.setText(u'' if v is None else '%.2f' % v)

            v = t.depthUncertainty
            self.depthUncertaintyLE.setText(u'' if v is None else '%.1f' % v)

            v = t.index
            self.indexLE.setText(u'' if v is None else v)

            v = t.id
            self.idLE.setText(u'' if v is None else v)

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
        t = t.getNextTrack(self._session)
        while t:
            successorNodes.append(t.nodeName)
            t = t.getNextTrack(self._session)
        cmds.select(successorNodes)

#___________________________________________________________________________________________________ selectPrecursorTracks
    def selectPrecursorTracks(self):
         """ Selects in Maya all nodes in the given track series up to but not including the first
          selected track. """
         t = self.getFirstSelectedTrack()
         if t is None:
             return

         precursorNodes = list()
         t = t.getPrevTrack(self._session)
         while t:
            precursorNodes.append(t.nodeName)
            t = t.prevTrack(self._session)
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

#___________________________________________________________________________________________________ setSelectedTrackway
    def setSelectedTrackway(self):
        print 'setSelectedTrackway: clicked!'

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _activateWidgetDisplayImpl
    def _activateWidgetDisplayImpl(self, **kwargs):
        if CadenceEnvironment.NIMBLE_IS_ACTIVE:
            self.refreshUI()
            return

        self.setVisible(False)
        PyGlassBasicDialogManager.openOk(
            self,
            header=u'No Nimble Connection',
            message=u'This tool requires an active Nimble server connection running in Maya',
            windowTitle=u'Tool Error')

#___________________________________________________________________________________________________ _getTrackSetNode
    def _getTrackSetNode(cls):
        """ This is redundunt with the version in TrackSceneUtils, but running locally. Note that
        if no TrackSetNode is found, it does not create one. """
        for node in cmds.ls(exactType='objectSet'):
            if node == CadenceEnvironment.TRACKWAY_SET_NODE_NAME:
                return node
        return None
