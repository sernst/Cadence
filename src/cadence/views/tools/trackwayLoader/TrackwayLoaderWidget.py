# TrackwayLoaderWidget.py
# (C)2013-2014
# Scott Ernst

import sqlalchemy as sqla
from PySide import QtGui
from pyglass.dialogs.PyGlassBasicDialogManager import PyGlassBasicDialogManager
from pyglass.elements.DataListWidgetItem import DataListWidgetItem
from pyglass.widgets.PyGlassWidget import PyGlassWidget

from cadence.data.TrackLinkageRemoteThread import TrackLinkageRemoteThread
from cadence.enum.TrackPropEnum import TrackPropEnum
from cadence.mayan.trackway.plugin import CreateTrackNodes
from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.util.threading.RunPythonModuleThread import RunPythonModuleThread

#___________________________________________________________________________________________________ TrackwayLoaderWidget
class TrackwayLoaderWidget(PyGlassWidget):
    """ User interface class for handling track data IO from any of the possible sources and
        saving them to, or loading them from the database. """

#===================================================================================================
#                                                                                       C L A S S

    _OVERWRITE_IMPORT_SUFFIX = '_OVERWRITE_IMPORT'

    RESOURCE_FOLDER_PREFIX = ['tools']

#___________________________________________________________________________________________________ __init__
    def __init__(self, parent, **kwargs):
        super(TrackwayLoaderWidget, self).__init__(parent, **kwargs)

        self._thread = None

        self.loadBtn.clicked.connect(self._handleLoadTracks)
        self.updateLinksBtn.clicked.connect(self._handleUpdateLinks)

        self._getLayout(self.filterBox, QtGui.QHBoxLayout, True)
        self._filterList = []
        self._processingFilters = False

        filterDefs = [
            {'enum':TrackPropEnum.SITE,            'label':'Site'},
            {'enum':TrackPropEnum.LEVEL,           'label':'Level'},
            {'enum':TrackPropEnum.SECTOR,          'label':'Sector'},
            {'enum':TrackPropEnum.YEAR,            'label':'Year'},
            {'enum':TrackPropEnum.TRACKWAY_NUMBER, 'label':'Trackway'}]

        index = 0
        for f in filterDefs:
            flBox, flBoxLayout = self._createWidget(self.filterBox, QtGui.QVBoxLayout, True)

            label = QtGui.QLabel(flBox)
            label.setText(f['label'])
            flBoxLayout.addWidget(label)

            fl = QtGui.QListWidget(self)
            fl.itemSelectionChanged.connect(self._handleFilterChange)
            fl.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
            fl.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
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

#___________________________________________________________________________________________________ _getFilteredTracks
    def _getFilteredTracks(self, session):
        model = Tracks_Track.MASTER
        query = session.query(model)

        for filterDef in self._filterList:
            items = filterDef['widget'].selectedItems()
            if not items or items[0].itemData is None:
                continue
            query = query.filter(getattr(model, filterDef['enum'].name) == items[0].itemData)

        # Prevents tracks that have been "hidden" from being loaded into the scene
        # query = query.filter(model.hidden == False)

        return query.all()

#===================================================================================================
#                                                                                 H A N D L E R S

#___________________________________________________________________________________________________ _handleRunIntegrityTests
    def _handleLoadTracks(self):
        self.mainWindow.showLoading(self, u'Loading Tracks')

        session   = Tracks_Track.MASTER.createSession()
        entries   = self._getFilteredTracks(session)
        count     = len(entries)
        trackList = []
        for entry in entries:
            trackList.append(entry.toMayaNodeDict())
        session.close()

        if not trackList:
            self.mainWindow.hideLoading(self)
            return

        thread = RunPythonModuleThread(
            self, CreateTrackNodes, trackList=trackList, runInMaya=True)
        thread.userData = {'count':count}
        thread.execute(callback=self._handleTrackNodesCreated)

#___________________________________________________________________________________________________ _handleTrackNodesCreated
    def _handleTrackNodesCreated(self, event):
        result = event.target.output

        if not result.success:
            PyGlassBasicDialogManager.openOk(
                parent=self, header=u'Load Error', message=u'Unable to load tracks')
        else:
            PyGlassBasicDialogManager.openOk(
                parent=self, header=str(event.target.userData['count']) + ' Tracks Created')

        self.mainWindow.hideLoading(self)

#___________________________________________________________________________________________________ _handleUpdateLinks
    def _handleUpdateLinks(self):

        result = PyGlassBasicDialogManager.openYesNo(
            self,
            u'Confirm Linkages Reset',
            u'Are you sure you want to reset the selected trackway linkages?',
            False)

        if not result:
            return

        session   = Tracks_Track.MASTER.createSession()
        entries   = self._getFilteredTracks(session)

        self.mainWindow.showStatus(
            self,
            u'Resetting Linkages',
            u'Updating linkages to their default values')

        thread = TrackLinkageRemoteThread(parent=self, session=session, tracks=entries)
        thread.userData = session
        thread.execute(
            callback=self._handleLinkagesComplete,
            logCallback=self._handleLinkagesStatusUpdate)

#___________________________________________________________________________________________________ _handleLinkagesComplete
    def _handleLinkagesComplete(self, event):
        session = event.target.userData
        if event.target.success:
            session.commit()
        else:
            session.rollback()
        session.close()

        self.mainWindow.showStatusDone(self)

#___________________________________________________________________________________________________ _handleImportStatusUpdate
    def _handleLinkagesStatusUpdate(self, event):
        self.mainWindow.appendStatus(self, event.get('message'))

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
