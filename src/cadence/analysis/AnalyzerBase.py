# AnalyzerBase.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os

from pyaid.config.ConfigsDict import ConfigsDict
from pyaid.debug.Logger import Logger
from pyaid.dict.DictUtils import DictUtils
from pyaid.file.FileUtils import FileUtils
from pyaid.list.ListUtils import ListUtils
from pyaid.system.SystemUtils import SystemUtils

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
from cadence.analysis.AnalysisStage import AnalysisStage

PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.TrackSeries import TrackSeries
from cadence.analysis.Trackway import Trackway
from cadence.enums.SourceFlagsEnum import SourceFlagsEnum
from cadence.enums.TrackPropEnum import TrackPropEnum
from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.models.tracks.Tracks_Track import Tracks_Track

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

#*************************************************************************************************** AnalyzerBase
class AnalyzerBase(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of AnalyzerBase."""
        self._tracksSession = kwargs.get('tracksSession')

        self._cache      = ConfigsDict(kwargs.get('cacheData'))
        self._logger     = kwargs.get('logger')
        self._loadHidden = kwargs.get('loadHidden', False)
        self._tempPath   = kwargs.get('tempPath')
        self._stages     = []
        self._currentStage = None

        self._plotFigures = dict()

        if not self._logger:
            self._logger = Logger(
                name=self,
                logFolder=kwargs.get('logFolderPath'),
                printOut=True,
                headerless=True,
                removeIfExists=True,
                timestampFileSuffix=False)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: stages
    @property
    def stages(self):
        return self._stages

#___________________________________________________________________________________________________ GS: plot
    @property
    def plot(self):
        return plt

#___________________________________________________________________________________________________ GS: logger
    @property
    def logger(self):
        return self._logger

#___________________________________________________________________________________________________ GS: cache
    @property
    def cache(self):
        return self._cache

#___________________________________________________________________________________________________ GS: analysisRootPath
    @property
    def analysisRootPath(self):
        return PyGlassEnvironment.getRootLocalResourcePath('analysis', isDir=True)

#___________________________________________________________________________________________________ GS: tempPath
    @property
    def tempPath(self):
        if not self._tempPath:
            return FileUtils.makeFolderPath(self.analysisRootPath, 'temp')
        return self._tempPath
    @tempPath.setter
    def tempPath(self, value):
        self._tempPath = value


#___________________________________________________________________________________________________ GS: loadHidden
    @property
    def loadHidden(self):
        return self._loadHidden

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ createStage
    def createStage(self, key, **kwargs):
        """createStage doc..."""
        stage = AnalysisStage(key=key, owner=self, **kwargs)
        self.addStage(stage)
        return stage

#___________________________________________________________________________________________________ addStage
    def addStage(self, stage):
        """addStage doc..."""
        if stage in self.stages:
            return
        stage.owner = self
        self.stages.append(stage)

#___________________________________________________________________________________________________ getPath
    def getPath(self, *args, **kwargs):
        """createOutputPath doc..."""
        return FileUtils.createPath(self.analysisRootPath, self.__class__.__name__, *args, **kwargs)

#___________________________________________________________________________________________________ getTempPath
    def getTempPath(self, *args, **kwargs):
        """getTempPath doc..."""
        return FileUtils.createPath(self.tempPath, *args, **kwargs)

#___________________________________________________________________________________________________ run
    def run(self):
        """run doc..."""
        myRootPath = self.getPath(isDir=True)
        if not os.path.exists(myRootPath):
            os.makedirs(myRootPath)

        tempPath = self.tempPath
        if os.path.exists(tempPath):
            SystemUtils.remove(tempPath)
        os.makedirs(tempPath)

        if not self.logger.loggingPath:
            self.logger.loggingPath = myRootPath

        try:
            self._preAnalyze()
            for stage in self._stages:
                print('#--- RUNNING STAGE "%s" ---#' % stage.key)
                self._currentStage = stage
                stage.analyze()
            self._currentStage = None
            self._postAnalyze()
        except Exception as err:
            self.logger.writeError([
                '[ERROR]: Failed to execute analysis',
                'STAGE: %s' % self._currentStage], err)

        self._cleanup()
        SystemUtils.remove(tempPath)

#___________________________________________________________________________________________________ createFigure
    def createFigure(self, key, subplotX =1, subPlotY =1, **kwargs):
        """createFigure doc..."""
        result = plt.subplots(subplotX, subPlotY, **kwargs)
        self._plotFigures[key] = plt.gcf()
        return result[0]

#___________________________________________________________________________________________________ getFigure
    def getFigure(self, key):
        """createFigure doc..."""
        if key in self._plotFigures:
            return self._plotFigures[key]
        return None

#___________________________________________________________________________________________________ savePlotFile
    def saveFigure(self, key, path, close =True, **kwargs):
        """savePlotFile doc..."""
        if not plt or key not in self._plotFigures:
            return False

        figure = self._plotFigures[key]

        if 'orientation' not in kwargs:
            kwargs['orientation'] = 'landscape'

        figure.savefig(path, **kwargs)
        if close:
            plt.close(figure)
            del self._plotFigures[key]

#___________________________________________________________________________________________________ getTracksSession
    def getTracksSession(self):
        """getTracksSession doc..."""
        if self._tracksSession is None:
            self._tracksSession = Tracks_SiteMap.createSession()
        return self._tracksSession

#___________________________________________________________________________________________________ closeTracksSession
    def closeTracksSession(self, commit =True):
        """closeTracksSession doc..."""
        if not self._tracksSession:
            return

        if commit:
            self._tracksSession.commit()
        self._tracksSession.close()
        self._tracksSession = None

#___________________________________________________________________________________________________ getSitemaps
    def getSitemaps(self):
        model   = Tracks_SiteMap.MASTER
        session = self.getTracksSession()
        return session.query(model).all()

#___________________________________________________________________________________________________ getTrackSeries
    @classmethod
    def getTrackSeries(cls, sitemap, loadHidden =False, loadIncomplete =False):
        """getTrackSeries doc..."""
        series  = dict()
        model   = Tracks_Track.MASTER
        column  = getattr(model, TrackPropEnum.SOURCE_FLAGS.name)
        query   = sitemap.getTracksQuery()

        if not loadIncomplete:
            query = query.filter(column.op('&')(SourceFlagsEnum.COMPLETED) == 1)

        if not loadHidden:
            query = query.filter(model.hidden == False)
        result = query.all()

        for track in result:
            fingerprint = track.trackSeriesFingerprint
            if not fingerprint in series:
                series[fingerprint] = TrackSeries(sitemap=sitemap)

            s = series[fingerprint]
            if track.hidden:
                s.hiddenTracks.append(track)
            else:
                s.tracks.append(track)

        out = []
        for n, s in DictUtils.iter(series):
            s.sort()
            out.append(s)

        ListUtils.sortObjectList(out, 'fingerprint', inPlace=True)
        return out

#___________________________________________________________________________________________________ getTrackways
    @classmethod
    def getTrackways(cls, sitemap, loadHidden =False, loadIncomplete =False):
        """getTrackways doc..."""

        trackways = dict()
        for series in cls.getTrackSeries(sitemap, loadHidden, loadIncomplete):
            firstTrack = series.tracks[0] if series.tracks else series.hiddenTracks[0]
            fingerprint = firstTrack.trackwayFingerprint
            if fingerprint not in trackways:
                trackways[fingerprint] = Trackway(sitemap=sitemap, fingerprint=fingerprint)
            if not trackways[fingerprint].addSeries(series, allowReplace=False):
                raise ValueError('Ambiguous track series encountered in trackway %s' % fingerprint)

        out = []
        for n, v in DictUtils.iter(trackways):
            out.append(v)

        ListUtils.sortObjectList(out, 'fingerprint', inPlace=True)
        return out

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    # noinspection PyMethodMayBeStatic
    def _preAnalyze(self):
        """_preAnalyze doc..."""
        pass

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        pass

#___________________________________________________________________________________________________ _cleanup
    def _cleanup(self):
        """_cleanup doc..."""
        pass

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

