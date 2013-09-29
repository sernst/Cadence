# TrackwayManagerWidget.py
# (C)2012-2013
# Scott Ernst and Kent A. Stevens

from nimble import cmds

from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.enum.TrackwayPropEnum import TrackwayPropEnum
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.mayan.trackway.Track import Track

#___________________________________________________________________________________________________ TrackwayManagerWidget
class TrackwayManagerWidget(PyGlassWidget):

#===================================================================================================
#                                                                                                    C L A S S
    RESOURCE_FOLDER_PREFIX = ['tools']

    _BLANK = ''

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)

        # path = self.getResourcePath('..', '..', 'help.markdown', isFile=True)
        # gives you the TrackwayManager folder
        # print "in the TrackwayManagerWidget, the path =%s" % path
        # get a qIcon or something or QButton icon and put the icons in the TrackwayManager Widget
        # folder and commit them to the project also. Look for them in the changes at the bottom
        # of PyCharm window

        # this returns the path to the shared directory resources/apps/CadenceApplication
        # to get self.getAppResourcePath()

        self.selectPriorBtn.clicked.connect(self.selectPrecursorTracks)
        self.selectLaterBtn.clicked.connect(self.selectSuccessorTracks)
        self.selectSeriesBtn.clicked.connect(self.selectTrackSeries)

        self.linkBtn.clicked.connect(self.linkSelectedTracks)
        self.unlinkBtn.clicked.connect(self.unlinkSelectedTracks)
        self.deleteBtn.clicked.connect(self.deleteSelectedTracks)

        self.firstBtn.clicked.connect(self.goToFirstTrack)
        self.prevBtn.clicked.connect(self.goToPrevTrack)
        self.nextBtn.clicked.connect(self.goToNextTrack)
        self.lastBtn.clicked.connect(self.goToLastTrack)

        self.refreshBtn.clicked.connect(self.refreshUI)
        self.setSelectedBtn.clicked.connect(self.setSelectedTracks)
        self.addBtn.clicked.connect(self.addTrack)

        self.renameBtn.clicked.connect(self.renameSelectedTracks)
        self.selectAllTracksBtn.clicked.connect(self.selectAllTracks)
        self.exportSelectedBtn.clicked.connect(self.exportSelectedTracks)

        self.testBtn.clicked.connect(self.test)
        self.initBtn.clicked.connect(self.initializeTrackway)

        self.adjustSize()
        self.refreshUI()

#===================================================================================================
#                                                                                                     P U B L I C
#

#___________________________________________________________________________________________________ isTrackNode
    def isTrackNode(self, n):
        return cmds.attributeQuery(TrackPropEnum.NAME.name, node=n, exists=True)

#___________________________________________________________________________________________________
    def getAllTracks(self):
        nodes = cmds.ls(transforms=True, exactType='transform')

        if nodes is None:
            return None
        tracks = list()
        for n in nodes:
            if self.isTrackNode(n):
                tracks.append(Track(n))
        return tracks

#___________________________________________________________________________________________________ getSelectedTracks
    def getSelectedTracks(self):
        selectedNodes = cmds.ls(selection=True, exactType='transform')

        if selectedNodes is None:
            return None
        tracks = list()
        for n in selectedNodes:
            if self.isTrackNode(n):
                tracks.append(Track(n))
        return tracks

#___________________________________________________________________________________________________ getFirstTrack
    def getFirstTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        t = selectedTracks[0]
        while t.getPrevTrack():
            t = t.getPrevTrack()
        return t

#___________________________________________________________________________________________________ getLastTrack
    def getLastTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        t = selectedTracks[-1]
        while t.getNextTrack():
            t = t.getNextTrack()
        return t

#___________________________________________________________________________________________________ getFirstSelectedTrack
    def getFirstSelectedTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        s = selectedTracks[0]
        while s.getPrevTrack() in selectedTracks:
            s = s.getPrevTrack()
        return s

#___________________________________________________________________________________________________ getLastSelectedTrack
    def getLastSelectedTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        s = selectedTracks[-1]
        while s.getNextTrack() in selectedTracks:
            s = s.getNextTrack(s)
        return s

 #__________________________________________________________________________________________________ getTrackSeries
    def getTrackSeries(self):
        series = list()
        t = self.getFirstTrack()
        while t:
            series.append(t)
            t = t.getNextTrack()
        return series

