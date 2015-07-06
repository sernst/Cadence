# SvgTest4.py
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

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment
PyGlassEnvironment.initializeFromInternalPath(__file__)

#---------------------------------------------------------------------------------------------------
# RUN TEST SCRIPT

import math

from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.svg.CadenceDrawing import CadenceDrawing

model   = Tracks_SiteMap.MASTER
session = model.createSession()
siteMap = session.query(model).filter(model.index == 26).first()
drawing = CadenceDrawing('test.svg', siteMap, labelTracks=False)

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

# create a bar-shaped pointer for map annotation
drawing.createGroup('bar')
drawing.line((0, 0), (0, -20), scene=False, groupId='bar')

# 20 units = 1 m

x = -100
z = 100
lengthRatio   = 0.5
trackLength   = 1.0
trackWidth    = 1.0
trackRotation = 15.0


# place a circle of radius 5 at (10.0, 10.0) in scene coordinates
drawing.circle((10, 10), 5, fill='none')

drawing.line((100,100), (200, 100), scene=True, stroke='red', stroke_width=4)

# label it with text at (20, 10)
drawing.text("circle of radius 5", (20, 10), scene=True)

# now place another circle and rect in map coordinates (not scene coordinates) at the federal marker
drawing.rect((xFed + 40, yFed), 20, 20, fill='none', scene=False)



# now overlay onto the above measured-dimension bars the corresponding length indicators
drawing.use(
            'bar',
            (100, 200),
            scale=1.0,
            scaleY=lengthRatio*trackLength,
            rotation=trackRotation,
            scene=True,
            stroke='red',
            stroke_width=2.0)

# draw the remaining portion of the length bar
drawing.use(
            'bar',
            (100, 200),
            scale=1.0,
            scaleY=(1.0 - lengthRatio)*trackLength,
            rotation=trackRotation + 180.0,
            #rotation=trackRotation + 45.0,
            scene=True,
            stroke='orange',
            stroke_width=2.0)

# and draw a bar representing the width (first drawing that part to the right of center)
drawing.use(
            'bar',
            (100, 200),
            scale=1.0,
            scaleY=trackWidth/2.0,
            rotation=trackRotation + 90.0,
            scene=True,
            stroke='blue',
            stroke_width=4.0)

# then drawing the other part of the width bar that is to the left of center
drawing.use(
            'bar',
            (100, 200),
            scale=1.0,
            scaleY=trackWidth/2.0,
            rotation=trackRotation - 90.0,
            scene=True,
            stroke='green',
            stroke_width=4.0)



# new version

l   = 100*trackLength
w   = 100*trackWidth
rot = math.radians(trackRotation)
z1  = lengthRatio*l
z2  = z1 - l

# draw the length line
drawing.line(
             (x + z1*math.sin(rot), z + z1*math.cos(rot)),
             (x + z2*math.sin(rot), z + z2*math.cos(rot)),
             scene=True,
             stroke='red',
             stroke_width=2.0)

# draw the width line

x1 = w/2.0
x2 = -w/2.0

drawing.line(
             (x + x1*math.cos(rot), z - x1*math.sin(rot)),
             (x + x2*math.cos(rot), z - x2*math.sin(rot)),
             scene=True,
             stroke='blue',
             stroke_width=2.0)

#drawing.federalCoordinates()
# drawing.grid(0.5)

drawing.save(toPDF=True)
session.close()
print 'Test Complete'
