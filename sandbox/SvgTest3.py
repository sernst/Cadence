# SvgTest3.py
# (C)2012-2014
# Kent A. Stevens and Scott Ernst
# test of CadenceDrawing and Tracks_SiteMap

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
from cadence.svg.CadenceDrawing import CadenceDrawing

model   = Tracks_SiteMap.MASTER
session = model.createSession()
siteMap = session.query(model).filter(model.index == 13).first()
drawing = CadenceDrawing('test3.svg', siteMap)

xFed   = siteMap.xFederal
yFed   = siteMap.yFederal
fMap   = (xFed, yFed)
fScene = drawing.projectToScene((xFed, yFed))
xScene = fScene[0]
yScene = fScene[1]

print "siteMap.index = %s and siteMap.name = %s" % (siteMap.index, siteMap.filename)
print 'in siteMap, xFederal = %s and yFederal = %s' % fMap
print 'in scene, xFederal = %s and yFederal = %s' % (xScene, yScene)

pScene = drawing.projectToMap((xScene, yScene))

print 'and back again, to siteMap, p = (%s, %s)' % pScene

print 'scaling to scene, siteMap.xFederal maps to %s' % drawing.scaleToScene(xFed)
print 'and this maps back to %s' % drawing.scaleToMap(drawing.scaleToScene(xFed))

# place a circle of radius 5 at (10.0, 10.0) in scene coordinates
drawing.circle((10, 10), 5, fill='none')

drawing.line((100,100), (200, 100), scene=True, stroke='red', stroke_width=4)

# label it with text at (20, 10)
drawing.text("circle of radius 5", (20, 10), scene=True)

# now place another circle and rect in map coordinates (not scene coordinates) at the federal marker
drawing.rect((xFed + 40, yFed), 20, 20, fill='none', scene=False)

drawing.grid

# done
drawing.save(toPDF=True)

session.close()

print 'Test Complete'