#___________________________________________________________________________________________________ selectTrack
    def selectTrack(self, track):
       track.setCadenceCamFocus()
       cmds.select(track.node)

# __________________________________________________________________________________________________ goToFirstTrack
    def goToFirstTrack(self):
        t = self.getFirstTrack()
        if t is None:
            return
        self.selectTrack(t)
        self.refreshUI()

#___________________________________________________________________________________________________ gotoPrevTrack
    def goToPrevTrack(self):
        p = None
        t = self.getFirstSelectedTrack()
        if t is None:
            return
        p = t.getPrevTrack()
        if p:
            self.selectTrack(p)
        else:
            self.selectTrack(t)
        self.refreshUI()

#___________________________________________________________________________________________________ goToNextTrack
    def goToNextTrack(self):
        n = None
        t = self.getLastSelectedTrack()
        if t is None:
            return
        n = t.getNextTrack()
        if n:
            self.selectTrack(n)
        else:
            self.selectTrack(t)
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
        selected = self.getSelectedTracks()
        if selected is None:
            return
        i = 0
        while i < len(selected) - 1:
            selected[i+1].link(selected[i])
            i += 1
        cmds.select(selected[-1].node)
        self.refreshUI()

#___________________________________________________________________________________________________ unlinkSelectedTracks
    def unlinkSelectedTracks(self):
        selected = self.getSelectedTracks()
        if selected is None:
            return

        s1 = self.getFirstSelectedTrack()
        s2 = self.getLastSelectedTrack()
        p = s1.getPrevTrack()
        n = s2.getNextTrack()

        if p and n:              # if track(s) to be unlinked are within
            s1.unlink()          # disconnect previous track from first selected track
            n.link(p)            # connect previous to next, bypassing the selected track(s)
            cmds.select(p.node)  # select the track just prior to the removed track(s)
        elif n and not p:        # selection includes the first track
            n.unlink()
            cmds.select(n.node)  # and select the track just after the selection
        elif p and not n:        # selection includes the last track
            s2.unlink()
            cmds.select(p.node)  # and bump selection back to the previous track
        for s in selected[0:-1]:
            s.unlink()
        self.refreshUI()

#___________________________________________________________________________________________________ _initializeTrackway
    def initializeTrackway(self):
        trackwayProperties = self.getTrackwayPropertiesFromUI()
        trackProperties    = self.getTrackPropertiesFromUI()

        lp1 = Track(Track.createNode())
        lp1.setTrackwayProperties(trackwayProperties)
        lp1.setName('LP1')
        lp1.setPosition(200.0, 100.0)
        lp1.setDimensions(0.4, 0.6)

        rp1 = Track(Track.createNode())
        rp1.setTrackwayProperties(trackwayProperties)
        rp1.setName('RP1')
        rp1.setPosition(100.0, 100.0)
        rp1.setDimensions(0.4, 0.6)

        lm1 = Track(Track.createNode())
        lm1.setTrackwayProperties(trackwayProperties)
        lm1.setName('LM1')
        lm1.setPosition(200.0, 200.0)
        lm1.setDimensions(0.25, 0.2)

        rm1 = Track(Track.createNode())
        rm1.setTrackwayProperties(trackwayProperties)
        rm1.setName('RM1')
        rm1.setPosition(100.0, 200.0)
        rm1.setDimensions(0.25, 0.2)

        lp2 = Track(Track.createNode())
        lp2.setTrackwayProperties(trackwayProperties)
        lp2.setName('LP2')
        lp2.setPosition(200.0, 400.0)
        lp2.setDimensions(0.4, 0.6)

        rp2 = Track(Track.createNode())
        rp2.setTrackwayProperties(trackwayProperties)
        rp2.setName('RP2')
        rp2.setPosition(100.0, 400.0)
        rp2.setDimensions(0.4, 0.6)

        lm2 = Track(Track.createNode())
        lm2.setTrackwayProperties(trackwayProperties)
        lm2.setName('LM2')
        lm2.setPosition(200.0, 500.0)
        lm2.setDimensions(0.25, 0.2)

        rm2 = Track(Track.createNode())
        rm2.setTrackwayProperties(trackwayProperties)
        rm2.setName('RM2')
        rm2.setPosition(100.0, 500.0)
        rm2.setDimensions(0.25, 0.2)

        lp2.link(lp1)
        rp2.link(rp1)
        lm2.link(lm1)
        rm2.link(rm1)

        cmds.select([lp1.node, rp1.node, lm1.node, rm1.node,
                     lp2.node, rp2.node, lm2.node, rm2.node])

