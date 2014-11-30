# AnalyzerBase.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os

from pyaid.config.ConfigsDict import ConfigsDict
from pyaid.config.SettingsConfig import SettingsConfig
from pyaid.debug.Logger import Logger
from pyaid.file.FileUtils import FileUtils
from pyaid.string.StringUtils import StringUtils
from pyaid.system.SystemUtils import SystemUtils
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap

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

        self._cache         = ConfigsDict(kwargs.get('cacheData'))
        self._logger        = kwargs.get('logger')
        self._tempPath      = kwargs.get('tempPath')
        self._stages        = []
        self._sitemaps      = []
        self._trackways     = dict()
        self._trackSeries   = dict()
        self._plotFigures   = dict()
        self._currentStage  = None

        if not self._logger:
            self._logger = Logger(
                name=self,
                logFolder=kwargs.get('logFolderPath'),
                printOut=True,
                headerless=True,
                removeIfExists=True,
                timestampFileSuffix=False)

        self._defaultRootPath = PyGlassEnvironment.getRootLocalResourcePath('analysis', isDir=True)

        self._settings = SettingsConfig(
            FileUtils.makeFilePath(self._defaultRootPath, 'analysis.json'), pretty=True)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: plotFigures
    @property
    def plotFigures(self):
        return self._plotFigures

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
        return self._settings.fetch('OUTPUT_PATH', self._defaultRootPath)

#___________________________________________________________________________________________________ GS: tempPath
    @property
    def tempPath(self):
        if not self._tempPath:
            return FileUtils.makeFolderPath(self._defaultRootPath, 'temp')
        return self._tempPath
    @tempPath.setter
    def tempPath(self, value):
        self._tempPath = value

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getStage
    def getStage(self, key):
        """getStage doc..."""
        for stage in self._stages:
            if stage.key == key:
                return stage
        return None

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
        print('[TARGET]: %s' % self.analysisRootPath)

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
    def getFigure(self, key, setActive =True):
        """createFigure doc..."""
        if key in self._plotFigures:
            out = self._plotFigures[key]
            if setActive:
                plt.figure(out.number)
        return None

#___________________________________________________________________________________________________ closeFigure
    def closeFigure(self, key):
        """closeFigure doc..."""
        if key not in self._plotFigures:
            return

        figure = self._plotFigures[key]
        plt.close(figure)
        del self._plotFigures[key]

#___________________________________________________________________________________________________ savePlotFile
    def saveFigure(self, key, path =None, close =True, **kwargs):
        """savePlotFile doc..."""
        if not plt or key not in self._plotFigures:
            return False

        if not path:
            path = self.getTempPath('%s-%s.pdf' % (key, StringUtils.getRandomString(16)), isFile=True)

        figure = self._plotFigures[key]

        if 'orientation' not in kwargs:
            kwargs['orientation'] = 'landscape'

        figure.savefig(path, **kwargs)
        if close:
            self.closeFigure(key)
        return path

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
        if not self._sitemaps:
            model   = Tracks_SiteMap.MASTER
            session = self.getTracksSession()
            self._sitemaps = session.query(model).all()

        return self._sitemaps

#___________________________________________________________________________________________________ getTrackways
    def getTrackways(self, sitemap):
        """getTrackways doc..."""
        if sitemap.uid in self._trackways:
            return self._trackways[sitemap.uid]

        trackways = sitemap.getTrackways()
        self._trackways[sitemap.uid] = trackways
        return trackways

#___________________________________________________________________________________________________ getTrackwaySeries
    def getTrackwaySeries(self, trackway):
        """getTrackSeries doc..."""
        if trackway.uid in self._trackSeries:
            return self._trackSeries[trackway.uid]

        series = trackway.getTrackSeries()
        self._trackSeries[trackway.uid] = series
        return series

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

