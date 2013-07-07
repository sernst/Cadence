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

        self.cloneButton.clicked.connect(self._cloneTracks)
        self.deleteButton.clicked.connect(self._deleteTracks)
        self.firstButton.clicked.connect(self._goToFirstTrack)
        self.initButton.clicked.connect(self._initializeTrackway)
        self.lastButton.clicked.connect(self._goToLastTrack)
        self.linkButton.clicked.connect(self._linkTracks)
        self.newButton.clicked.connect(self._newTrack)
        self.nextButton.clicked.connect(self._goToNextTrack)
        self.prevButton.clicked.connect(self._goToPreviousTrack)
        self.refreshButton.clicked.connect(self._refresh)
        self.selectAllButton.clicked.connect(self._selectAll)
        self.selectLaterButton.clicked.connect(self._selectSuccessors)
        self.selectPriorButton.clicked.connect(self._selectPrecursors)
        self.setButton.clicked.connect(self._setMetadata)
        self.testButton.clicked.connect(self._test)
        self.unlinkButton.clicked.connect(self._unlinkTracks)
        self.adjustSize()
        self._refresh()

#===================================================================================================
#                                                                                                     P R O T E C T E D
#
#___________________________________________________________________________________________________ _cloneTracks
    def _cloneTracks(self):
        name = self.nameLineEdit.text()
        if name == self._BLANK:
            print 'CLONE: Must specify initial track name (e.g., LP1 or RM1)'
            return
        metadata = self._getMetadata()
        TrackwayManager.cloneTracks(name, metadata)
        self._refresh()
#___________________________________________________________________________________________________ _linkTracks
    def _linkTracks(self):
        TrackwayManager.linkTracks()
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
#___________________________________________________________________________________________________ _getMetadata
    def _getMetadata(self):
        site     = self.siteLineEdit.text()
        level    = self.levelLineEdit.text()
        trackway = self.trackwayLineEdit.text()
        note     = self.noteTextEdit.toPlainText()
        return [site, level, trackway, note]
#___________________________________________________________________________________________________ _setMetadata
    def _setMetadata(self):
        metadata = self._getMetadata()
        selected = TrackwayManager.getSelectedTracks()
        if not selected:
            return
        for s in selected:
            TrackwayManager.setMetadata(s, *metadata)
        if len(selected) == 1:
            TrackwayManager.setName(selected[0], self.nameLineEdit.text())

#___________________________________________________________________________________________________ _refresh
    def _refresh(self):
        selected = TrackwayManager.getSelectedTracks()
        if len(selected) == 1:
            s = selected[0]
            self.siteLineEdit.setText(TrackwayManager.getSite(s))
            self.levelLineEdit.setText(TrackwayManager.getLevel(s))
            self.trackwayLineEdit.setText(TrackwayManager.getTrackway(s))
            self.noteTextEdit.setText(TrackwayManager.getNote(s))
            self.nameLineEdit.setText(TrackwayManager.getName(s))
        else:
            self.siteLineEdit.setText('BSY')
            self.levelLineEdit.setText('1040')
            self.trackwayLineEdit.setText('S18')
            self.noteTextEdit.setText('An example of a remarkable trackway')
            # self.siteLineEdit.setText(self._BLANK)
            # self.levelLineEdit.setText(self._BLANK)
            # self.trackwayLineEdit.setText(self._BLANK)
            # self.noteTextEdit.setText(self._BLANK)
            self.nameLineEdit.setText(self._BLANK)

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
