# TrackwayIoWidget.py
# (C)2013-2014
# Scott Ernst

import os
import sqlalchemy as sqla

from PySide import QtCore
from PySide import QtGui

from pyaid.file.FileUtils import FileUtils
from pyaid.OsUtils import OsUtils
from pyaid.system.SystemUtils import SystemUtils

from pyglass.elements.PyGlassElementUtils import PyGlassElementUtils
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager
from pyglass.elements.DataListWidgetItem import DataListWidgetItem
from pyglass.widgets.PyGlassWidget import PyGlassWidget

import nimble
from cadence.data.TrackExporterRemoteThread import TrackExporterRemoteThread
from cadence.data.TrackLinkageRemoteThread import TrackLinkageRemoteThread

from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.enum.UserConfigEnum import UserConfigEnum
from cadence.data.TrackImporterRemoteThread import TrackImporterRemoteThread
from cadence.mayan.trackway.plugin import CreateTrackNodes
from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ TrackwayIoWidget
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

        self._thread = None

        self.loadBtn.clicked.connect(self._handleLoadTracks)
        self.importCsvBtn.clicked.connect(self._handleImport)
        self.importJsonBtn.clicked.connect(self._handleImport)
        self.exportBtn.clicked.connect(self._handleExport)
        self.updateLinksBtn.clicked.connect(self._handleUpdateLinks)
        self.databaseReplaceBtn.clicked.connect(self._handleReplaceDatabase)

        PyGlassElementUtils.registerCheckBox(
            self, self.exportPrettyCheck,
            configSetting=UserConfigEnum.EXPORT_PRETTY)
        PyGlassElementUtils.registerCheckBox(
            self, self.exportCompressCheck,
            configSetting=UserConfigEnum.EXPORT_COMPRESSED)
        PyGlassElementUtils.registerCheckBox(
            self, self.exportDiffCheck,
            configSetting=UserConfigEnum.EXPORT_DIFF)
        PyGlassElementUtils.registerCheckBox(
            self, self.importCompressCheck,
            configSetting=UserConfigEnum.IMPORT_COMPRESSED)

        self._getLayout(self.filterBox, QtGui.QHBoxLayout, True)
        self._filterList = []
        self._processingFilters = False

        filterDefs = [
            {'enum':TrackPropEnum.SITE,            'label':'Site'},
            {'enum':TrackPropEnum.LEVEL,           'label':'Level'},
            {'enum':TrackPropEnum.SECTOR,          'label':'Sector'},
            {'enum':TrackPropEnum.TRACKWAY_NUMBER, 'label':'Trackway'},
            {'enum':TrackPropEnum.YEAR,            'label':'Year'} ]

        index = 0
        for f in filterDefs:
            flBox, flBoxLayout = self._createWidget(self.filterBox, QtGui.QVBoxLayout, True)

            label = QtGui.QLabel(flBox)
            label.setText(f['label'])
            flBoxLayout.addWidget(label)

            fl = QtGui.QListWidget(self)
            fl.itemSelectionChanged.connect(self._handleFilterChange)
            fl.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
            fl.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
            flBoxLayout.addWidget(fl)
            f['index']  = index
            f['widget'] = fl
            self._filterList.append(f)
            index += 1

        self.tabWidget.currentChanged.connect(self._handleTabChanged)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _activateLoadTab
    def _activateLoadTab(self):
        model   = Tracks_Track.MASTER
        session = model.createSession()
        for filterDef in self._filterList:
            self._updateFilterList(filterDef, session)
        session.close()

#___________________________________________________________________________________________________ _activateWidgetDisplayImpl
    def _activateWidgetDisplayImpl(self, **kwargs):
        self._activateLoadTab()

