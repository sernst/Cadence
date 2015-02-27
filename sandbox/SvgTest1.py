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
siteMap = session.query(model).filter(model.index == 13).first()
drawing = CadenceDrawing('testSVG+PDF.svg', siteMap)

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

#===================================================================================================

# place a circle of radius 5 at (100.0, 100.0) in scene coordinates
# drawing.circle((100, 100), 5, scene=True, stroke='red', fill='green')

# label it with text at (100, 10)
drawing.text("circle of radius 5 at (200, 10)", (100, 10), scene=True, stroke='blue')

# now place another circle and rect in map (not scene) coordinates below the federal marker
drawing.rect((xScene, yScene - 100), 4, 10, scene=False, fill='red')

# and another at (100, 200), also in map coordinates
drawing.rect((100, 200), 10, 4, scene=False)

# # and test out polyLine
# xc = 50
# yc = 50
#
# points = (
#     (xc - 50, yc -50),
#     (xc + 50, yc - 50),
#     (xc + 50, yc + 50),
#     (xc - 50, yc + 50),
#     (xc - 50, yc - 50))
#
# drawing.polyLine(points)

#==================================================================================================
#  CREATE A GROUP CONTAINING A RECT, SHOWING HOW TO USE (INSTANCE) IT ROTATED AND TRANSLATED

drawing.createGroup('r1')
drawing.rect((0, 0), 10, 30, scene=False, groupId='r1') # add this rect to the group

drawing.use('r1', (400, 100), rotation=10, fill='blue')
drawing.use('r1', (400, 200), rotation=20, fill='blue')
drawing.use('r1', (400, 300), rotation=30, fill='blue')
drawing.use('r1', (400, 400), rotation=40, fill='blue')
drawing.use('r1', (400, 500), rotation=50, fill='blue')

#==================================================================================================
#  CREATE A GROUP CONTAINING A CIRCLE, SHOWING HOW TO USE (INSTANCE) IT SCALED

drawing.createGroup('g1')
drawing.circle((0, 0), 10,
               scene=False,
               groupId='g1',
               fill='none',
               stroke='blue',
               stroke_width=2) # add this circle to the group

drawing.use('g1', (100, 100), fill='yellow', scale=1, scaleY=1)
drawing.use('g1', (100, 200), fill='yellow', scale=1, scaleY=1.1)
drawing.use('g1', (100, 300), fill='yellow', scale=1, scaleY=1.5)
drawing.use('g1', (100, 400), fill='yellow', scale=1, scaleY=2)
drawing.use('g1', (100, 500), fill='yellow', scale=1, scaleY=.5)

# remember that scene coordinates increase in x to the left, and z upward.

drawing.createGroup('g2')
drawing.circle((0, 0), 10, scene=False, groupId='g2',fill='yellow', stroke='red')

drawing.use('g2', (0,   200), scene=True, scale=1, scaleY=1, rotation=10)
drawing.use('g2', (200, 200), scene=True, scale=1, scaleY=2, rotation=20)
drawing.use('g2', (400, 200), scene=True, scale=1, scaleY=3, rotation=30)
drawing.use('g2', (600, 200), scene=True, scale=1, scaleY=4, rotation=40)
drawing.use('g2', (800, 200), scene=True, scale=1, scaleY=5, rotation=50)
drawing.grid()
#==================================================================================================

drawing.save(toPDF=True)
session.close()
print 'Test Complete'
