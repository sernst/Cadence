# SvgWriter.py
# (C)2014
# Kent A. Stevens

import math

import svgwrite
from svgwrite import mm

from pyaid.OsUtils import OsUtils

#___________________________________________________________________________________________________ CadenceDrawing
class CadenceDrawing(object):
    """ A class for writing Scalable Vector Graphics (SVG) files, tailored to create overlays for
        site maps. Each site map has a marker that indicates a reference point in Swiss Federal
        coordinates.  At least one such marker appears somewhere within each site map (in cases
        where there were two, the more central was chosen).  The maps are all oriented such that
        the x axis is positve to the right (towards the east) and the y axis is positive down
        (southward).  For visualization in Cadence, a site map is projected onto the y=0 plane of a
        3D scene such that the Federal Coordinate marker is placed at the origin in 3D, and the
        scene's positive x axis increases to the left ('west') and the scene's positive z axis
        increases to the 'north'.  The correspondence between these two coordinate systems is
        handled by public functions to be found in this class, based on information derived from an
        instance of a Tracks_SiteMap (specifically the scale and the location of a federal
        coordinates marker within the siteMap).

        This class wraps (owns) an instance of an svgwrite.Drawing and handles the mapping from 3D
        scene coordinates (x, z) to svg coordinates (x, y).  Scene coordinates are in real-world cm,
        while the svg coordinates used in the sitemaps is in 50:1 scaled mm.  That is, one mm in the
        drawing equals 5 cm, realworld.  By default, a saved CadenceDrawing can then be
        placed in an Adobe Illustrator layer, in registation with the vector art of a sitemap.

        As background, the underlying svgwrite.Drawing class provides functions to draw lines,
        rectangles, and other objects, that are accumulated (by .add() function) and subsequently
        written (by .save() to the file specified.  The svgwrite class Drawing uses kwargs to
        provide a Pythonic means to specify attributes such as stroke, stroke_linecap, stroke_width,
        and fill.  For example (as shown in svgwrite.shapes.py):
            line    requires start=(x, y), end=(x, y)
            rect    requires insert=(x, y), size=(width, height)
            circle  requires center=(x, y), r=<number>
            ellipse requires center=(x, y), r=(radius1, radius2)
        where a simple svgwrite usage would be:
            import svgwrite
            d = svgwrite.Drawing(someMap, someFile)
            d.add(d.line(someStartPoint, someEndPoint)
            d.save()
        See further coding examples at http://nullege.com/codes/search/svgwrite.Drawing.

        In this wrapper adaptation of svgwrite, a CadenceDrawing provides the basic shape functions
        line, rect, circle, etc., each of which returns an svg object.  They are scaled
        appropriately for inclusion into a tracksite file in Adobe illustrator, but they can also
        be added to svg groups and so forth. Generally one would leave the kwarg scene to default
        to True, as that enables conversion from scene coordinates to scaled mm."""


#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, fileName, siteMap):
        """ Creates a new instance of CadenceDrawing.  Calls to the public functions line(), rect(),
            and others result in objects being added to the SVG canvas, with the file written by the
            save() method to specified fileName.  The second argument, the siteMap is provided as an
            argument to establish the correspondence between the Maya scene and the site siteMap
            coordinates.  Note that all coordinates will be assumed to be mm units. """

        self.siteMap = siteMap

        # Generally units can be specified in millimeters.  In a few cases, however, (e.g.,
        # PolyLine) the coordinates must be unqualified integers (as px).  The site maps, however
        # are in 'scaled mm'.  Hence the need for a cnversion factor pxPerMm. Unfortunately, the
        # conversion between px and mm is OS-dependent. The conversion from px to inches is 72 for
        # Apple but 90 more generally).

        ppi = 72 if OsUtils.isMac() else 90
        self.pxPerMm = ppi/25.4

        # specify the width and height explicitly in mm, and likewise for the background rect
        left   = siteMap.left*mm
        top    = siteMap.top*mm
        width  = siteMap.width*mm
        height = siteMap.height*mm

        self.drawing = svgwrite.Drawing(
            fileName,
            profile='tiny',
            size=(width, height),
            stroke=svgwrite.rgb(0, 0, 0))
        self.drawing.add(self.drawing.rect((left, top), (width, height), opacity='0'))

