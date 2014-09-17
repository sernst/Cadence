# SvgWriter.py
# (C)2014
# Kent A. Stevens

import svgwrite

#___________________________________________________________________________________________________ SvgWriter
class SvgWriter(object):
    """ A class for writing Scalable Vector Graphics (SVG) files, tailored to create overlays for
        site maps. A site map has a marker that indicates a reference point in Swiss Federal
        coordinates.  One such marker appears somewhere within each site map.  The may is oriented
        such that the x axis is positve to the right (towards the east) and the y axis is positive
        down (southward).  This site map is projected onto the y=0 plane of a 3D scene, by scaling,
        rotating, and translating such that the Federal Coordinate marker is at the origin, the
        scene's positive x axis increases to the left ('west') and the scene's positive z axis
        increases to the 'north'.  The correspondence between these two coordinate systems is
        handled by public functions in the Track_SiteMap instance, based on the scale and site map
        coordinates of the federal coordinates marker. When creating an instance of SvgWriter,
        an instance of a Track_SiteMap is provided.  The SvgWriter has public methods to provide
        the ability to draw lines, """

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, fileName, map):
        """ Creates a new instance of SvgWriter.  An instance of a map is provided as an argument
            to establish the correspondence between the Maya scene and the site map coordinates. """

        self.map     = map
        self.drawing = svgwrite.Drawing(fileName, profile='tiny')


#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ line
    def line(self, x1, y1, x2, y2, **extra):
        """ Adds a line object to the svg file. """
        self.drawing.add(self.drawing.line((x1, y1), (x2, y2), **extra))

#___________________________________________________________________________________________________ polyLine
    def polyLine(self, points, **extra):
        """ Adds a line object to the svg file. """
        self.drawing.add(self.drawing.polyLine(points, **extra))

#___________________________________________________________________________________________________ rect
    def rect(self, upperLeftX, upperLeftY, width, height, rx =None, ry =None, **extra):
        """ Adds a rectangle object to the svg file. """
        insert = (upperLeftX, upperLeftY)
        size   = (width, height)
        self.drawing.add(self.drawing.rect(insert, size, rx, ry, *extra))

#___________________________________________________________________________________________________ circle
    def circle(self, centerX, centerY, radius, **extra):
        """ Adds a circle object to the svg file. """
        self.drawing.add(self.drawing.circle((centerX, centerY), radius, **extra))

#___________________________________________________________________________________________________ ellipse
    def ellipse(self, x1, y1, radius1, radius2, **extra):
        """ Adds an ellipse object to the svg file, based on a center point and two radii. """
        self.drawing.add(self.drawing.ellipse((x1, y1), (radius1, radius2), **extra))

#___________________________________________________________________________________________________ text
    def text(self, textString, upperLeftX, upperLeftY, **extra):
        """ Adds a text of a given fill at the given insertion point. """
        self.drawing.add(self.drawing.text(textString, (upperLeftX, upperLeftY), **extra))

#___________________________________________________________________________________________________ save
    def save(self):
        """ Writes the current drawing to the file specified at initialization. """
        self.drawing.save()