#___________________________________________________________________________________________________ _updateFilterList
    def _updateFilterList(self, filterDef, session, filterDict =None):
        model = Tracks_Track.MASTER
        query = session.query(sqla.distinct(getattr(model, filterDef['enum'].name)))

        if filterDict:
            for key,value in filterDict.iteritems():
                if isinstance(value, basestring):
                    query = query.filter(getattr(model, key) == value)
                else:
                    query = query.filter(getattr(model, key).in_(value))

        result = query.all()

        fl = filterDef['widget']
        fl.itemSelectionChanged.disconnect(self._handleFilterChange)
        fl.clear()
        for item in result:
            DataListWidgetItem(str(item[0]), fl, id=str(item[0]), data=item[0])
        fl.sortItems()
        first = DataListWidgetItem('(All)', id='ALL', data=None)
        fl.insertItem(0, first)
        first.setSelected(True)
        fl.itemSelectionChanged.connect(self._handleFilterChange)

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleLoadTracks
    def _handleLoadTracks(self):
        self.mainWindow.showLoading(self, u'Loading Tracks')

        model   = Tracks_Track.MASTER
        session = model.createSession()
        query   = session.query(model)

        for filterDef in self._filterList:
            items = filterDef['widget'].selectedItems()
            if not items or items[0].itemData is None:
                continue
            query = query.filter(getattr(model, filterDef['enum'].name) == items[0].itemData)

        # Prevents tracks that have been "hidden" from being loaded into the scene
        # query = query.filter(model.hidden == False)

        entries   = query.all()
        count     = len(entries)
        trackList = []
        for entry in entries:
            trackList.append(entry.toMayaNodeDict())
        session.close()

        if not trackList:
            self.mainWindow.hideLoading(self)
            return

        conn = nimble.getConnection()
        result = conn.runPythonModule(
            CreateTrackNodes,
            trackList=trackList,
            runInMaya=True)
        if not result.success:
            PyGlassBasicDialogManager.openOk(
                parent=self, header=u'Load Error', message=u'Unable to load tracks')
        else:
            PyGlassBasicDialogManager.openOk(
                parent=self, header=str(count) + ' Tracks Created')

        self.mainWindow.hideLoading(self)

#___________________________________________________________________________________________________ _handleImport
    def _handleImport(self):
        btn  = self.sender()
        if btn == self.importCsvBtn:
            label = u'CSV'
            importType = TrackImporterRemoteThread.CSV
        else:
            label = u'JSON'
            importType = TrackImporterRemoteThread.JSON

        self.mainWindow.showLoading(
            self,
            u'Browsing for Track File',
            u'Choose the %s file to import into the database' % label)

        path = PyGlassBasicDialogManager.browseForFileOpen(
            parent=self,
            caption=u'Select %s File to Import' % label,
            defaultPath=self.mainWindow.appConfig.get(UserConfigEnum.LAST_BROWSE_PATH) )

        self.mainWindow.hideLoading(self)
        if not path or not isinstance(path, basestring):
            self.mainWindow.toggleInteractivity(True)
            return

        # Store directory location as the last active directory
        self.mainWindow.appConfig.set(
            UserConfigEnum.LAST_BROWSE_PATH,
            FileUtils.getDirectoryOf(path) )

        self.mainWindow.showStatus(
            self,
            u'Importing Tracks',
            u'Reading track information into database')

        self._thread = TrackImporterRemoteThread(
            parent=self,
            path=path,
            importType=importType,
            compressed=self.importCompressCheck.isChecked())
        self._thread.execute(
            callback=self._handleImportComplete,
            logCallback=self._handleImportStatusUpdate)

#___________________________________________________________________________________________________ _handleUpdateLinks
    def _handleUpdateLinks(self):

        result = PyGlassBasicDialogManager.openYesNo(
            self,
            u'Confirm Linkages Reset',
            u'Are you sure you want to reset all track linkages within the current database?',
            False)

        if not result:
            return

        self.mainWindow.showStatus(
            self,
            u'Resetting Linkages',
            u'Updating linkages to their default values')

        self._thread = TrackLinkageRemoteThread(parent=self)
        self._thread.execute(
            callback=self._handleImportComplete,
            logCallback=self._handleImportStatusUpdate)


#___________________________________________________________________________________________________ _handleImportStatusUpdate
    def _handleImportStatusUpdate(self, message):
        self.mainWindow.appendStatus(self, message)

#___________________________________________________________________________________________________ _handleImportComplete
    def _handleImportComplete(self, response):
        actionType = 'Export' if isinstance(self._thread, TrackExporterRemoteThread) else 'Import'

        if response['response']:
            print 'ERROR: %s Failed' % actionType
            print '  OUTPUT:', response['output']
            print '  ERROR:', response['error']
            PyGlassBasicDialogManager.openOk(
                parent=self,
                header='ERROR',
                message=actionType + ' operation failed')
        else:
            PyGlassBasicDialogManager.openOk(
                parent=self,
                header='Success',
                message=actionType + ' operation complete')

        self.mainWindow.showStatusDone(self)

