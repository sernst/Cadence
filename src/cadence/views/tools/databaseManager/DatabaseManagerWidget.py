# DatabaseManagerWidget.py
# (C)2013-2014
# Scott Ernst

import os

from pyaid.file.FileUtils import FileUtils
from pyaid.OsUtils import OsUtils
from pyaid.system.SystemUtils import SystemUtils
from pyglass.elements.PyGlassElementUtils import PyGlassElementUtils
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager
from pyglass.widgets.PyGlassWidget import PyGlassWidget
from cadence.data.SitemapImporterRemoteThread import SitemapImporterRemoteThread

from cadence.data.TrackExporterRemoteThread import TrackExporterRemoteThread
from cadence.data.TrackMergeRemoteThread import TrackMergeRemoteThread
from cadence.enum.UserConfigEnum import UserConfigEnum
from cadence.data.TrackImporterRemoteThread import TrackImporterRemoteThread
from cadence.models.tracks.Tracks_Track import Tracks_Track

#___________________________________________________________________________________________________ DatabaseManagerWidget
class DatabaseManagerWidget(PyGlassWidget):
    """ User interface class for handling track data IO from any of the possible sources and
        saving them to, or loading them from the database. """

#===================================================================================================
#                                                                                       C L A S S

    _OVERWRITE_IMPORT_SUFFIX = '_OVERWRITE_IMPORT'

    RESOURCE_FOLDER_PREFIX = ['tools']

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(DatabaseManagerWidget, self).__init__(parent, **kwargs)

        self._thread = None

        self.importCsvBtn.clicked.connect(self._handleImport)
        self.importJsonBtn.clicked.connect(self._handleImport)
        self.exportBtn.clicked.connect(self._handleExport)
        self.mergeBtn.clicked.connect(self._handleMerge)
        self.sitemapImportBtn.clicked.connect(self._handleImportSitemaps)
        self.databaseReplaceBtn.clicked.connect(self._handleReplaceDatabase)

        PyGlassElementUtils.registerCheckBox(
            self, self.verboseDisplayCheck,
            configSetting=UserConfigEnum.VERBOSE_IO_DISPLAY)
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

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _activateWidgetDisplayImpl
    def _activateWidgetDisplayImpl(self, **kwargs):
        pass

#===================================================================================================
#                                                                                 H A N D L E R S

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
            UserConfigEnum.LAST_BROWSE_PATH, FileUtils.getDirectoryOf(path) )

        self.mainWindow.showStatus(
            self,
            u'Importing Tracks',
            u'Reading track information into database')

        TrackImporterRemoteThread(
            parent=self,
            path=path,
            verbose=self.verboseDisplayCheck.isChecked(),
            importType=importType,
            compressed=self.importCompressCheck.isChecked()
        ).execute(
            callback=self._handleImportComplete,
            logCallback=self._handleImportStatusUpdate )

#___________________________________________________________________________________________________ _handleImportSitemaps
    def _handleImportSitemaps(self):


        self.mainWindow.showLoading(
            self,
            u'Browsing for Sitemap File',
            u'Choose the Sitemap CSV file to import into the database')

        path = PyGlassBasicDialogManager.browseForFileOpen(
            parent=self,
            caption=u'Select CSV File to Import',
            defaultPath=self.mainWindow.appConfig.get(UserConfigEnum.LAST_BROWSE_PATH) )

        self.mainWindow.hideLoading(self)

        if not path or not isinstance(path, basestring):
            self.mainWindow.toggleInteractivity(True)
            return

        # Store directory location as the last active directory
        self.mainWindow.appConfig.set(
            UserConfigEnum.LAST_BROWSE_PATH, FileUtils.getDirectoryOf(path) )

        self.mainWindow.showStatus(
            self,
            u'Importing Sitemaps',
            u'Reading sitemap information into database')

        SitemapImporterRemoteThread(
            parent=self,
            path=path
        ).execute(
            callback=self._sitemapImportComplete,
            logCallback=self._handleImportStatusUpdate)

#___________________________________________________________________________________________________ _sitemapImportComplete
    def _sitemapImportComplete(self, response):
        self.mainWindow.showStatusDone(self)

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

#___________________________________________________________________________________________________ _handleMerge
    def _handleMerge(self):

        result = PyGlassBasicDialogManager.openYesNo(
            self,
            u'Are You Sure?',
            u'Merging this database will overwrite existing storage values for all tracks.',
            False,
            u'Confirm Merge?')

        if not result:
            return

        self.mainWindow.showStatus(
            self,
            u'Merging Database',
            u'Changes to tracks are being applied to the storage entries')

        thread = TrackMergeRemoteThread(self, None)
        thread.execute(self._handleMergeComplete, self._handleLogMessage)

#___________________________________________________________________________________________________ _handleMergeComplete
    def _handleMergeComplete(self, response):
        self.mainWindow.showStatusDone(self)

#___________________________________________________________________________________________________ _handleLogMessage
    def _handleLogMessage(self, message):
        self.mainWindow.appendStatus(self, message)
