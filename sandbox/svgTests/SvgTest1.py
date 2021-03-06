# SvgTest.py
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
siteMap = session.query(model).filter(model.index == 17).first()
drawing = CadenceDrawing('CRO_510_index_17_test_rot.svg', siteMap)

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

#==================================================================================================
#  CREATE A GROUP CONTAINING A CIRCLE, SHOWING HOW TO 'USE' (INSTANCE) IT SCALED

drawing.createGroup('rect')
drawing.rect((50, 0),
             100,
             4,
             scene=False,
             groupId='rect')

drawing.createGroup('rect2')
drawing.rect((0, 0),
             -200,
             100,
             scene=False,
             groupId='rect2')


drawing.createGroup('circ')
drawing.circle((0, 0),
               50,
               scene=False,
               groupId='circ',
               fill='none',
               stroke='blue',
               stroke_width=2)

drawing.use('rect', (0, 0), scene=True, fill='yellow', scale=1, scaleY=1)
drawing.use('rect', (0, 0), scene=True, fill='red', scale=1, scaleY=1, rotation=45)
#drawing.use('rect2', (0, 0), scene=True, fill='red', scale=1, scaleY=1)
drawing.use('circ', (0, 0), scene=True, rotation=0, scale=2, scaleY=2, fill='none', stroke='blue')

#drawing.use('rect',  (1000, -100), scene=True, fill='yellow', scale=1, scaleY=1, rotation=0.0)
#drawing.use('rect2', (1000, -1000), scene=True, fill='yellow', scale=1, scaleY=1)
#drawing.use('circ',  (1000, -1000), scene=True, rotation=0, scale=1, scaleY=1, fill='none', stroke='blue')

#==================================================================================================

drawing.grid(size=10, stroke='red')
drawing.circle((0,0), 5, fill='none', stroke='red')
drawing.federalCoordinates()

drawing.save(toPDF=True)
session.close()
print 'Test Complete'
