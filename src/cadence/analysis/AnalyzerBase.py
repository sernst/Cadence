# AnalyzerBase.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os

from pyglass.alembic.AlembicUtils import AlembicUtils
import sqlalchemy as sqla
from pyaid.config.ConfigsDict import ConfigsDict
from pyaid.config.SettingsConfig import SettingsConfig
from pyaid.debug.Logger import Logger
from pyaid.file.FileUtils import FileUtils
from pyaid.string.StringUtils import StringUtils
from pyaid.system.SystemUtils import SystemUtils
from pyaid.time.TimeUtils import TimeUtils
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

import cadence.models.tracks as tracks
headRevision = AlembicUtils.getHeadDatabaseRevision(databaseUrl=tracks.DATABASE_URL)
myRevision = AlembicUtils.getCurrentDatabaseRevision(databaseUrl=tracks.DATABASE_URL)
tracksStamp = '[TRACKS]: %s [HEAD %s]' % (myRevision, headRevision)

import cadence.models.analysis as analysis
headRevision = AlembicUtils.getHeadDatabaseRevision(databaseUrl=analysis.DATABASE_URL)
myRevision = AlembicUtils.getCurrentDatabaseRevision(databaseUrl=analysis.DATABASE_URL)
analysisStamp = '[ANALYSIS]: %s [HEAD %s]' % (myRevision, headRevision)

from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.models.analysis.Analysis_Sitemap import Analysis_Sitemap

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None
    print('WARNING: Matplotlib failed to import.')

