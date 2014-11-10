from pyaid.dict.DictUtils import DictUtils
from pyaid.file.FileUtils import FileUtils
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

location = FileUtils.getDirectoryOf(__file__)

PyGlassEnvironment.initializeExplicitAppSettings(
    FileUtils.createPath(location, '..', 'resources', isDir=True),
    FileUtils.createPath(location, '..', 'resources', 'local', isDir=True) )

from cadence.models.tracks.Tracks_Track import Tracks_Track
from cadence.models.tracks.Tracks_TrackStore import Tracks_TrackStore
from cadence.enums.TrackPropEnum import TrackPropEnum

model = Tracks_Track.MASTER
session = model.createSession()

