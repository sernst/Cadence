# TrackwayManagerWidget.py
# (C)2012-2013
# Scott Ernst and Kent A. Stevens


from nimble import cmds

from pyaid.json.JSON import JSON

from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.mayan.trackway.Track import Track

#___________________________________________________________________________________________________ TrackwayManagerWidget
class TrackwayManagerWidget(PyGlassWidget):

#===================================================================================================
#                                                                                                    C L A S S
    RESOURCE_FOLDER_PREFIX = ['tools']

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

#___________________________________________________________________________________________________ getAllTracks
    def getAllTracks(self):
        nodes = cmds.ls('track*')

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
        while t.getPrev():
            t = t.getPrev()
        return t

#___________________________________________________________________________________________________ getLastTrack
    def getLastTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        t = selectedTracks[-1]
        while t.getNext():
            t = t.getNext()
        return t

#___________________________________________________________________________________________________ getFirstSelectedTrack
    def getFirstSelectedTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        s = selectedTracks[0]
        while s.getPrev() in selectedTracks:
            s = s.getPrev()
        return s

#___________________________________________________________________________________________________ getLastSelectedTrack
    def getLastSelectedTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        s = selectedTracks[-1]
        while s.getNext() in selectedTracks:
            s = s.getNext(s)
        return s

 #__________________________________________________________________________________________________ getTrackSeries
    def getTrackSeries(self):
        series = list()
        t = self.getFirstTrack()
        while t:
            series.append(t)
            t = t.getNext()
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
        p = t.getPrev()
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
        n = t.getNext()
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
        p = s1.getPrev()
        n = s2.getNext()

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
        """  This creates the initial two tracks for each of the four series of a trackway.
        Select the eight initial tracks and then set series information"""

        trackProperties = self.getTrackPropertiesFromUI()
        # load up a new dictionary for this

        lp1 = Track(Track.createNode())
        lp1.setName('LP1')
        lp1.setX(200.0)
        lp1.setZ(100.0)
        lp1.setWidth(0.4)
        lp1.setLength(0.6)

        rp1 = Track(Track.createNode())
        rp1.setName('RP1')
        rp1.setX(100.0)
        rp1.setZ(100.0)
        rp1.setWidth(0.4)
        rp1.setLength(0.6)

        lm1 = Track(Track.createNode())
        lm1.setName('LM1')
        lm1.setX(200.0)
        lm1.setZ(200.0)
        lm1.setWidth(0.25)
        lm1.setLength(0.2)

        rm1 = Track(Track.createNode())
        rm1.setName('RM1')
        rm1.setX(100.0)
        rm1.setZ(200.0)
        rm1.setWidth(0.25)
        rm1.setLength(0.2)

        lp2 = Track(Track.createNode())
        lp2.setName('LP2')
        lp2.setX(200.0)
        lp2.setZ(400.0)
        lp2.setWidth(0.4)
        lp2.setLength(0.6)

        rp2 = Track(Track.createNode())
        rp2.setName('RP2')
        rp2.setX(100.0)
        rp2.setZ(400.0)
        rp2.setWidth(0.4)
        rp2.setLength(0.6)

        lm2 = Track(Track.createNode())
        lm2.setName('LM2')
        lm2.setX(200.0)
        lm2.setZ(500.0)
        lm2.setWidth(0.25)
        lm2.setLength(0.2)

        rm2 = Track(Track.createNode())
        rm2.setName('RM2')
        rm2.setX(100.0)
        rm2.setZ(500.0)
        rm2.setWidth(0.25)
        rm2.setLength(0.2)

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
        prevTrack = lastTrack.getPrev()
        nextTrack = Track(cmds.duplicate(lastTrack.node)[0])
        nextName  = Track.incrementName(lastTrack.getName())
        nextTrack.setName(nextName)
        dx = lastTrack.getX() - prevTrack.getX()
        dz = lastTrack.getZ() - prevTrack.getZ()
        nextTrack.setX(lastTrack.getX() + dx)
        nextTrack.setZ(lastTrack.getZ() + dz)
        nextTrack.link(lastTrack)
        self.refreshUI()

#___________________________________________________________________________________________________ getNamefromUI
    def getNameFromUI(self):
        return self.rightLeftLEdit.text() + self.manusPesLEdit.text() + self.numberLEdit.text()