#___________________________________________________________________________________________________ addTrack
    def addTrack(self):
        lastTrack = self.getLastTrack()
        if lastTrack is None:
            return
        prevTrack = lastTrack.getPrevTrack()
        nextTrack = Track(cmds.duplicate(lastTrack.node)[0])
        nextName  = Track.incrementName(lastTrack.getName())
        nextTrack.setName(nextName)
        dx = lastTrack.getX() - prevTrack.getX()
        dz = lastTrack.getZ() - prevTrack.getZ()
        nextTrack.moveRelative(dx, 0, dz)
        nextTrack.link(lastTrack)
        self.refreshUI()

#___________________________________________________________________________________________________ composeNamefromUI
    def getNameFromUI(self):
        return self.rightLeftLEdit.text() + self.manusPesLEdit.text() + self.numberLEdit.text()

#___________________________________________________________________________________________________ getTrackwayPropertiesFromUI
    def getTrackwayPropertiesFromUI(self):
        dictionary = dict()
        dictionary[TrackwayPropEnum.COMM.name]     = self.communityLEdit.text()
        dictionary[TrackwayPropEnum.SITE.name]     = self.siteLEdit.text()
        dictionary[TrackwayPropEnum.YEAR.name]     = self.yearLEdit.text()
        dictionary[TrackwayPropEnum.SECTOR.name]   = self.sectorLEdit.text()
        dictionary[TrackwayPropEnum.LEVEL.name]    = self.levelLEdit.text()
        dictionary[TrackwayPropEnum.TRACKWAY.name] = self.trackwayLEdit.text()
        return dictionary

#___________________________________________________________________________________________________ getTrackPropertiesFromUI
    def getTrackPropertiesFromUI(self):
        dictionary = dict()
        n = self.getNameFromUI()
        if n != "":
            dictionary[TrackPropEnum.NAME.name] = n
        dictionary[TrackPropEnum.NOTE.name]     = self.noteTEdit.toPlainText()
#       dictionary[TrackPropEnum.SNAPSHOT.name] = ... must come from the node or DB, not the UI
#       dictionary[TrackPropEnum.INDEX.name]    = ... must come from the node or DB, not the UI
        w = self.widthLEdit.text()
        if w != "":
            dictionary[TrackPropEnum.WIDTH.name] = float(w)
        l = self.lengthLEdit.text()
        if l != "":
            dictionary[TrackPropEnum.LENGTH.name] = float(l)
        r = self.rotationLEdit.text()
        if r != "":
            dictionary[TrackPropEnum.ROTATION.name] = float(r)
        return dictionary