#*************************************************************************************************** AnalyzerBase
class AnalyzerBase(object):
    """ The abstract base class for all Cadence Analyzers. Each Analyzer acts as a container
        around one or more AnalysisStage instances and provide these stage objects with the
        common functionality for that particular Analyzer."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """ Creates a new instance of AnalyzerBase.

            [cacheData] ~ Object | CacheData
                A caching object on which to store data during analysis at the analyzer level,
                instead of the stage level.

            [logger] ~ Logger
                A logger object to use for logging within this analyzer. If no such logger exists,
                a new logger is created.

            [logFolderPath] ~ String
                If no logger was specified for the analyzer, this is the absolute path to the
                folder where the log file should be written. This value is ignored if you specify
                a logger. """

        self._tracksSession     = None
        self._analysisSession   = None
        self._cache             = ConfigsDict(kwargs.get('cacheData'))
        self._logger            = kwargs.get('logger')
        self._tempPath          = kwargs.get('tempPath')
        self._stages            = []
        self._sitemaps          = []
        self._trackways         = dict()
        self._seriesBundles       = dict()
        self._plotFigures       = dict()
        self._currentStage      = None
        self._success           = False
        self._errorMessage      = None
        self._startTime         = None

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

#___________________________________________________________________________________________________ GS: elapsedTime
    @property
    def elapsedTime(self):
        if not self._startTime:
            return 0
        return TimeUtils.getElapsedTime(
            startDateTime=self._startTime,
            endDateTime=TimeUtils.getNowDatetime(),
            toUnit=TimeUtils.MILLISECONDS)

#___________________________________________________________________________________________________ GS: success
    @property
    def success(self):
        return self._success

#___________________________________________________________________________________________________ GS: errorMessage
    @property
    def errorMessage(self):
        return self._errorMessage

#___________________________________________________________________________________________________ GS: sitemapFilters
    @property
    def sitemapFilters(self):
        """ A list of sitemap filtering strings, which match the beginning of the sitemap name,
            e.g. ["BEB", "TCH"]. This value is loaded from the analysis.json file with the
            'SITEMAP_FILTERS' key. """

        return self._settings.get('SITEMAP_FILTERS', [])

#___________________________________________________________________________________________________ GS: plotFigures
    @property
    def plotFigures(self):
        """ A dictionary containing the currently open (in the background) PyPlot figures. """
        return self._plotFigures

#___________________________________________________________________________________________________ GS: stages
    @property
    def stages(self):
        """ A list of the analyzer stages that make up the analysis process of this Analyzer. """
        return self._stages

#___________________________________________________________________________________________________ GS: plot
    @property
    def plot(self):
        """ A convenience reference to Matplotlib's PyPlot module. Included here so Analyzers do
            not have to handle failed Matplotlib loading internally. """

        return plt

#___________________________________________________________________________________________________ GS: logger
    @property
    def logger(self):
        """ The logging object for the Analyzer. """
        return self._logger

#___________________________________________________________________________________________________ GS: cache
    @property
    def cache(self):
        """ The shared CacheData instance for the analyzer. """
        return self._cache

#___________________________________________________________________________________________________ GS: analysisRootPath
    @property
    def analysisRootPath(self):
        """ The root folder path where all analyses are stored. This is a top-level directory that
            should not be accessed directly unless absolutely necessary. In most cases you should
            use the outputPath property instead. """

        return self._settings.fetch('OUTPUT_PATH', self._defaultRootPath)

#___________________________________________________________________________________________________ GS: outputRootPath
    @property
    def outputRootPath(self):
        """ The root folder where analysis output files for this particular Analyzer should be
            stored. This path represents a folder within the analysisRootPath property specific
            to this analyzer. """

        return FileUtils.makeFolderPath(self.analysisRootPath, self.__class__.__name__)

#___________________________________________________________________________________________________ GS: tempPath
    @property
    def tempPath(self):
        """ The root folder path where all temporary files created during analysis should be stored.
            This path is created on demand and always removed at the end of the analysis process,
            even if the process is aborted by an error in an analysis stage. """

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
        """ Returns the analysis stage associated with the specified key or None if no such stage
            exists. """

        for stage in self._stages:
            if stage.key == key:
                return stage
        return None

#___________________________________________________________________________________________________ addStage
    def addStage(self, stage):
        """ Appends the specified stage to this instances stage list if it is not already in the
            list at another location. """

        if stage in self.stages:
            return
        stage.owner = self
        self.stages.append(stage)

#___________________________________________________________________________________________________ getPath
    def getPath(self, *args, **kwargs):
        """ Convenience method for creating paths relative to the output root path for this
            Analyzer. """

        return FileUtils.createPath(self.outputRootPath, *args, **kwargs)

#___________________________________________________________________________________________________ getTempFilePath
    def getTempFilePath(self, name =None, extension =None, *args):
        """ Used to create a temporary file path within this instance's temporary folder.
            Any file on this path will be automatically removed at the end of the analysis
            process.

            [name] :: String :: None
                The desired file name for the desired file within the temporary directory. If no
                name is specified, a name will be created automatically using the current time
                (microsecond) and a 16 digit random code for a very low probability of collisions.

            [extension] :: String :: None
                Specifies the extension to add to this file. The file name is not altered if no
                extension is specified.

            [*args] :: [String] :: []
                A list of relative folder prefixes in which the file should reside. For example,
                if you wish to have a file 'bar' in a folder 'foo' then you would specify 'foo' as
                the single arg to get a file located at 'foo/bar' within the temporary file. No
                directory prefixes will be created within this method. """

        if not name:
            name = TimeUtils.getUidTimecode(suffix=StringUtils.getRandomString(16))
        if extension:
            extension = '.' + extension.strip('.')
            if not name.endswith(extension):
                name += extension

        args = list(args) + [name]
        return FileUtils.makeFilePath(self.tempPath, *args)

#___________________________________________________________________________________________________ getTempPath
    def getTempPath(self, *args, **kwargs):
        """ Creates a path relative to this instance's root temporary path. Uses the
            FileUtils.createPath() format for args and kwargs. """

        return FileUtils.createPath(self.tempPath, *args, **kwargs)

#___________________________________________________________________________________________________ run
    def run(self):
        """ Executes the analysis process, iterating through each of the analysis stages before
            cleaning up and exiting. """

        print('[OUTPUT PATH]: %s' % self.analysisRootPath)
        print(analysisStamp)
        print(tracksStamp)

        self._startTime = TimeUtils.getNowDatetime()

        myRootPath = self.getPath(isDir=True)
        if os.path.exists(myRootPath):
            FileUtils.emptyFolder(myRootPath)
        if not os.path.exists(myRootPath):
            os.makedirs(myRootPath)

        tempPath = self.tempPath
        if os.path.exists(tempPath):
            SystemUtils.remove(tempPath)
        os.makedirs(tempPath)

        if not self.logger.loggingPath:
            self.logger.loggingPath = myRootPath

        try:
            session = self.getAnalysisSession()
            self._preAnalyze()
            for stage in self._stages:
                self._currentStage = stage
                stage.analyze()
            self._currentStage = None
            self._postAnalyze()

            session.commit()
            session.close()
            self._success = True
        except Exception as err:
            session = self.getAnalysisSession()
            session.close()
            msg = [
                '[ERROR]: Failed to execute analysis',
                'STAGE: %s' % self._currentStage]
            self._errorMessage = Logger.createErrorMessage(msg, err)
            self.logger.writeError(msg, err)

        session = self.getTracksSession()
        session.close()

        self._cleanup()
        SystemUtils.remove(tempPath)

        self.logger.write('\n\n[%s]: %s (%s)' % (
            'SUCCESS' if self._success else 'FAILED',
            self.__class__.__name__,
            TimeUtils.toPrettyElapsedTime(self.elapsedTime)
        ), indent=False)

#___________________________________________________________________________________________________ createFigure
    def createFigure(self, key, subplotX =1, subPlotY =1, **kwargs):
        """ A convenience method for creating a PyPlot figure that is managed by this analyzer. """
        result = plt.subplots(subplotX, subPlotY, **kwargs)
        self._plotFigures[key] = plt.gcf()
        return result[0]

#___________________________________________________________________________________________________ getFigure
    def getFigure(self, key, setActive =True):
        """ Retrieves the managed PyPlot figure for the specified key if such a figure exists. """
        if key in self._plotFigures:
            out = self._plotFigures[key]
            if setActive:
                plt.figure(out.number)
        return None

#___________________________________________________________________________________________________ closeFigure
    def closeFigure(self, key):
        """ Closes the managed figure specified by its key if such a figure exists. """
        if key not in self._plotFigures:
            return

        figure = self._plotFigures[key]
        plt.close(figure)
        del self._plotFigures[key]

#___________________________________________________________________________________________________ savePlotFile
    def saveFigure(self, key, path =None, close =True, **kwargs):
        """ Saves the specified figure to a file at teh specified path.

            key :: String
                The key for the figure to be saved. If no such key exists, the method will return
                false.

            path :: String :: None
                The absolute file location to where the figure should be saved. If no path is
                specified the file will be saved as a pdf in this Analyzer's temporary folder.

            close :: Boolean :: True
                If true, the figure will be closed upon successful completion of the save process.

            [kwargs]
                Data to be passed directly to the PyPlot Figure.savefig() method, which can be
                used to further customize how the figure is saved. """

        if not plt or key not in self._plotFigures:
            return False

        if not path:
            path = self.getTempPath('%s-%s.pdf' % (
                key, TimeUtils.getUidTimecode(suffix=StringUtils.getRandomString(16))), isFile=True)

        figure = self._plotFigures[key]

        if 'orientation' not in kwargs:
            kwargs['orientation'] = 'landscape'

        figure.savefig(path, **kwargs)
        if close:
            self.closeFigure(key)
        return path

#___________________________________________________________________________________________________ getAnalysisSession
    def getAnalysisSession(self):
        """ Returns a managed session to the analysis database. Used for shared session access
            across analysis stages, which is used to increase performance by eliminating the
            overhead in loading large segments of the database multiple times. """

        if self._analysisSession is None:
            self._analysisSession = Analysis_Sitemap.MASTER.createSession()
        return self._analysisSession

#___________________________________________________________________________________________________ getTracksSession
    def getTracksSession(self):
        """ Returns a managed session to the tracks database. Used for shared session access across
            analysis stages, which is used to increase performance by eliminating the overhead in
            loading large segments of the database multiple times. """

        if self._tracksSession is None:
            self._tracksSession = Tracks_SiteMap.MASTER.createSession()
        return self._tracksSession

#___________________________________________________________________________________________________ closeTracksSession
    def closeTracksSession(self, commit =False):
        """ Closes the shared track database session. By default no commit is made because the
            analyzers should not be writing to the tracks database. """

        if not self._tracksSession:
            return

        if commit:
            self._tracksSession.commit()
        self._tracksSession.close()
        self._tracksSession = None

#___________________________________________________________________________________________________ getSitemaps
    def getSitemaps(self):
        """ Retrieves a list of sitemap model instances from the tracks database for use in
            analysis. These sitemaps are cached for the remainder of the analysis process for
            data persistence and performance reasons. """

        if self._sitemaps:
            return self._sitemaps

        model   = Tracks_SiteMap.MASTER
        session = self.getTracksSession()
        query   = session.query(model)

        # If filters exist for sitemaps then create a collection of OR clauses to only load
        # sitemaps that match the filter list.
        orFilters = []
        for sf in self.sitemapFilters:
            sf = sf.split('.')[0]
            orFilters.append(model.name.like('%s%%' % sf.upper()))
        if orFilters:
            query = query.filter(sqla.or_(*orFilters))

        self._sitemaps = query.all()
        return self._sitemaps

#___________________________________________________________________________________________________ getTrackways
    def getTrackways(self, sitemap):
        """ Retrieves a list of trackway model instances for the specified sitemap. These trackways
            are cached for data persistence and performance reasons. """

        if sitemap.uid in self._trackways:
            return self._trackways[sitemap.uid]

        trackways = sitemap.getTrackways()
        self._trackways[sitemap.uid] = trackways
        return trackways

#___________________________________________________________________________________________________ getSeriesBundle
    def getSeriesBundle(self, trackway):
        """ Retrieves a list of TrackSeries instances for the specified trackway. These series are
            cached for data persistence and performance reasons. """

        if trackway.uid in self._seriesBundles:
            return self._seriesBundles[trackway.uid]

        bundle = trackway.getTrackSeries()
        self._seriesBundles[trackway.uid] = bundle
        return bundle

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    # noinspection PyMethodMayBeStatic
    def _preAnalyze(self):
        """ A pre-analysis hook method that is called just prior to executing the first
            AnalysisStage and can be overridden to customize the analyzer prior to that phase
            of the run() method. """

        pass

#___________________________________________________________________________________________________ _postAnalyze
    # noinspection PyMethodMayBeStatic
    def _postAnalyze(self):
        """ A post-analysis hook method that is called just after the final AnalysisStage finishes
            execution. This method can be overridden to customize the post analysis behavior before
            the cleanup process. """

        pass

#___________________________________________________________________________________________________ _cleanup
    # noinspection PyMethodMayBeStatic
    def _cleanup(self):
        """ A hook method called in the final stages of the run() method after all analysis is
            complete, and should be overridden if this Analyzer creates any non-standard transient
            data during its lifetime. Also, this method will be called even if an AnalysisStage
            aborts due to an exception, so this method should be hardened against exceptions
            caused by incomplete run execution. """

        pass

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__