#___________________________________________________________________________________________________ getTrackPropertiesFromUI
    def getPropertiesFromUI(self):
        """This returns a dictionary of only non-empty attribute-value pairs from the UI."""

        dictionary = dict()

        dictionary[TrackPropEnum.COMM.name]     = self.communityLEdit.text()
        dictionary[TrackPropEnum.SITE.name]     = self.siteLEdit.text()
        dictionary[TrackPropEnum.YEAR.name]     = self.yearLEdit.text()
        dictionary[TrackPropEnum.SECTOR.name]   = self.sectorLEdit.text()
        dictionary[TrackPropEnum.LEVEL.name]    = self.levelLEdit.text()
        dictionary[TrackPropEnum.TRACKWAY.name] = self.trackwayLEdit.text()
        dictionary[TrackPropEnum.NAME.name]     = self.getNameFromUI()
        dictionary[TrackPropEnum.INDEX.name]    = self.indexLEdit.text()
        dictionary[TrackPropEnum.NOTE.name]     = self.noteTEdit.toPlainText()

        v = self.widthLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.WIDTH.name] = float(v)

        v = self.widthUncertaintyLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.WIDTH_UNCERTAINTY.name] = float(v)

        v = self.widthMeasuredLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.WIDTH_MEASURED.name] = float(v)

        v = self.lengthLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.LENGTH.name] = float(v)

        v = self.lengthUncertaintyLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.LENGTH_UNCERTAINTY.name] = float(v)

        v = self.lengthMeasuredLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.LENGTH_MEASURED.name] = float(v)

        v = self.rotationLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.ROTATION.name] = float(v)

        v = self.rotationUncertaintyLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.ROTATION_UNCERTAINTY.name] = float(v)

        v = self.xLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.X.name] = float(v)

        v = self.zLEdit.text()
        if v != '':
            dictionary[TrackPropEnum.Z.name] = float(v)

        return dictionary