#___________________________________________________________________________________________________ _handleFilterChange
    def _handleFilterChange(self):
        if self._processingFilters:
            return
        self._processingFilters = True

        sender = self.sender()
        model = Tracks_Track.MASTER
        session = model.createSession()
        filterDef = None
        filterDict = dict()

        for fd in self._filterList:
            if filterDef:
                self._updateFilterList(fd, session, filterDict=filterDict)
                continue

            if sender == fd['widget']:
                filterDef = fd

            items = fd['widget'].selectedItems()
            if not items or not len(items):
                continue

            entries = []
            for item in items:
                if item and item.itemData:
                    entries.append(item.itemData)
            if entries:
                filterDict[fd['enum'].name] = entries

        session.close()
        self._processingFilters = False

#___________________________________________________________________________________________________ _handleTabChanged
    QtCore.Signal(int)
    def _handleTabChanged(self, index):
        if index == 0:
            self._activateLoadTab()

#___________________________________________________________________________________________________ _handleExport
    def _handleExport(self):

        self.mainWindow.showLoading(
            self,
            u'Browsing for Exporting File',
            u'Choose the file location to save the export')

        defaultPath = self.mainWindow.appConfig.get(UserConfigEnum.LAST_SAVE_PATH)
        if not defaultPath:
            defaultPath = self.mainWindow.appConfig.get(UserConfigEnum.LAST_BROWSE_PATH)

        path = PyGlassBasicDialogManager.browseForFileSave(
            parent=self, caption=u'Specify Export File', defaultPath=defaultPath)
        self.mainWindow.hideLoading(self)

        if not path:
            self.mainWindow.toggleInteractivity(True)
            return

        # Store directory location as the last save directory
        self.mainWindow.appConfig.set(
            UserConfigEnum.LAST_SAVE_PATH,
            FileUtils.getDirectoryOf(path) )

        if not path.endswith('.json'):
            path += '.json'

        self.mainWindow.showStatus(
            self,
            u'Exporting Tracks',
            u'Writing track information from database')

        self._thread = TrackExporterRemoteThread(
            self, path=path,
            pretty=self.exportPrettyCheck.isChecked(),
            compressed=self.exportCompressCheck.isChecked(),
            difference=self.exportDiffCheck.isChecked())

        self._thread.execute(
            callback=self._handleImportComplete,
            logCallback=self._handleImportStatusUpdate)

#___________________________________________________________________________________________________ _handleReplaceDatabase
    def _handleReplaceDatabase(self):

        self.mainWindow.showLoading(
            self,
            u'Browsing for Database File',
            u'Choose a valid database (*.vcd) file')

        defaultPath = self.appConfig.get(UserConfigEnum.DATABASE_IMPORT_PATH)
        if not defaultPath:
            defaultPath = self.appConfig.get(UserConfigEnum.LAST_BROWSE_PATH)

        path = PyGlassBasicDialogManager.browseForFileOpen(
            parent=self,
            caption=u'Select Database File',
            defaultPath=defaultPath)
        self.mainWindow.hideLoading(self)

        if not path:
            self.mainWindow.toggleInteractivity(True)
            return

        # Store directory for later use
        self.appConfig.set(
            UserConfigEnum.DATABASE_IMPORT_PATH,
            FileUtils.getDirectoryOf(path) )

        self.mainWindow.showStatus(
            self,
            u'Replacing Database File',
            u'Removing existing database file and replacing it with selection')

        sourcePath = getattr(Tracks_Track, 'URL')[len(u'sqlite:'):].lstrip(u'/')
        if not OsUtils.isWindows():
            sourcePath = u'/' + sourcePath

        savePath = sourcePath + u'.store'
        try:
            if os.path.exists(savePath):
                SystemUtils.remove(savePath, throwError=True)
        except Exception, err:
            self.mainWindow.appendStatus(
                self, u'<span style="color:#CC3333">ERROR: Unable to access database save location.</span>')
            self.mainWindow.showStatusDone(self)
            return

        try:
            SystemUtils.move(sourcePath, savePath)
        except Exception, err:
            self.mainWindow.appendStatus(
                self, u'<span style="color:#CC3333;">ERROR: Unable to modify existing database file.</span>')
            self.mainWindow.showStatusDone(self)
            return

        try:
            SystemUtils.copy(path, sourcePath)
        except Exception, err:
            SystemUtils.move(savePath, sourcePath)
            self.mainWindow.appendStatus(
                self, u'<span style="color:#CC3333;">ERROR: Unable to copy new database file.</span>')
            self.mainWindow.showStatusDone(self)
            return

        if os.path.exists(savePath):
            SystemUtils.remove(savePath)

        self.mainWindow.appendStatus(self, u'<span style="color:#33CC33;">Database Replaced</span>')
        self.mainWindow.showStatusDone(self)