#===================================================================================================
#                                                                                     P U B L I C


#___________________________________________________________________________________________________ scaleToScene
    def scaleToScene(self, value):
        """ Site maps (Adobe Illustrator .ai files) are typically in 50:1 scale, and use mm as their
            units.  Consequently a single unit in the site map corresponds to 50 mm in the 'real
            world'. The 3D scene used in Cadence, on the other hand, uses cm scale.  That is,
            coordinates and dimensions are in cm.  This function converts a value (coordinate or
            dimension) from 'scaled mm' of the map into centimeter units of the 3D scene. For
            example, a value of 20 units corresponds to 100 cm in the scene, which is returned. """

        return 0.1*self.siteMap.scale*value

#___________________________________________________________________________________________________ scaleToMap
    def scaleToMap(self, v):
        """ Converts from scene coordinates (in cm) to siteMap coordinates ('scaled mm'). The
            siteMap is usually drawn in 50:1 scale. """

        #return round(v/(0.1*self.siteMap.scale))
        return v/(0.1*self.siteMap.scale)

#___________________________________________________________________________________________________ projectToScene
    def projectToScene(self, p):
        """ The given siteMap location p is projected to the corresponding scene point and returned.
            In the scene, x is positive to the left, and z is positive upwards.  In the siteMap, x
            is positive to the right and y is positive downwards. """

        xMap   = p[0]
        yMap   = p[1]
        xScene = -self.scaleToScene(xMap - self.siteMap.xFederal)
        zScene = -self.scaleToScene(yMap - self.siteMap.yFederal)

        return (xScene, zScene)

#___________________________________________________________________________________________________ projectToMap
    def projectToMap(self, p):
        """ The given 2D scene point p, comprised of scene cooordinates (xScene, zScene), is
            projected to the corresponding 2D siteMap location (xMap, yMap) and returned. xScene
            is positive to the left, and zScene is positive upwards; xMap is positive to the right
            and yMap is positive downwards. """

        xScene = p[0]
        yScene = p[1]
        xMap   = self.siteMap.xFederal - self.scaleToMap(xScene)
        yMap   = self.siteMap.yFederal - self.scaleToMap(yScene)

        return (xMap, yMap)

#___________________________________________________________________________________________________ mm
    def mm(self, p):
        """ Appends the units label 'mm' to each value. """
        return (p[0]*mm, p[1]*mm)

#___________________________________________________________________________________________________ line
    def line(self, p1, p2, scene =True, **extra):
        """ Adds a line object to the svg file based on two scene points. It first converts from
            scene to siteMap coordinates if necessary, then concatenates the units suffix 'mm' to
            all coordinate values. """

        # convert from scene coordinates to siteMap coordinates if necessary
        if scene:
            p1 = self.projectToMap(p1, scene)
            p2 = self.projectToMap(p2, scene)

        # append 'mm' units to each coordinate of the points p1 and p2 and create line object
        p1 = self.mm(p1)
        p2 = self.mm(p2)

        line = self.drawing.line(p1, p2, **extra)
        self.drawing.add(line)
        return line

#___________________________________________________________________________________________________ polyLine
    def polyLine(self, points, scene =True, **extra):
        """ Adds a polyline object to the svg file, based on a list of scene points. """

        # map from scene coordinates to siteMap coordinates if necessary
        if scene:
            mappedPoints = list()
            for p in points:
                mappedPoints.append(self.projectToMap(p))
            points = mappedPoints

        # svgwrite does not allow coordinates with the suffix 'mm', hence all values must be in px.
        convertedPoints = list()
        for p in points:
            x = p[0]*self.pxPerMm
            y = p[1]*self.pxPerMm
            convertedPoints.append((x, y))

        obj = self.drawing.polyline(convertedPoints, **extra)
        self.drawing.add(obj)
        return obj

