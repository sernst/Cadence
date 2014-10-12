# SvgWriter.py
# (C)2014
# Kent A. Stevens

import math

import svgwrite
from svgwrite import mm


#___________________________________________________________________________________________________ CadenceDrawing
class CadenceDrawing(object):
    """ A class for writing Scalable Vector Graphics (SVG) files, tailored to create overlays for
        site maps. Each site map has a marker that indicates a reference point in Swiss Federal
        coordinates.  One such marker appears somewhere within each site map.  The may is oriented
        such that the x axis is positve to the right (towards the east) and the y axis is positive
        down (southward).  This site map is projected onto the y=0 plane of a 3D scene (by scaling,
        rotating, and translating) such that the Federal Coordinate marker is at the origin, the
        scene's positive x axis increases to the left ('west') and the scene's positive z axis
        increases to the 'north'.  The correspondence between these two coordinate systems is
        handled by public functions in this class, based on information derived from an instance of
        a Tracks_SiteMap (specifically the scale and the location of a federal coordinates marker
        within the map).

        This class wraps an instance of an svgwrite.Drawing and handles the mapping from 3D scene
        coordinates (x, z) to svg coordinates (x, y).  Scene coordinates are in real-world cm, while
        the svg coordinates used in the sitemaps is in 50:1 scaled mm.  That is, one mm in the
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
    def __init__(self, fileName, map):
        """ Creates a new instance of CadenceDrawing.  Calls to the public functions line(), rect(),
            and others result in objects being added to the SVG canvas, with the file written by the
            save() method to specified fileName.  The second argument, the map is provided as an
            argument to establish the correspondence between the Maya scene and the site map
            coordinates.  Note that all coordinates will be assumed to be mm units. """

        self.map = map

        self.pxPerMm = None

        # specify the width and height explicitly in mm, and likewise for the background rect
        left   = map.left*mm
        top    = map.top*mm
        width  = map.width*mm
        height = map.height*mm

        self.drawing = svgwrite.Drawing(fileName,
                                        profile='tiny',
                                        size=(width, height),
                                        stroke=svgwrite.rgb(0, 0, 0))
        self.drawing.add(self.drawing.rect((left, top), (width, height), opacity='0'))

#===================================================================================================
#                                                                                     P U B L I C


#___________________________________________________________________________________________________ scaleToScene
    def scaleToScene(self, v):
        """ Converts from map coordinates ('scaled mm') to scene coordinates (in cm). The 0.1 factor
            converts from the 'scaled mm' units of the map to the centimeter units of the scene.
            The map is usually drawn in 50:1 scale. """

        return int(v*(0.1*self.map.scale))

#___________________________________________________________________________________________________ scaleToMap
    def scaleToMap(self, v):
        """ Converts from scene coordinates (in cm) to map coordinates ('scaled mm')   The map
            is usually drawn in 50:1 scale. """

        return int(v/(0.1*self.map.scale))

#___________________________________________________________________________________________________ projectToScene
    def projectToScene(self, p):
        """ The given map location p is projected to the corresponding scene point and returned.
            In the scene, x is positive to the left, and z is positive upwards.  In the map, x is
            positive to the right and y is positive downwards (hence both are multiplied by -1.
            Note the asymmetry between projectToScene and projectToMap.  Going from the map to the
            scene presumes one starts with map coordinates in mm, while going from the map """

        xScene = -self.scaleToScene(p[0] - self.map.xFederal)
        zScene = -self.scaleToScene(p[1] - self.map.yFederal)

        return [xScene, zScene]

#___________________________________________________________________________________________________ projectToMap
    def projectToMap(self, p, scene =True):
        """ The given scene point p is projected to the corresponding map location and returned.
            xScene is positive to the left, and zScene is positive upwards; xMap is positive to the
            right and yMap is positive downwards.  """

        x = self.map.xFederal - self.scaleToMap(p[0])
        y = self.map.yFederal - self.scaleToMap(p[1])

        return [x, y]

#___________________________________________________________________________________________________ mm
    def mm(self, p):
        """ Appends the units label 'mm' to each value. """
        return [p[0]*mm, p[1]*mm]

#___________________________________________________________________________________________________ line
    def line(self, p1, p2, scene =True, **extra):
        """ Adds a line object to the svg file based on two scene points. It first converts from
            scene to map coordinates if necessary, then concatenates 'mm' units to all values. """

        # convert from scene coordinates to map coordinates if necessary
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

        # convert from scene coordinates to map coordinates if necessary
        if scene:
            p = list()
            for point in points:
                p.append(self.projectToMap(point))
            points = p

        # create a list of points p with 'mm' appended to the coordinates of each point
        p = list()
        for point in points:
            p.append(self.mm(point))

        obj = self.drawing.polyline(p, **extra)
        self.drawing.add(obj)
        return obj

#___________________________________________________________________________________________________ rect
    def rect(self, insert, size, scene =True, rx =None, ry =None, **extra):
        """ Adds a rect object to the svg file, based on insert (coordinates of upper left corner)
            and size (width, height).  If the boolean scene is True, the arguments are converted to
            'scaled mm', otherwise they are presumed to be in mm.  All coordinates are explicitly
            labled with 'mm' and passed to svgwrite. """

        # convert from scene coordinates to map coordinates if necessary
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

        # convert from scene coordinates to map coordinates if necessary
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

        # convert from scene coordinates to map coordinates if necessary
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

        # convert from scene coordinates to map coordinates if necessary
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
        """ Adds a grid of marks (each an'X' or '+" depending on the boolean diagonals) of a given
            size and spacing, spaThe
            grid is then filled out with marks within the width and height of the map, spaced in x
            by dx and in y by dy. Note that the grid is computed entirely in map coordinates. """

        x0 = self.map.xFederal
        y0 = self.map.yFederal
        x0 = x0%dx
        y0 = y0%dy
        xn = int(self.map.width/dx)
        yn = int(self.map.height/dy)

        for i in range(xn):
            x = x0 + i*dy
            for j in range(yn):
                y = y0 + j*dy
                self.mark([x, y], markerSize, diagonals, scene=False, **extra)

#___________________________________________________________________________________________________ markG
    def markG(self, size, diagonals =True, scene =True, **extra):
        """ Adds a mark of given radius at a given location.  If diagonals is True the mark is
            an 'X' else a '+'. """

        x = 0
        y = 0

        #markGroup = self.drawing.add(self.drawing.g(id='markGroup'))
        markGroup = self.drawing.g(id='markGroup')
        if diagonals:
            size *= math.sqrt(2.0)
            markGroup.add(self.line([x - size, y - size], [x + size, y + size], scene=scene, **extra))
            markGroup.add(self.line([x - size, y + size], [x + size, y - size], scene=scene, **extra))
        else:
            markGroup.add(self.line([x - size, y], [x + size, y], scene=scene, **extra))
            markGroup.add(self.line([x, y - size], [x, y + size], scene=scene, **extra))

        return markGroup

#___________________________________________________________________________________________________ gridG
    def gridG(self, markerSize =2, diagonals =True, dx =200, dy =200, **extra):
        """ Adds a grid of marks (each an'X' or '+" depending on the boolean diagonals) of a given
            size and spacing, spaThe
            grid is then filled out with marks within the width and height of the map, spaced in x
            by dx and in y by dy. Note that the grid is computed entirely in map coordinates. """

        x0 = self.map.xFederal
        y0 = self.map.yFederal
        x0 = x0%dx
        y0 = y0%dy
        xn = int(self.map.width/dx)
        yn = int(self.map.height/dy)

        markerG = self.markG(markerSize, diagonals, scene=False, **extra)

        for i in range(xn):
            x = x0 + i*dy
            for j in range(yn):
                y = y0 + j*dy
                #self.mark([x, y], markerSize, diagonals, scene=False, **extra)
                instance = self.drawing.use(markerG)
                instance.translate(2.834*x, 2.834*y)
                self.drawing.add(instance)

#___________________________________________________________________________________________________ save
    def save(self):
        """ Writes the current drawing to the file specified at initialization. """
        self.drawing.save()
