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

from pyglass.app.PyGlassEnvironment import PyGlassEnvironment

PyGlassEnvironment.initializeFromInternalPath(__file__)

#---------------------------------------------------------------------------------------------------
# RUN TEST SCRIPT

from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.svg.CadenceDrawing import CadenceDrawing

model   = Tracks_SiteMap.MASTER
session = model.createSession()
siteMap = session.query(model).filter(model.index == 13).first()
drawing = CadenceDrawing('test_2.svg', siteMap)

# --------------------------------------------------------------------------------------------------
# THIS DEMONSTRATES MAPPING BETWEEN A SITE MAP AND THE SCENE, PLUS SIMPLE SHAPES

xFed   = siteMap.xFederal
yFed   = siteMap.yFederal
fMap   = (xFed, yFed)
fScene = drawing.projectToScene((xFed, yFed))

print "siteMap.index = %s and siteMap.name = %s" % (siteMap.index, siteMap.filename)
print 'in siteMap, the federal marker is (%s, %s)' % fMap
print 'which projects into the scene as (%s, %s)' % (fScene[0], fScene[1])
print 'and projecting back to the map gives (%s, %s)' % drawing.projectToMap((fScene[0], fScene[1]))

# place a circle of radius 5 at (10.0, 10.0) in scene coordinates
drawing.circle((10, 10), 5)

# label it with text at (20, 10)
drawing.text("circle of radius 5", (20, 10), scene=True)

# now place a 20x40 rect in map coordinates (not scene coordinates) at the federal marker
drawing.rect((xFed + 40, yFed), 20, 40, scene=False)

# and another smaller one at (10, 20) in map coordinates
drawing.rect((10, 20), 4, 8, scene=False)

# place the federal coordinates as a text string 20 cm above the marker
text = "(%s, %s)" % (drawing.siteMap.federalEast, drawing.siteMap.federalNorth)
drawing.text(text, (0, 20), scene=True, stroke='green')

# place a 2 cm green unfilled circle atop the federal coordinate marker
drawing.circle((0, 0), 2, scene=True, fill='none', stroke='green', stroke_width=1)

# place a grid in registration with the 10m grid in the site map, and illustrates the use of a
# group which is then instanced multiple times across a drawing.
drawing.grid()

#==================================================================================================
# TEST POLYLINE

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
# LOAD ALL TRACKS FOR THIS SITE AND DRAW THEM AS DISKS
#
# tracks = siteMap.getAllTracks(session)
#
# print '%s tracks returned' % len(tracks)
#
# for track in tracks:
#     x = track.x
#     z = track.z
#
#     # The track dimensions stored in the database are in fractional meters, so multiply by
#     # 100 to convert to cm.
#     r = 100*0.5*(track.width/2.0 + track.length/2.0)
#
#     drawing.circle((x, z), r, scene=True, fill='none', stroke='blue', stroke_width=1)
#
#     # compute the averge uncertainty in cm (also stored in fractional meters)
#     u = 100*(track.widthUncertainty + track.lengthUncertainty)/2.0
#
#     drawing.circle((x, z), u, scene=True, fill='red', stroke='red', stroke_width=1)


#==================================================================================================
#  CREATE A GROUP CONTAINING A RECT, SHOWING HOW TO USE (INSTANCE) IT ROTATED AND TRANSLATED

drawing.createGroup('g1')
drawing.rect((0, 0), 10, 40, scene=False, groupId='g1') # add this rect to the group

drawing.use('g1', (400, 100), rotation=10)
drawing.use('g1', (400, 200), rotation=20)
drawing.use('g1', (400, 300), rotation=30)
drawing.use('g1', (400, 400), rotation=40)
drawing.use('g1', (400, 500), rotation=50)

#==================================================================================================
# #  CREATE A GROUP CONTAINING A CIRCLE, SHOWING HOW TO USE (INSTANCE) IT SCALED
#
# drawing.createGroup('g1')
# drawing.circle((0, 0), 10, scene=False, groupId='g1') # add this circle to the group
#
# drawing.use('g1', (400, 100), scale=1, scaleY=1)
# drawing.use('g1', (400, 200), scale=1, scaleY=1.1)
# drawing.use('g1', (400, 300), scale=1, scaleY=1.5)
# drawing.use('g1', (400, 400), scale=1, scaleY=2)
# drawing.use('g1', (400, 500), scale=1, scaleY=.5)
#
# # next, do a circle in scene coordinates
#
# drawing.createGroup('g2')
# drawing.circle((0, 0), 100, scene=True, groupId='g2') # add this circle to the group
#
# drawing.use('g2', (0, 0),   scale=1, scaleY=1)
# drawing.use('g2', (0, 100), scale=1, scaleY=1.1)
# drawing.use('g2', (0, 300), scale=1, scaleY=1.5)
# drawing.use('g2', (0, 400), scale=1, scaleY=2)
# drawing.use('g2', (0, 500), scale=1, scaleY=.5)
#

#==================================================================================================
# LOAD ALL TRACKS FOR THIS SITE AND DRAW THEM AS DISKS
#
# tracks = siteMap.getAllTracks(session)
#
# print '%s tracks returned' % len(tracks)
#
# drawing.createGroup('g')
# drawing.circle((0, 0), 10, scene=False, groupId='g') # add this circle to the group
#
# track = tracks[0]
#
# print ('track scale %s and %s' % (track.width, track.length))
#
# drawing.use('g', (0, 0),
#             scale=track.width, scaleY=track.length, rotation=track.rotation,
#             scene=True, fill='none', stroke='blue', stroke_width=1)
#
#
# # # place the federal coordinates as a text string 20 cm above the marker
# text = "(%s, %s)" % (drawing.siteMap.federalEast, drawing.siteMap.federalNorth)
# drawing.text(text, (0, 20), scene=True, stroke='green')
# #
# # # place a 2 cm green unfilled circle atop the federal coordinate marker
# # drawing.circle((0, 0), 2, scene=True, fill='none', stroke='green', stroke_width=1)
# #
# # drawing.circle((2011, 454), 2, scene=False, fill='none', stroke='red', stroke_width=2)
#
# # place a 4 cm green unfilled circle atop the federal coordinate marker
# drawing.circle((0, 0), 4, scene=True, fill='none', stroke='green', stroke_width=1)
#
# for track in tracks:
#     x = track.x
#     z = track.z
#
#     drawing.use('g', (x, z),
#                 scale=track.width, scaleY=track.length,
#                 rotation=track.rotation,
#                 scene=True, fill='none', stroke='blue', stroke_width=4)
#
#     # compute the averge uncertainty in cm (also stored in fractional meters)
#     # The track dimensions stored in the database are in fractional meters, so multiply by
#     # 100 to convert to cm.
#     u = 100*(track.widthUncertainty + track.lengthUncertainty)/2.0
#
#     drawing.circle((x, z), u, scene=True, fill='red', stroke='red', stroke_width=1)
#     drawing.line((x, z), (x + 20, z + 20), scene=True, stroke= 'blue')

#==================================================================================================
# done
drawing.save()

# Don't forget to always close the session at the end in order to release the database lock
session.close()

print 'Test Complete'