#___________________________________________________________________________________________________ rect
    def rect(self, insert, size, scene =True, rx =None, ry =None, **extra):
        """ Adds a rect object to the svg file, based on insert (coordinates of upper left corner)
            and size (width, height).  If the boolean scene is True, the arguments are converted to
            'scaled mm', otherwise they are presumed to be in mm.  All coordinates are explicitly
            labled with 'mm' and passed to svgwrite. """

        # convert from scene coordinates to siteMap coordinates if necessary
        if scene:
            insert = self.projectToMap(insert, scene)
            size   = [self.scaleToMap(size[0]), self.scaleToMap(size[1])]

        # append the 'mm' units
        insert = self.mm(insert)
        size   = self.mm(size)

        obj = self.drawing.rect(insert, size, rx, ry, **extra)
        self.drawing.add(obj)
        return obj

#___________________________________________________________________________________________________ circle
    def circle(self, center, radius, scene =True, **extra):
        """ Adds a circle object to the svg file. All coordinates are explicitly labled with 'mm'
            and passed to svgwrite. """

        # convert from scene coordinates to siteMap coordinates if necessary
        if scene:
            center = self.projectToMap(center)
            radius = self.scaleToMap(radius)

        # append the 'mm' units
        center = self.mm(center)
        radius = radius*mm

        obj = self.drawing.circle(center, radius, **extra)
        self.drawing.add(obj)
        return obj

#___________________________________________________________________________________________________ ellipse
    def ellipse(self, center, radii, scene =True, **extra):
        """ Adds an ellipse object to the svg file, based on a center point and two radii.  All
            coordinates are explicitly labled with 'mm' and passed to svgwrite. """

        # convert from scene coordinates to siteMap coordinates if necessary
        if scene:
            center = self.projectToMap(center)
            radii  = [self.scaleToMap(radii[0]), self.scaleToMap(radii[1])]

        # append the 'mm' units
        center = self.mm(center)
        radii  = self.mm(radii)

        obj = self.drawing.ellipse(center, radii, **extra)
        self.drawing.add(obj)
        return obj

#___________________________________________________________________________________________________ text
    def text(self, textString, insert, scene =True, **extra):
        """ Adds a text of a given fill at the given insertion point. """

        # convert from scene coordinates to siteMap coordinates if necessary
        if scene:
            insert = self.projectToMap(insert)

        # append the 'mm' units
        insert = self.mm(insert)

        obj = self.drawing.text(textString, insert, **extra)
        self.drawing.add(obj)
        return obj

#___________________________________________________________________________________________________ mark
    def mark(self, center, size, diagonals =True, scene =True, **extra):
        """ Adds a mark of given radius at a given location.  If diagonals is True the mark is
            an 'X' else a '+'. """

        x = center[0]
        y = center[1]

        if diagonals:
            size *= math.sqrt(2.0)
            self.line([x - size, y - size], [x + size, y + size], scene=scene, **extra)
            self.line([x - size, y + size], [x + size, y - size], scene=scene, **extra)
        else:
            self.line([x - size, y], [x + size, y], scene=scene, **extra)
            self.line([x, y - size], [x, y + size], scene=scene, **extra)

#___________________________________________________________________________________________________ grid
    def grid(self, markerSize =2, diagonals =True, dx =200, dy =200, **extra):
        """ Adds a rectangular grid of marks (each an'X' or '+" depending on the boolean diagonals)
            of a given size and spacing.  The grid is in registration with the site map's federal
            coordinate marker, spaced by multiples of dx and dy to fill up the width and height of
            the siteMap. Note that the grid is computed entirely in siteMap coordinates. Note that
            the grid marks on a site map are separated by 10 m in the real world, or 200 units in
            the map. """

        x0 = self.siteMap.xFederal
        y0 = self.siteMap.yFederal
        x0 = x0%dx
        y0 = y0%dy
        xn = int(self.siteMap.width/dx)
        yn = int(self.siteMap.height/dy)

        for i in range(xn):
            x = x0 + i*dy
            for j in range(yn):
                y = y0 + j*dy
                self.mark([x, y], markerSize, diagonals, scene=False, **extra)

#___________________________________________________________________________________________________ save
    def save(self):
        """ Writes the current drawing to the file specified at initialization. """
        self.drawing.save()

#___________________________________________________________________________________________________ group
    def group(self):
        """ Creates an svgwrite group, so that the SVG fragments that are added to the group can be
            transformed by the group's transform mixin.  For this
        """
        pass

#___________________________________________________________________________________________________ symbol
    def symbol(self, name):
        """  Creates a symbol of a given name. """
        #self.drawing. ... later
        pass