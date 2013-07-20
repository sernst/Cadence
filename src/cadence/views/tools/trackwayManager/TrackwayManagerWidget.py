# TrackwayManagerWidget.py
# (C)2012-2013
# Scott Ernst and Kent A. Stevens
from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.mayan.trackway.TrackwayManager import TrackwayManager

#___________________________________________________________________________________________________ TrackwayManagerWidget
class TrackwayManagerWidget(PyGlassWidget):

#===================================================================================================
#                                                                                                    C L A S S
    RESOURCE_FOLDER_PREFIX = ['tools']

    _BLANK = ' -- '
#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayManagerWidget, self).__init__(parent, **kwargs)


        path = self.getResourcePath('..', '..', 'help.markdown', isFile=True) #gives you the TrackwayManager folder
        print "in the TrackwayManagerWidget, the path =%s" % path
        # get a qIcon or something or QButton icon and put the icons in the TrackwayManager Widget
        # folder and commit them to the project also. Look for them in the changes at the bottom
        # of PyCharm window

        # this returns the path to the shared directory resources/apps/CadenceApplication
        # to get self.getAppResourcePath()

        self.cloneBtn.clicked.connect(self._cloneTracks)
        self.deleteBtn.clicked.connect(self._deleteTracks)
        self.firstBtn.clicked.connect(self._goToFirstTrack)
        self.initBtn.clicked.connect(self._initializeTrackway)
        self.lastBtn.clicked.connect(self._goToLastTrack)
        self.linkBtn.clicked.connect(self._linkTracks)
        self.newBtn.clicked.connect(self._newTrack)
        self.nextBtn.clicked.connect(self._goToNextTrack)
        self.prevBtn.clicked.connect(self._goToPreviousTrack)
        self.refreshBtn.clicked.connect(self._refresh)
        self.renameBtn.clicked.connect(self._rename)
        self.selectAllBtn.clicked.connect(self._selectAll)
        self.selectLaterBtn.clicked.connect(self._selectSuccessors)
        self.selectPriorBtn.clicked.connect(self._selectPrecursors)
        self.setBtn.clicked.connect(self._set)
        self.testBtn.clicked.connect(self._test)
        self.unlinkBtn.clicked.connect(self._unlinkTracks)
        self.adjustSize()
        self._refresh()

#===================================================================================================
#                                                                                                     P R O T E C T E D
#
#___________________________________________________________________________________________________ _cloneTracks
    def _cloneTracks(self):
        name = self.nameLEdit.text()
        if name == self._BLANK:
            print 'CLONE: Must specify initial track name (e.g., LP1 or RM1)'
            return
        metadata = self._getMetadata()
        TrackwayManager.cloneTracks(name, metadata)
        self._refresh()

#___________________________________________________________________________________________________ _linkTracks
    def _linkTracks(self):
        TrackwayManager.linkTracks()
        self._refresh()

 #___________________________________________________________________________________________________ _unlinkTracks
    def _unlinkTracks(self):
        TrackwayManager.unlinkTracks()
        self._refresh()

#___________________________________________________________________________________________________ _goToFirstTrack
    def _goToFirstTrack(self):
        TrackwayManager.goToFirstTrack()
        self._refresh()

#___________________________________________________________________________________________________ _goToPreviousTrack
    def _goToPreviousTrack(self):
        TrackwayManager.goToPreviousTrack()
        self._refresh()

#___________________________________________________________________________________________________ _goToNextTrack
    def _goToNextTrack(self):
        TrackwayManager.goToNextTrack()
        self._refresh()

#___________________________________________________________________________________________________ _goToLastTrack
    def _goToLastTrack(self):
        TrackwayManager.goToLastTrack()
        self._refresh()

#___________________________________________________________________________________________________ _initializeTrackway
    def _initializeTrackway(self):
        metadata = self._getMetadata()
        TrackwayManager.initialize(*metadata)

#___________________________________________________________________________________________________ _newTrack
    def _newTrack(self):
        TrackwayManager.duplicateTrack()
        self._refresh()

#___________________________________________________________________________________________________ _insertTrack
    def _insertTrack(self):
        TrackwayManager.insertTrack()
        self._refresh()

#___________________________________________________________________________________________________ _getMetadata
    def _getMetadata(self):
        site     = self.siteLEdit.text()
        level    = self.levelLEdit.text()
        year     = self.yearLEdit.text()
        trackway = self.trackwayLEdit.text()
        note     = self.noteTEdit.toPlainText()
        return [site, level, trackway, note]

#___________________________________________________________________________________________________ _set
    def _set(self):
        selected = TrackwayManager.getSelectedTracks()
        if not selected:
            return
        metadata = self._getMetadata()
        for s in selected:
            TrackwayManager.setMetadata(s, *metadata)
            number = TrackwayManager.getName(s)[2:]
            name = self.rightLeftLEdit.text() + self.manusPesLEdit.text() + number
            TrackwayManager.setName(s, name)
        if len(selected) == 1:
            name = self.rightLeftLEdit.text() + self.manusPesLEdit.text() + self.numberLEdit.text()
            TrackwayManager.setName(selected[0], name)

#___________________________________________________________________________________________________ _refresh
    def _refresh(self):
        selected = TrackwayManager.getSelectedTracks()
        if not selected:
            self.siteLEdit.setText(self._BLANK)
            self.levelLEdit.setText(self._BLANK)
            self.trackwayLEdit.setText(self._BLANK)
            self.rightLeftLEdit.setText(self._BLANK)
            self.manusPesLEdit.setText(self._BLANK)
            self.numberLEdit.setText(self._BLANK)
            self.noteTEdit.setText(self._BLANK)
            return
        s = selected[0]
        self.siteLEdit.setText(TrackwayManager.getSite(s))
        self.levelLEdit.setText(TrackwayManager.getLevel(s))
        self.trackwayLEdit.setText(TrackwayManager.getTrackway(s))
        name = TrackwayManager.getName(s)
        self.rightLeftLEdit.setText(name[0])
        self.manusPesLEdit.setText(name[1])
        if len(selected) == 1:
            self.numberLEdit.setText(name[2:])
            TrackwayManager.goTo(selected)
        self.noteTEdit.setText(TrackwayManager.getNote(s))


#___________________________________________________________________________________________________ _rename
    def _rename(self):
        metadata = self._getMetadata()
        name = self.rightLeftLEdit.text() + self.manusPesLEdit.text() + self.numberLEdit.text()
        TrackwayManager.renameSelected(name, *metadata)

#___________________________________________________________________________________________________ _test
    def _test(self):
        self._initializeTrackway()

#___________________________________________________________________________________________________
    def _selectSuccessors(self):
        TrackwayManager.selectSuccessors()

#___________________________________________________________________________________________________
    def _selectPrecursors(self):
        TrackwayManager.selectPrecursors()

#___________________________________________________________________________________________________
    def _selectAll(self):
        TrackwayManager.selectAll()

#___________________________________________________________________________________________________
    def _deleteTracks(self):
        TrackwayManager.deleteSelected()
