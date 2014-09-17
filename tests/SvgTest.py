# SvgTest.py
# (C)2012-2014
# Kent A. Stevens and Scott Ernst
# test of SvgWriter and Tracks_SiteMap

#---------------------------------------------------------------------------------------------------
# INITIALIZE PYGLASS ENVIRONMENT
#       When running outside of a PyGlass application, the PyGlass environment must be initialized
#       explicitly, including specifying the relationship between the run script (this file) and
#       the resource directory. This must be done before importing database classes so that the
#       database import correctly locates the database file and initializes the model classes to
#       that file.

from pyaid.file.FileUtils import FileUtils
from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

location = FileUtils.getDirectoryOf(__file__)

PyGlassEnvironment.initializeExplicitAppSettings(
    FileUtils.createPath(location, '..', 'resources', isDir=True),
    FileUtils.createPath(location, '..', 'resources', 'local', isDir=True) )

#---------------------------------------------------------------------------------------------------
# RUN TEST SCRIPT

from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.svg.SvgWriter import SvgWriter

model   = Tracks_SiteMap.MASTER
session = model.createSession()
siteMap = session.query(model).filter(model.index == 1).first()

print "map.index = %s and map.name = %s" % (siteMap.index, siteMap.filename)

writer = SvgWriter('test.svg', map)
writer.rect(10, 10, 4, 4)
writer.circle(20, 10, 4)
writer.ellipse(40, 10, 2, 4)
writer.text("test", 60, 10)
writer.save()

# Don't forget to always close the session at the end to release the database lock
session.close()

print 'Test Complete'
