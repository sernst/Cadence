# SvgTestPDF.py
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

from pyaid.system.SystemUtils import SystemUtils

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
fileName = 'test_new.svg'
drawing = CadenceDrawing(fileName, siteMap)

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

#===============================================================================

# place a circle of radius 5 at (100.0, 100.0) in scene coordinates
# drawing.circle((100, 100), 5, scene=True, stroke='red', fill='green')

# label it with text at (100, 10)
drawing.text("circle of radius 5 at (200, 10)", (100, 10), scene=True, stroke='blue')

# now place another circle and rect in map (not scene) coordinates below the federal marker
drawing.rect((xScene, yScene - 100), 4, 10, scene=False, fill='red')

# and another at (100, 200), also in map coordinates
drawing.rect((100, 200), 10, 4, scene=False)


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

drawing.save()

#==================================================================================================
""" The general format for the command line invocation of inkscape is:

for PDF export:

inkscape -f sourceFile.svg -A destinationFile.pdf

or with the standard installation (without inkscape addd to the search path:

/Applications/Inkscape.app/Content/Resources/bin/inkscape -f sourceFile.svg -A destinationFile.pdf

for PNG export:

inkscape -f sourceFile.svg -e destinationFile.png


  # path = self.getResourcePath('..', '..', 'help.markdown', isFile=True)
        # gives you the TrackwayManager folder
        # print "in the TrackwayManagerWidget, the path =%s" % path
        # get a qIcon or something or QButton icon and put the icons in the TrackwayManager Widget
        # folder and commit them to the project also. Look for them in the changes at the bottom
        # of PyCharm window

        # this returns the path to the shared directory resources/apps/CadenceApplication
        # to get self.getAppResourcePath()

"""

sourceFile = fileName
destinationFile = 'testDELETEME.pdf'

cmd = [
    '/Applications/Inkscape.app/Contents/Resources/bin/inkscape',
    '-f',
    None,
    '-A',
    None]

cmd[2] = sourceFile
cmd[4] = destinationFile

print(cmd)
response = SystemUtils.executeCommand(cmd)





#==================================================================================================

session.close()
print 'Test Complete'
