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
drawing = CadenceDrawing('test0.svg', siteMap)

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
drawing.circle((10, 10), 5)

# label it with text at (20, 10)
drawing.text("circle of radius 5", (20, 10), scene=True)

# now place another circle and rect in map coordinates (not scene coordinates) at the federal marker
drawing.rect((xFed + 40, yFed), 20, 20, scene=False)

# and another smaller one at (10, 20) in map coordinates
drawing.rect((10, 20), 4, 8, scene=False)

# and test out polyLine
xc = 50
yc = 50

points = (
    (xc - 50, yc -50),
    (xc + 50, yc - 50),
    (xc + 50, yc + 50),
    (xc - 50, yc + 50),
    (xc - 50, yc - 50))

drawing.polyLine(points)

# done
drawing.save()

# Don't forget to always close the session at the end in order to release the database lock
session.close()

print 'Test Complete'

# #___________________________________________________________________________________________________
#
# def basic_shapes(name):
#
#     # make a drawing
#     dwg = svgwrite.Drawing(filename=name, debug=True)
#
#     # add a group with the name hlines and assign it to a variable of the same name, note.
#     hlines = dwg.add(dwg.g(id='hlines', stroke='green'))
#
#     #add lines to that group (within the drawing dwg)
#     for y in range(20):
#         hlines.add(dwg.line(start=(2*cm, (2+y)*cm), end=(18*cm, (2+y)*cm)))
#
#     # make another group, this one called vlines
#     vlines = dwg.add(dwg.g(id='vline', stroke='blue'))
#
#     # and add lines to it also
#     for x in range(17):
#         vlines.add(dwg.line(start=((2+x)*cm, 2*cm), end=((2+x)*cm, 21*cm)))
#
#     # next make a third group called shapes (again note the group name is the same as the variable)
#     shapes = dwg.add(dwg.g(id='shapes', fill='red'))
#
#     # set presentation attributes at object creation as SVG-Attributes
#     shapes.add(dwg.circle(center=(15*cm, 8*cm), r='2.5cm', stroke='blue',
#                           stroke_width=3))
#
#     # override the 'fill' attribute of the parent group 'shapes'
#     shapes.add(dwg.rect(insert=(5*cm, 5*cm), size=(45*mm, 45*mm),
#                         fill='blue', stroke='red', stroke_width=3))
#
#     # or set presentation attributes by helper functions of the Presentation-Mixin
#     ellipse = shapes.add(dwg.ellipse(center=(10*cm, 15*cm), r=('5cm', '10mm')))
#     ellipse.fill('green', opacity=0.5).stroke('black', width=5).dasharray([20, 20])
#     dwg.save()