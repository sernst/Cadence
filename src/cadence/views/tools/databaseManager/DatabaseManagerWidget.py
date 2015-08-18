# DatabaseManagerWidget.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os

from pyaid.file.FileUtils import FileUtils
from pyaid.OsUtils import OsUtils
from pyaid.string.StringUtils import StringUtils
from pyaid.system.SystemUtils import SystemUtils
from pyglass.elements.PyGlassElementUtils import PyGlassElementUtils
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager
from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.data.SitemapImporterRemoteThread import SitemapImporterRemoteThread
from cadence.data.TrackExporterRemoteThread import TrackExporterRemoteThread
from cadence.enums.UserConfigEnum import UserConfigEnum
from cadence.data.TrackImporterRemoteThread import TrackImporterRemoteThread
from cadence.models.tracks.Tracks_Track import Tracks_Track

#_______________________________________________________________________________
class DatabaseManagerWidget(PyGlassWidget):
    """ User interface class for handling track data IO from any of the possible sources and
        saving them to, or loading them from the database. """

#===============================================================================
#                                                                                       C L A S S

    _OVERWRITE_IMPORT_SUFFIX = '_OVERWRITE_IMPORT'

    RESOURCE_FOLDER_PREFIX = ['tools']

#_______________________________________________________________________________
    def __init__(self, parent, **kwargs):
        super(DatabaseManagerWidget, self).__init__(parent, **kwargs)

        self._thread = None

        self.importCsvBtn.clicked.connect(self._handleImport)
        self.exportBtn.clicked.connect(self._handleExport)
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

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _activateWidgetDisplayImpl(self, **kwargs):
        pass

#===============================================================================
#                                                                                 H A N D L E R S

#_______________________________________________________________________________
    def _handleImport(self):
        label = u'CSV'
        importType = TrackImporterRemoteThread.CSV

        self.mainWindow.showLoading(
            self,
            u'Browsing for Track File',
            u'Choose the %s file to import into the database' % label)

        path = PyGlassBasicDialogManager.browseForFileOpen(
            parent=self,
            caption=u'Select %s File to Import' % label,
            defaultPath=self.mainWindow.appConfig.get(UserConfigEnum.LAST_BROWSE_PATH) )

        self.mainWindow.hideLoading(self)
        if not path or not StringUtils.isStringType(path):
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
            compressed=False
        ).execute(
            callback=self._handleImportComplete,
            logCallback=self._handleImportStatusUpdate )

#_______________________________________________________________________________
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

        if not path or not StringUtils.isStringType(path):
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

#_______________________________________________________________________________
    def _sitemapImportComplete(self, event):
        self.mainWindow.showStatusDone(self)

#_______________________________________________________________________________
    def _handleImportStatusUpdate(self, event):
        self.mainWindow.appendStatus(self, event.get('message'))

#_______________________________________________________________________________
    def _handleImportComplete(self, event):
        actionType = 'Export' if isinstance(self._thread, TrackExporterRemoteThread) else 'Import'

        if not event.target.success:
            print('ERROR: %s Failed' % actionType)
            print('  OUTPUT:', event.target.output)
            print('  ERROR:', event.target.error)
            PyGlassBasicDialogManager.openOk(
                parent=self,
                header='ERROR',
                message='%s operation failed' % actionType)
        else:
            PyGlassBasicDialogManager.openOk(
                parent=self,
                header='Success',
                message='%s operation complete' % actionType)

        self.mainWindow.showStatusDone(self)

#_______________________________________________________________________________
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

#_______________________________________________________________________________
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

        savePath = '%s.store' % sourcePath
        try:
            if os.path.exists(savePath):
                SystemUtils.remove(savePath, throwError=True)
        except Exception as err:
            self.mainWindow.appendStatus(
                self, u'<span style="color:#CC3333">ERROR: Unable to access database save location.</span>')
            self.mainWindow.showStatusDone(self)
            return

        try:
            SystemUtils.move(sourcePath, savePath)
        except Exception as err:
            self.mainWindow.appendStatus(
                self, u'<span style="color:#CC3333;">ERROR: Unable to modify existing database file.</span>')
            self.mainWindow.showStatusDone(self)
            return

        try:
            SystemUtils.copy(path, sourcePath)
        except Exception as err:
            SystemUtils.move(savePath, sourcePath)
            self.mainWindow.appendStatus(
                self, u'<span style="color:#CC3333;">ERROR: Unable to copy new database file.</span>')
            self.mainWindow.showStatusDone(self)
            return

        if os.path.exists(savePath):
            SystemUtils.remove(savePath)

        self.mainWindow.appendStatus(self, u'<span style="color:#33CC33;">Database Replaced</span>')
        self.mainWindow.showStatusDone(self)

#_______________________________________________________________________________
    def _handleMergeComplete(self, event):
        self.mainWindow.showStatusDone(self)

#_______________________________________________________________________________
    def _handleLogMessage(self, event):
        self.mainWindow.appendStatus(self, event.get('message'))