#___________________________________________________________________________________________________ setSelected
    def setSelectedTracks(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return
        for t in selectedTracks:
             t.setTrackwayProperties(self.getTrackwayPropertiesFromUI())
        if len(selectedTracks) == 1:
            selectedTracks[0].setTrackProperties(self.getTrackPropertiesFromUI())

#___________________________________________________________________________________________________ refreshUI
    def refreshUI(self):
        selectedTracks = self.getSelectedTracks()

        if not selectedTracks or len(selectedTracks) > 1:
            self.communityLEdit.setText(self._BLANK)
            self.siteLEdit.setText(self._BLANK)
            self.yearLEdit.setText(self._BLANK)
            self.sectorLEdit.setText(self._BLANK)
            self.levelLEdit.setText(self._BLANK)
            self.trackwayLEdit.setText(self._BLANK)
            self.rightLeftLEdit.setText(self._BLANK)
            self.manusPesLEdit.setText(self._BLANK)
            self.numberLEdit.setText(self._BLANK)
            self.lengthLEdit.setText(self._BLANK)
            self.lengthUncertaintyLEdit.setText(self._BLANK)
            self.widthLEdit.setText(self._BLANK)
            self.widthUncertaintyLEdit.setText(self._BLANK)
            self.rotationLEdit.setText(self._BLANK)
            self.rotationUncertaintyLEdit.setText(self._BLANK)
            self.noteTEdit.setText(self._BLANK)
        else:
            s = selectedTracks[0]
            community = s.getTrackwayProp(TrackwayPropEnum.COMM)
            if community is None:
                community = ""
            self.communityLEdit.setText(community)
            site = s.getTrackProp(TrackwayPropEnum.SITE)
            if site is None:
                site = ""
            self.siteLEdit.setText(site)
            year = s.getTrackProp(TrackwayPropEnum.YEAR)
            if year is None:
                year = ""
            self.yearLEdit.setText(year)
            sector = s.getTrackProp(TrackwayPropEnum.SECTOR)
            if sector is None:
                sector = ""
            self.sectorLEdit.setText(sector)
            level = s.getTrackProp(TrackwayPropEnum.LEVEL)
            if sector is None:
                level = ""
            self.levelLEdit.setText(level)
            trackway = s.getTrackProp(TrackwayPropEnum.TRACKWAY)
            if trackway is None:
                trackway = ""
            self.trackwayLEdit.setText(trackway)
            name = s.getTrackProp(TrackPropEnum.NAME)
            self.rightLeftLEdit.setText(name[0])
            self.manusPesLEdit.setText(name[1])
            self.numberLEdit.setText(name[2:])
            width = s.getWidth()
            self.widthLEdit.setText(   "%.2f" % width)
            self.lengthLEdit.setText(  "%.2f" % s.getLength())
            print "in refresh, rotation = %s"  % s.getRotation()
            self.rotationLEdit.setText("%.2f" % s.getRotation())
            self.noteTEdit.setText(s.getTrackProp(TrackPropEnum.NOTE))

#___________________________________________________________________________________________________ renameSelectedTracks
    def renameSelectedTracks(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
             return None
        #trackwayProps = self.getTrackwayPropertiesFromUI()
        #trackProps = self.getTrackProperties()
        name = self.rightLeftLEdit.text() + self.manusPesLEdit.text() + self.numberLEdit.text()
        for track in selectedTracks:
             track.setName(name)
             name = self.incrementName(name)

#___________________________________________________________________________________________________ selectSuccessorTracks
    def selectSuccessorTracks(self):
        t = self.getLastSelectedTrack()
        if not t:
            print 'Select at least one track'
            return
        n = t.getNextTrack()
        successorNodes = list()
        while n:
            successorNodes.append(n.node)
            n = n.getNextTrack()
        cmds.select(successorNodes)

#___________________________________________________________________________________________________ selectPrecursorTracks
    def selectPrecursorTracks(self):
         t = self.getFirstSelectedTrack()
         if not t:
             print 'Select at least one track'
             return
         p = t.getPrevTrack()
         precursorNodes = list()
         while p:
            precursorNodes.append(p.node)
            p = p.getPrevTrack()
         cmds.select(precursorNodes)

#___________________________________________________________________________________________________ selectTrackSeries
    def selectTrackSeries(self):
        tracks = self.getTrackSeries()
        if tracks is None:
            return
        print "selected track series consists of %s tracks" % len(tracks)
        nodes = list()
        for t in tracks:
            nodes.append(t.node)
        cmds.select(nodes)

#___________________________________________________________________________________________________ deleteSelectedTracks
    def deleteSelectedTracks(self):
        tracks = self.getSelectedTracks()
        if tracks is None:
            return
        self.unlinkSelectedTracks()
        nodes = list()
        for t in tracks:
            nodes.append(t.node)
        cmds.delete(nodes)

#___________________________________________________________________________________________________ selectAllTracks
    def selectAllTracks(self):
        tracks = self.getAllTracks()
        if len(tracks) == 0:
            return
        nodes = list()
        for t in tracks:
            nodes.append(t.node)
        cmds.select(nodes)

#___________________________________________________________________________________________________ exportSelectedTracks
    def exportSelectedTracks(self):
        tracks = self.getSelectedTracks()
        return tracks

#___________________________________________________________________________________________________ test
    def test(self):
        pass;
