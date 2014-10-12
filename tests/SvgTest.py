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
map     = session.query(model).filter(model.index == 14).first()
drawing  = CadenceDrawing('test.svg', map)

fMap = (map.xFederal, map.yFederal)
fScene = drawing.projectToScene([fMap[0], fMap[1]])

print "map.index = %s and map.name = %s" % (map.index, map.filename)
print 'in map, xFederal = %s and yFederal = %s' % fMap
print 'in scene, xFederal = %s and yFederal = %s' % (fScene[0], fScene[1])
print 'and back again, to map, p = %s' % drawing.projectToMap([fScene[0], fScene[1]])

print 'scaling to scene, map.xFederal maps to %s' % drawing.scaleToScene(map.xFederal)
print 'and this maps back to to %s' % drawing.scaleToMap(drawing.scaleToScene(map.xFederal))

#
# #drawing.rect(0, 0, map.width, map.height, sceneCoordinates=False)
#
# #drawing.circle(10.0, 10.0, 5)
# # drawing.text("zero-zero", 10, 10)
# drawing.circle(map.xFederal, map.yFederal, r=4, sceneCoordinates=False)
# # drawing.mark(map.xFederal, map.yFederal, 10)
#
# # drawing.mmLine(500, 500, 550, 550)
# # drawing.line(500, 550, 550, 500)
#
drawing.gridG()
#
# xc = map.xFederal
# yc = map.yFederal
#
# # points = ((xc - 50, yc -50), (xc + 50, yc - 50), (xc + 50, yc + 50), (xc - 50, yc + 50), (xc - 50, yc - 50))
# # drawing.polyLine(points)
drawing.text("fed", [map.xFederal - 100, map.yFederal], scene=False)
drawing.save()

# Don't forget to always close the session at the end to release the database lock
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
#     # make anoher group, this one called vlines
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