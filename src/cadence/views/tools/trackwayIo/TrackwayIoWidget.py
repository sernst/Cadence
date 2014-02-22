# TrackwayIoWidget.py
# (C)2013-2014
# Scott Ernst

import sqlalchemy as sqla

from PySide import QtCore
from PySide import QtGui

from pyaid.file.FileUtils import FileUtils
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager
from pyglass.elements.PyGlassElementUtils import PyGlassElementUtils
from pyglass.elements.DataListWidgetItem import DataListWidgetItem
from pyglass.widgets.PyGlassWidget import PyGlassWidget
from cadence.enum.TrackPropEnum import TrackPropEnum

from cadence.enum.UserConfigEnum import UserConfigEnum
from cadence.dataio.TrackCsvImporterRemoteThread import TrackCsvImporterRemoteThread
from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ Viewer
class TrackwayIoWidget(PyGlassWidget):
    """ User interface class for handling track data IO from any of the possible sources and
        saving them to, or loading them from the database. """

#===================================================================================================
#                                                                                       C L A S S

    _OVERWRITE_IMPORT_SUFFIX = '_OVERWRITE_IMPORT'

    RESOURCE_FOLDER_PREFIX = ['tools']

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayIoWidget, self).__init__(parent, **kwargs)

        PyGlassElementUtils.registerCheckBox(
            owner=self,
            target=self.overwriteImportChk,
            configSetting=self.__class__.__name__ + self._OVERWRITE_IMPORT_SUFFIX)

        self.loadBtn.clicked.connect(self._handleLoadTracks)
        self.importBtn.clicked.connect(self._handleImportCsv)
        self._thread = None

        self._getLayout(self.filterBox, QtGui.QHBoxLayout, True)
        self._filterList = []

        filterDefs = [
            {'enum':TrackPropEnum.SITE, 'label':'Site'},
            {'enum':TrackPropEnum.LEVEL, 'label':'Level'},
            {'enum':TrackPropEnum.SECTOR, 'label':'Sector'},
            {'enum':TrackPropEnum.TRACKWAY_NUMBER, 'label':'Trackway'} ]

        index = 0
        for f in filterDefs:
            flBox, flBoxLayout = self._createWidget(self.filterBox, QtGui.QVBoxLayout, True)

            label = QtGui.QLabel(flBox)
            label.setText(f['label'])
            flBoxLayout.addWidget(label)

            fl = QtGui.QListWidget(self)
            fl.currentItemChanged.connect(self._handleFilterChange)
            flBoxLayout.addWidget(fl)
            f['index']  = index
            f['widget'] = fl
            self._filterList.append(f)
            index += 1

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _activateWidgetDisplayImpl
    def _activateWidgetDisplayImpl(self, **kwargs):
        model   = Tracks_Track.MASTER
        session = model.createSession()
        for filterDef in self._filterList:
            self._updateFilterList(filterDef, session)
        session.close()

#___________________________________________________________________________________________________ _updateFilterList
    def _updateFilterList(self, filterDef, session, filterDict =None):
        model = Tracks_Track.MASTER
        query = session.query(sqla.distinct(getattr(model, filterDef['enum'].name)))

        if filterDict:
            for key,value in filterDict.iteritems():
                query = query.filter(getattr(model, key) == value)

        result = query.all()

        fl = filterDef['widget']
        fl.clear()
        for item in result:
            DataListWidgetItem(str(item[0]), fl, id=str(item[0]), data=item[0])
        fl.sortItems()
        first = DataListWidgetItem('(All)', id='ALL', data=None)
        fl.insertItem(0, first)
        first.setSelected(True)

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleLoadTracks
    def _handleLoadTracks(self):
        self.setEnabled(False)
        self.refreshGui()

        model   = Tracks_Track.MASTER
        session = model.createSession()
        query   = session.query(model)

        for filterDef in self._filterList:
            items = filterDef['widget'].selectedItems()
            if not items or items[0].itemData is None:
                continue
            query = query.filter(getattr(model, filterDef['enum'].name) == items[0].itemData)

        entries = query.all()
        count   = len(entries)
        for entry in entries:
            entry.createNode()
        session.close()
        self.setEnabled(True)

        PyGlassBasicDialogManager.openOk(
            parent=self, header=str(count) + ' Tracks Created')

#___________________________________________________________________________________________________ _handleImportCsv
    def _handleImportCsv(self):
        path = PyGlassBasicDialogManager.browseForFileOpen(
            parent=self,
            caption=u'Select CSV File to Import',
            defaultPath=self.mainWindow.appConfig.get(UserConfigEnum.LAST_BROWSE_PATH) )
        if not path:
            return

        # Store directory location as the last active directory
        self.mainWindow.appConfig.set(
            UserConfigEnum.LAST_BROWSE_PATH,
            FileUtils.getDirectoryOf(path) )

        # Disable gui while import in progress
        self.mainWindow.setEnabled(False)
        self.mainWindow.refreshGui()

        self._thread = TrackCsvImporterRemoteThread(
            parent=self,
            path=path,
            force=self.overwriteImportChk.isChecked())
        self._thread.execute(callback=self._handleCsvImportComplete)

#___________________________________________________________________________________________________ _handleCsvImportComplete
    def _handleCsvImportComplete(self, response):
        if response['response']:
            print 'ERROR: CSV Import Failed'
            print '  OUTPUT:', response['output']
            print '  ERROR:', response['error']

        self.mainWindow.setEnabled(True)

#___________________________________________________________________________________________________ _handleFilterChange
    @QtCore.Slot(QtGui.QListWidgetItem, QtGui.QListWidgetItem)
    def _handleFilterChange(self, current, previous):
        if current is None:
            return

        session = Tracks_Track.MASTER.createSession()

        filterDef   = None
        filterDict = dict()
        for fd in self._filterList:
            if filterDef:
                self._updateFilterList(fd, session, filterDict=filterDict)
            elif current.listWidget() == fd['widget']:
                filterDef = fd
                if current.itemData:
                    filterDict[fd['enum'].name] = current.itemData
            else:
                items = fd['widget'].selectedItems()
                if items and items[0].itemData:
                    filterDict[fd['enum'].name] = items[0].itemData

        session.close()