#___________________________________________________________________________________________________ setSelected
    def setSelectedTracks(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        dictionary = dict()
        if len(selectedTracks) > 1:
            dictionary[TrackPropEnum.COMM.name]     = self.communityLEdit.text()
            dictionary[TrackPropEnum.SITE.name]     = self.siteLEdit.text()
            dictionary[TrackPropEnum.YEAR.name]     = self.yearLEdit.text()
            dictionary[TrackPropEnum.SECTOR.name]   = self.sectorLEdit.text()
            dictionary[TrackPropEnum.LEVEL.name]    = self.levelLEdit.text()
            dictionary[TrackPropEnum.TRACKWAY.name] = self.trackwayLEdit.text()
            dictionary[TrackPropEnum.NOTE.name]     = self.noteTEdit.toPlainText()
            selectedTracks[0].setProperties(dictionary)
        else:
            dictionary = self.getPropertiesFromUI()
        for t in selectedTracks:
            t.setProperties(dictionary)

#___________________________________________________________________________________________________ clearUI
    def clearUI(self):
        self.communityLEdit.setText('')
        self.siteLEdit.setText('')
        self.yearLEdit.setText('')
        self.sectorLEdit.setText('')
        self.levelLEdit.setText('')
        self.trackwayLEdit.setText('')
        self.rightLeftLEdit.setText('')
        self.manusPesLEdit.setText('')
        self.numberLEdit.setText('')

        self.widthLEdit.setText('')
        self.widthUncertaintyLEdit.setText('')
        self.widthMeasuredLEdit.setText('')

        self.lengthLEdit.setText('')
        self.lengthUncertaintyLEdit.setText('')
        self.lengthMeasuredLEdit.setText('')

        self.rotationLEdit.setText('')
        self.rotationUncertaintyLEdit.setText('')

        self.indexLEdit.setText('')
        self.noteTEdit.setPlainText('')

        self.xLEdit.setText('')
        self.zLEdit.setText('')

        self.firstBtn.setText('First Track')
        self.prevBtn.setText('Prev Track')
        self.nextBtn.setText('Next Track')
        self.lastBtn.setText('Last Track')

#___________________________________________________________________________________________________ refreshUI
    def refreshUI(self):
        selectedTracks = self.getSelectedTracks()

        if len(selectedTracks) == 1:
            t = selectedTracks[0]

            s = t.getProperty(TrackPropEnum.COMM)
            s = '' if s is None else s
            self.communityLEdit.setText('' if s is None else s)

            s = t.getProperty(TrackPropEnum.SITE)
            s = '' if s is None else s
            self.siteLEdit.setText('' if s is None else s)

            s = t.getProperty(TrackPropEnum.YEAR)
            s = '' if s is None else s
            self.yearLEdit.setText('' if s is None else s)

            s = t.getProperty(TrackPropEnum.SECTOR)
            self.sectorLEdit.setText('' if s is None else s)

            s = t.getProperty(TrackPropEnum.LEVEL)
            self.levelLEdit.setText('' if s is None else s)

            s = t.getProperty(TrackPropEnum.TRACKWAY)
            self.trackwayLEdit.setText('' if s is None else s)

            s = t.getProperty(TrackPropEnum.NAME)
            s = '' if s is None else s
            self.rightLeftLEdit.setText(s[0])
            self.manusPesLEdit.setText(s[1])
            self.numberLEdit.setText(s[2:])

            v = t.getProperty(TrackPropEnum.WIDTH)
            self.widthLEdit.setText('' if v is None else "%.2f" % v)

            v = t.getProperty(TrackPropEnum.WIDTH_MEASURED)
            self.widthMeasuredLEdit.setText('' if v is None else "%.2f" % v)

            v = t.getProperty(TrackPropEnum.WIDTH_UNCERTAINTY)
            self.widthUncertaintyLEdit.setText('' if v is None else "%.2f" % v)

            v = t.getProperty(TrackPropEnum.LENGTH)
            self.lengthLEdit.setText('' if v is None else "%.2f" % v)

            v = t.getProperty(TrackPropEnum.LENGTH_MEASURED)
            self.lengthMeasuredLEdit.setText('' if v is None else "%.2f" % v)

            v = t.getProperty(TrackPropEnum.LENGTH_UNCERTAINTY)
            self.lengthUncertaintyLEdit.setText('' if v is None else "%.2f" % v)

            v = t.getProperty(TrackPropEnum.ROTATION)
            self.rotationLEdit.setText('' if v is None else "%.2f" % v)

            v = t.getProperty(TrackPropEnum.ROTATION_UNCERTAINTY)
            self.rotationUncertaintyLEdit.setText('' if v is None else "%.2f" % v)

            s = t.getProperty(TrackPropEnum.INDEX)
            self.indexLEdit.setText(u'' if s is None else s)

            s = t.getProperty(TrackPropEnum.NOTE)
            self.noteTEdit.setPlainText(u'' if s is None else s)

            v = t.getProperty(TrackPropEnum.X)
            self.xLEdit.setText(u'' if v is None else "%.2f" % v)

            v = t.getProperty(TrackPropEnum.Z)
            self.zLEdit.setText(u'' if v is None else "%.2f" % v)

            s = self.getFirstTrack()
            self.firstTrackLbl.setText(u'' if s is None else unicode(s))

            s = t.getPrev()
            self.prevTrackLbl.setText(u'' if s is None else unicode(s))

            s = t.getNext()
            self.nextTrackLbl.setText(u'' if s is None else unicode(s))

            s = self.getLastTrack()
            self.lastTrackLbl.setText(u'' if s is None else unicode(s))
        else:
            self.clearUI()

#___________________________________________________________________________________________________ renameSelectedTracks
    def renameSelectedTracks(self):
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
             return None
        name = self.getNameFromUI()
        for t in selectedTracks:
             t.setName(name)
             name = Track.incrementName(name)

#___________________________________________________________________________________________________ selectSuccessorTracks
    def selectSuccessorTracks(self):
        t = self.getLastSelectedTrack()
        if t is None:
            print 'Select at least one track'
            return
        n = t.getNext()
        successorNodes = list()
        while n:
            successorNodes.append(n.node)
            n = n.getNext()
        cmds.select(successorNodes)

#___________________________________________________________________________________________________ selectPrecursorTracks
    def selectPrecursorTracks(self):
         t = self.getFirstSelectedTrack()
         if t is None:
             print 'Select at least one track'
             return
         p = t.getPrev()
         precursorNodes = list()
         while p:
            precursorNodes.append(p.node)
            p = p.getPrev()
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

        l = list()
        for t in tracks:
            l.append(t.getProperties())

        JSON.toFile('../../sandbox/test.json', l)

        return tracks

#___________________________________________________________________________________________________ test
    def test(self):
        pass;
