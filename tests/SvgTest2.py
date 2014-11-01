# SvgTest2.py
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
drawing = CadenceDrawing('test.svg', siteMap)

# --------------------------------------------------------------------------------------------------
# THIS DEMONSTRATES MAPPING BETWEEN A SITE MAP THE SCENE, PLUS SIMPLE SHAPES

#
# xFed   = siteMap.xFederal
# yFed   = siteMap.yFederal
# fMap   = (xFed, yFed)
# fScene = drawing.projectToScene((xFed, yFed))
#
# print "siteMap.index = %s and siteMap.name = %s" % (siteMap.index, siteMap.filename)
# print 'in siteMap, the federal marker is (%s, %s)' % fMap
# print 'which projects into the scene as (%s, %s)' % (fScene[0], fScene[1])
# print 'and projecting back to the map gives (%s, %s)' % drawing.projectToMap((fScene[0], fScene[1]))
#
# # place a circle of radius 5 at (10.0, 10.0) in scene coordinates
# drawing.circle((10, 10), 5)
#
# # label it with text at (20, 10)
# drawing.text("circle of radius 5", (20, 10), scene=True)
#
# # now place another circle and rect in map coordinates (not scene coordinates) at the federal marker
# drawing.rect((xFed + 40, yFed), (20, 20), scene=False)
#
# # and another smaller one at (10, 20) in map coordinates
# drawing.rect((10, 20), (4, 8), scene=False)
#
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
# LOAD ALL TRACKS FOR THIS SITE AND DRAW THEM

tracks = siteMap.getAllTracks(session)

print '%s tracks returned' % len(tracks)

for track in tracks:
    x = track.x
    z = track.z

    # The track dimensions stored in the database are in fractional meters, so multiply by
    # 100 to convert to cm.
    r = 100*0.5*(track.width/2.0 + track.length/2.0)

    drawing.circle((x, z), r, scene=True, fill='none', stroke='blue', stroke_width=1)

    # compute the averge uncertainty in cm (also stored in fractional meters)
    u = 100*(track.widthUncertainty + track.lengthUncertainty)/2.0

    drawing.circle((x, z), u, scene=True, fill='red', stroke='red', stroke_width=1)

# done
drawing.save()

# Don't forget to always close the session at the end in order to release the database lock
session.close()

print 'Test Complete'
