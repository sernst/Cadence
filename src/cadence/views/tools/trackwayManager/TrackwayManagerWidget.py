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
        self.selectTrackwayBtn.clicked.connect(self.selectAllTracks)

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
        nodes = cmds.ls('track*') # presumes object is a track node iff name starts with 'track'

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
        while t.prev is not None:
            t = t.prev
        return t

#___________________________________________________________________________________________________ getLastTrack
    def getLastTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        t = selectedTracks[-1]
        while t.next is not None:
            t = t.next
        return t

#___________________________________________________________________________________________________ getFirstSelectedTrack
    def getFirstSelectedTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        s = selectedTracks[0]
        while s.prev in selectedTracks:
            s = s.prev
        return s

#___________________________________________________________________________________________________ getLastSelectedTrack
    def getLastSelectedTrack(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return None
        s = selectedTracks[-1]
        while s.next in selectedTracks:
            s = s.next
        return s

 #__________________________________________________________________________________________________ getTrackSeries
    def getTrackSeries(self):
        series = list()
        t = self.getFirstTrack()
        while t:
            series.append(t)
            t = t.next
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
        p = t.prev
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
        n = t.next
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
        p = s1.prev
        n = s2.next

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

#___________________________________________________________________________________________________ initializeTrackway
    def initializeTrackway(self):
        """  This creates the initial two tracks for each of the four series of a trackway.
        Select the eight initial tracks and then set series information"""

        trackProperties = self.getTrackPropertiesFromUI()
        # load up a new dictionary for this

        lp1 = Track(Track.createNode())
        lp1.name = 'LP1'
        lp1.x = 200.0
        lp1.z = 100.0
        lp1.width = 0.4
        lp1.length = 0.6

        rp1 = Track(Track.createNode())
        rp1.name = 'RP1'
        rp1.x = 100.0
        rp1.z = 100.0
        rp1.width = 0.4
        rp1.length = 0.6

        lm1 = Track(Track.createNode())
        lm1.name = 'LM1'
        lm1.x = 200.0
        lm1.z = 200.0
        lm1.width = 0.25
        lm1.length = 0.2

        rm1 = Track(Track.createNode())
        rm1.name = 'RM1'
        rm1.x = 100.0
        rm1.z = 200.0
        rm1.width = 0.25
        rm1.length = 0.2

        lp2 = Track(Track.createNode())
        lp2.name = 'LP2'
        lp2.x = 200.0
        lp2.z = 400.0
        lp2.width = 0.4
        lp2.length = 0.6

        rp2 = Track(Track.createNode())
        rp2.name = 'RP2'
        rp2.x = 100.0
        rp2.z = 400.0
        rp2.width = 0.4
        rp2.length = 0.6

        lm2 = Track(Track.createNode())
        lm2.name = 'LM2'
        lm2.x = 200.0
        lm2.z = 500.0
        lm2.width = 0.25
        lm2.length = 0.2

        rm2 = Track(Track.createNode())
        rm2.name = 'RM2'
        rm2.x = 100.0
        rm2.z = 500.0
        rm2.width = 0.25
        rm2.length = 0.2

        lp2.link(lp1)
        rp2.link(rp1)
        lm2.link(lm1)
        rm2.link(rm1)

        cmds.select([
            lp1.node, rp1.node, lm1.node, rm1.node,
            lp2.node, rp2.node, lm2.node, rm2.node] )
        lp1.setCadenceCamFocus()
        self.setSelectedTracks()

#___________________________________________________________________________________________________ addTrack
    def addTrack(self):
        lastTrack = self.getLastTrack()
        if lastTrack is None:
            return
        prevTrack = lastTrack.prev
        nextTrack = Track(cmds.duplicate(lastTrack.node)[0])
        nextName  = Track.incrementName(lastTrack.name)
        nextTrack.name = nextName
        dx = lastTrack.x - prevTrack.x
        dz = lastTrack.z - prevTrack.z
        nextTrack.x = lastTrack.x + dx
        nextTrack.z = lastTrack.z + dz
        nextTrack.link(lastTrack)
        self.refreshUI()

#___________________________________________________________________________________________________ getNamefromUI
    def getNameFromUI(self):
        return self.rightLeftLE.text() + self.manusPesLE.text() + self.numberLE.text()

#___________________________________________________________________________________________________ getTrackPropertiesFromUI
    def getTrackwayPropertiesFromUI(self):
        dictionary = dict()

        dictionary[TrackPropEnum.COMM.name]     = self.communityLE.text()
        dictionary[TrackPropEnum.SITE.name]     = self.siteLE.text()
        dictionary[TrackPropEnum.YEAR.name]     = self.yearLE.text()
        dictionary[TrackPropEnum.SECTOR.name]   = self.sectorLE.text()
        dictionary[TrackPropEnum.LEVEL.name]    = self.levelLE.text()
        dictionary[TrackPropEnum.TRACKWAY.name] = self.trackwayLE.text()
        return dictionary

#___________________________________________________________________________________________________ getTrackPropertiesFromUI
    def getTrackPropertiesFromUI(self):
        dictionary = self.getTrackwayPropertiesFromUI() # first get the trackway properties
        # then add to the dictionary the specifics of a given track
        dictionary[TrackPropEnum.NAME.name]  = self.getNameFromUI()
        dictionary[TrackPropEnum.INDEX.name] = self.indexLE.text()
        dictionary[TrackPropEnum.ID.name]    = self.idLE.text()
        dictionary[TrackPropEnum.NOTE.name]  = self.noteTE.toPlainText()

        v = self.widthLE.text()
        if v != '':
            dictionary[TrackPropEnum.WIDTH.name] = float(v)
        v = self.widthUncertaintyLE.text()
        if v != '':
            dictionary[TrackPropEnum.WIDTH_UNCERTAINTY.name] = float(v)
        v = self.widthMeasuredLE.text()
        if v != '':
            dictionary[TrackPropEnum.WIDTH_MEASURED.name] = float(v)

        v = self.lengthLE.text()
        if v != '':
            dictionary[TrackPropEnum.LENGTH.name] = float(v)
        v = self.lengthUncertaintyLE.text()
        if v != '':
            dictionary[TrackPropEnum.LENGTH_UNCERTAINTY.name] = float(v)
        v = self.lengthMeasuredLE.text()
        if v != '':
            dictionary[TrackPropEnum.LENGTH_MEASURED.name] = float(v)

        v = self.rotationLE.text()
        if v != '':
            dictionary[TrackPropEnum.ROTATION.name] = float(v)
        v = self.rotationUncertaintyLE.text()
        if v != '':
            dictionary[TrackPropEnum.ROTATION_UNCERTAINTY.name] = float(v)

        v = self.xLE.text()
        if v != '':
            dictionary[TrackPropEnum.X.name] = float(v)
        v = self.zLE.text()
        if v != '':
            dictionary[TrackPropEnum.Z.name] = float(v)

        return dictionary

#___________________________________________________________________________________________________ setSelected
    def setSelectedTracks(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        if len(selectedTracks) == 1:
            selectedTracks[0].setProperties(self.getTrackPropertiesFromUI())
            return

        dictionary = self.getTrackwayPropertiesFromUI()
        dictionary[TrackPropEnum.NOTE.name] = self.noteTE.toPlainText()
        for t in selectedTracks:
            t.setProperties(dictionary)

#___________________________________________________________________________________________________ clearUI
    def clearUI(self):
        self.communityLE.setText('')
        self.siteLE.setText('')
        self.yearLE.setText('')
        self.sectorLE.setText('')
        self.levelLE.setText('')
        self.trackwayLE.setText('')
        self.rightLeftLE.setText('')
        self.manusPesLE.setText('')
        self.numberLE.setText('')

        self.widthLE.setText('')
        self.widthUncertaintyLE.setText('')
        self.widthMeasuredLE.setText('')

        self.lengthLE.setText('')
        self.lengthUncertaintyLE.setText('')
        self.lengthMeasuredLE.setText('')

        self.rotationLE.setText('')
        self.rotationUncertaintyLE.setText('')

        self.indexLE.setText('')
        self.idLE.setText('')
        self.noteTE.setPlainText('')

        self.xLE.setText('')
        self.zLE.setText('')

        self.firstBtn.setText('First Track')
        self.prevBtn.setText('Prev Track')
        self.nextBtn.setText('Next Track')
        self.lastBtn.setText('Last Track')

#___________________________________________________________________________________________________ refreshUI
    def refreshUI(self):
        selectedTracks = self.getSelectedTracks()
        if not selectedTracks:
            return

        t = selectedTracks[0]

        v = t.getProperty(TrackPropEnum.COMM)
        self.communityLE.setText(u'' if v is None else v)

        v = t.getProperty(TrackPropEnum.SITE)
        self.siteLE.setText(u'' if v is None else v)

        v = t.getProperty(TrackPropEnum.YEAR)
        self.yearLE.setText(u'' if v is None else v)

        v = t.getProperty(TrackPropEnum.SECTOR)
        self.sectorLE.setText(u'' if v is None else v)

        v = t.getProperty(TrackPropEnum.LEVEL)
        self.levelLE.setText(u'' if v is None else v)

        v = t.getProperty(TrackPropEnum.TRACKWAY)
        self.trackwayLE.setText(u'' if v is None else v)

        if len(selectedTracks) == 1:
            v = t.getProperty(TrackPropEnum.NAME)
            v = '' if v is None else v
            self.rightLeftLE.setText(v[0])
            self.manusPesLE.setText(v[1])
            self.numberLE.setText(v[2:])

            v = t.getProperty(TrackPropEnum.WIDTH)
            self.widthLE.setText(u'' if v is None else '%.2f' % v)

            v = t.getProperty(TrackPropEnum.WIDTH_MEASURED)
            self.widthMeasuredLE.setText(u'' if v is None else '%.2f' % v)

            v = t.getProperty(TrackPropEnum.WIDTH_UNCERTAINTY)
            self.widthUncertaintyLE.setText(u'' if v is None else '%.2f' % v)

            v = t.getProperty(TrackPropEnum.LENGTH)
            self.lengthLE.setText(u'' if v is None else '%.2f' % v)

            v = t.getProperty(TrackPropEnum.LENGTH_MEASURED)
            self.lengthMeasuredLE.setText(u'' if v is None else '%.2f' % v)

            v = t.getProperty(TrackPropEnum.LENGTH_UNCERTAINTY)
            self.lengthUncertaintyLE.setText(u'' if v is None else '%.2f' % v)

            v = t.getProperty(TrackPropEnum.ROTATION)
            self.rotationLE.setText(u'' if v is None else '%.2f' % v)

            v = t.getProperty(TrackPropEnum.ROTATION_UNCERTAINTY)
            self.rotationUncertaintyLE.setText(u'' if v is None else '%.2f' % v)

            v = t.getProperty(TrackPropEnum.INDEX)
            self.indexLE.setText(u'' if v is None else v)

            v = t.getProperty(TrackPropEnum.ID)
            self.idLE.setText(u'' if v is None else v)

            v = t.getProperty(TrackPropEnum.NOTE)
            self.noteTE.setPlainText(u'' if v is None else v)

            v = t.getProperty(TrackPropEnum.X)
            self.xLE.setText(u'' if v is None else '%.2f' % v)

            v = t.getProperty(TrackPropEnum.Z)
            self.zLE.setText(u'' if v is None else '%.2f' % v)

            v = self.getFirstTrack()
            self.firstTrackLbl.setText(u'' if v is None else unicode(v))

            v = t.prev
            self.prevTrackLbl.setText(u'' if v is None else unicode(v))

            v = t.next
            self.nextTrackLbl.setText(u'' if v is None else unicode(v))

            v = self.getLastTrack()
            self.lastTrackLbl.setText(u'' if v is None else unicode(v))
        else:
            self.clearUI()

#___________________________________________________________________________________________________ renameSelectedTracks
    def renameSelectedTracks(self):
        selectedTracks = self.getSelectedTracks()
        if selectedTracks is None:
             return None
        name = self.getNameFromUI()
        for t in selectedTracks:
             t.name = name
             name   = Track.incrementName(name)

#___________________________________________________________________________________________________ selectSuccessorTracks
    def selectSuccessorTracks(self):
        t = self.getLastSelectedTrack()
        if t is None:
            print 'Select at least one track'
            return
        n = t.next
        successorNodes = list()
        while n:
            successorNodes.append(n.node)
            n = n.next
        cmds.select(successorNodes)

#___________________________________________________________________________________________________ selectPrecursorTracks
    def selectPrecursorTracks(self):
         t = self.getFirstSelectedTrack()
         if t is None:
             print 'Select at least one track'
             return
         p = t.prev
         precursorNodes = list()
         while p:
            precursorNodes.append(p.node)
            p = p.prev
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

        if tracks is None:
            return

        l = list()
        for t in tracks:
            l.append(t.getProperties())

        JSON.toFile('../../sandbox/test.json', l)

        return tracks

#___________________________________________________________________________________________________ test
    def test(self):
        pass
