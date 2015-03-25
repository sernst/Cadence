# CadenceDrawing.py
# (C)2014
# Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division


import svgwrite
from svgwrite import mm

from pyaid.system.SystemUtils import SystemUtils
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
        scene coordinates (x, z) to SVG coordinates (x, y).  Scene coordinates are in real-world cm,
        while the SVG coordinates used in the sitemaps is in (50:1 scaled) mm.  That is, one mm in
        the _drawing equals 5 cm, realworld.  By default, a saved CadenceDrawing can be placed in an
        Adobe Illustrator layer, then adjusted to be in registation with the sitemap.

        CadenceDrawing is built upon the svgwrite.Drawing class, which provides the basic
        functions to draw lines, rectangles, and other SVG objects. For further information on
        svgwrite, consult: https://pythonhosted.org/svgwrite

        A CadenceDrawing instance simplifies the functionality of svgwrite, encapsulating all the
        handling of all SVG fragments through function calls to create lines, polyLines, rects,
        circles, elipses, and text, plus transformable groups, with the resultant SVG file written
        by the function save.  A CadenceDrawing adopts the underlying svgwrite convention of using
        kwargs to provide a Pythonic means to specify SVG attributes such as stroke, stroke_linecap,
        stroke_width, and fill. CadenceDrawing is a wrapper adaptation of svgwrite.  That is, a
        CadenceDrawing encapsulates an instance of an svgwrite Drawing. Coordinate mapping allows
        trackway data (coordinates and dimensions) to be scaled appropriately for inclusion into an
        SVG-format tracksite file to be placed in a layer in Adobe illustrator).  This scaling is
        provided by the kwarg scene=True, wherein scene coordinates (in cm) are converted to scaled
        mm. The following is an example in which all tracks for a given site are loaded and drawn:

            tracks = siteMap.getAllTracks(session)
            for track in tracks:
                x = track.x
                z = track.z
                # Track dimensions are in fractional meters, so multiply by 100 to convert to cm.
                r = 100*0.5*(track.width/2.0 + track.length/2.0)
                drawing.circle((x, z), r, scene=True, fill='none', stroke='blue', stroke_width=1)
                # compute this track's averge uncertainty in cm (also stored in fractional meters)
                u = 100*(track.widthUncertainty + track.lengthUncertainty)/2.0
                drawing.circle((x, z), u, scene=True, fill='red', stroke='red', stroke_width=1)

        A more advanced usage uses groups that can be transformed (rotated, scaled, translated).
        A group is created and given an ID that is then passed to drawing functions (which create
        the shape), then the group is used (instantiated) at somePlace at a rotation of 45 degrees:

            drawing.createGroup('g1')
            drawing.rect((0, 0), width, height, groupId='g1')
            ...etc...

            drawing.use('g1', somePlace, rotation=45)

        The use of groups, while convenient, requires that all map coordinates be converted to px.
        For more detail, see the use function and grid, which produces a 10 m grid. """

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, fileName, siteMap):
        """ Creates a new instance of CadenceDrawing.  Calls to the public functions line(), rect(),
            and others result in objects being added to the SVG canvas, with the file written by the
            save() method to specified fileName.  The second argument, the siteMap is provided as an
            argument to establish the correspondence between the Maya scene and the site siteMap
            coordinates. """

        self.siteMapReady = False if siteMap.scale == 0.0 else True

        if not self.siteMapReady:
            print("CadenceDrawing: %s %s not completed " % (siteMap.name, siteMap.level))
            return

        self.fileName = fileName
        self.siteMap  = siteMap

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

        self._drawing = svgwrite.Drawing(
            fileName,
            profile='tiny',
            size=(width, height),
            stroke=svgwrite.rgb(0, 0, 0))
        self._drawing.add(self._drawing.rect((left, top), (width, height), opacity='0'))

        self.groups = dict()


#===================================================================================================
#                                                                                     P U B L I C


#___________________________________________________________________________________________________ circle
    def circle(self, center, radius, scene =True, groupId =None, **extra):
        """ Adds a circle object to the SVG file. All coordinates are explicitly labled with 'mm'
            and passed to svgwrite. """

        if not self.siteMapReady:
            return

        # convert from scene coordinates to map coordinates as necessary
        if scene:
            center = self.projectToMap(center)
            radius = self.scaleToMap(radius)

        # convert from (scaled) mm to px
        center = (self.pxPerMm*center[0], self.pxPerMm*center[1])
        radius *= self.pxPerMm

        # create the object
        obj = self._drawing.circle(center, radius, **extra)

        # and add it to either a specific group or to the default _drawing
        if groupId:
            group = self.groups[groupId]
            if group:
                group.add(obj)
            else:
                print('circle:  %s is not a valid group ID' % groupId)
                return
        else:
            self._drawing.add(obj)

#___________________________________________________________________________________________________ createGroup
    def createGroup(self, id, **extra):
        """ Creates an SVG group, so that subsequent SVG fragments can be added to the group.  When
            the group is subsequently used (by the use function) an instance is created, and placed
            at a particular location in the drawing, with a particular scale and rotation. This
            method only creates tghe group; to then add fragments, the group's id is passed to draw
            functions so that those fragments are added to the group rather than to the drawing
            directly. Groups are intended to be placed readily across a drawing, hence the pivot
            for the group should normally be centered on the user space (map) origin."""

        if not self.siteMapReady:
            return

        group = self._drawing.g(id=id, **extra)

        # add it to defs so that it is not directly rendered
        self._drawing.defs.add(group)

        # and keep track of the id so it can be used to refer to the group
        self.groups[id] = group

#___________________________________________________________________________________________________ ellipse
    def ellipse(self, center, radii, scene =True, groupId =None, **extra):
        """ Adds an ellipse object to the SVG file, based on a center point and two radii.  All
            coordinates are explicitly labled with 'mm' and passed to svgwrite. """

        if not self.siteMapReady:
            return

        # convert from scene coordinates to map coordinates as necessary
        if scene:
            center = self.projectToMap(center)
            radii  = [self.scaleToMap(radii[0]), self.scaleToMap(radii[1])]

        # convert from (scaled) mm to px
        center = (self.pxPerMm*center[0], self.pxPerMm*center[1])
        radii  = (self.pxPerMm*radii[0], self.pxPerMm*radii[1])

        # create the object
        obj = self._drawing.ellipse(center, radii, **extra)

        # and add it to either a specific group or to the default _drawing
        if groupId:
            group = self.groups[groupId]
            if group:
                group.add(obj)
            else:
                print('ellipse:  %s is not a valid group ID' % groupId)
                return
        else:
            self._drawing.add(obj)

#___________________________________________________________________________________________________ federalCoordinates
    def federalCoordinates(self, deltaX =0, deltaZ =20, diskRadius =2):
        """ Place the coordinates a text string at an offset from the fiducial marker. """

        if not self.siteMapReady:
            return

        text = "(%s, %s)" % (self.siteMap.federalEast, self.siteMap.federalNorth)
        self.text(text, (deltaX, deltaZ), scene=True, font_size="8")

        # place an unfilled green circle of specified radius atop the federal coordinate marker
        self.circle(
            (0, 0),
            diskRadius,
            scene=True,
            fill='none',
            stroke='green',
            stroke_width=1)

#___________________________________________________________________________________________________ grid
    def grid(self, size =2, diagonals =True, dx =200, dy =200, **extra):
        """ This is a group-based version of grid.  It creates a rectangular grid of marks.
            The grid marks on a site map are separated by 10 m in the real world, or 200 units
            in the map in their 'scaled mm' convention. Unfortunately, the group construct in
            svgwrite requires px values, and will not allow the mm suffix. """

        if not self.siteMapReady:
            return

        x0 = self.siteMap.xFederal%dx
        y0 = self.siteMap.yFederal%dy
        xn = int(self.siteMap.width/dx)
        yn = int(self.siteMap.height/dy)

        self.createGroup('mark')
        self.mark(size, scene=False, groupId='mark')

        for i in range(xn):
            x = x0 + i*dy
            for j in range(yn):
                y = y0 + j*dy
                self.use('mark', [self.pxPerMm*x, self.pxPerMm*y], rotation=45, scene=False)

#___________________________________________________________________________________________________ line
    def line(self, p1, p2, scene =True, groupId =None, **extra):
        """ Adds a line object to the svg file based on two scene points. It first converts from
            scene to siteMap coordinates if necessary, then concatenates the units suffix 'mm' to
            all coordinate values. """

        if not self.siteMapReady:
            return

        # convert from scene coordinates to map coordinates as necessary
        if scene:
            p1 = self.projectToMap(p1)
            p2 = self.projectToMap(p2)

        # convert from (scaled) mm to px
        p1 = (self.pxPerMm*p1[0], self.pxPerMm*p1[1])
        p2 = (self.pxPerMm*p2[0], self.pxPerMm*p2[1])

        # create the object
        obj = self._drawing.line(p1, p2, **extra)

        # and add it to either a specific group or to _drawing (the default)
        if groupId:
            group = self.groups[groupId]
            if group:
                group.add(obj)
            else:
                print('line:  %s is not a valid group ID' % groupId)
                return
        else:
            self._drawing.add(obj)

#___________________________________________________________________________________________________ mark
    def mark(self, size, scene =True, groupId =None, **extra):
        """ Adds an axis-aligned '+' mark of given size at the origin. If scene=True, the size is
            transformed to map coordinates, else it is presumed to already be in map coordinates. If
            groupId=True, the mark is added to the specified group, rather than to the drawing.
            This fragment is intended for use as a group (see grid). """

        if not self.siteMapReady:
            return

        r = size

        self.line([-r, 0], [r, 0], scene=scene, groupId=groupId, **extra)
        self.line([0, -r], [0, r], scene=scene, groupId=groupId, **extra)

#___________________________________________________________________________________________________ mm
    def mm(self, p):
        """ Appends the units label 'mm' to each value.  Too many cases where svgwrite will not
            allow this suffix, so not currently used. """

        return (p[0]*mm, p[1]*mm)

#___________________________________________________________________________________________________ polyLine
    def polyLine(self, points, scene =True, groupId =None, **extra):
        """ Adds a polyline object to the SVG file, based on a list of scene points. If canvas is
            specified, this permits adding this object to a """

        if not self.siteMapReady:
            return

        # map from scene coordinates to map coordinates as necessary
        if scene:
            mappedPoints = list()
            for p in points:
                mappedPoints.append(self.projectToMap(p))
            points = mappedPoints

        # svgwrite does not allow coordinates with the suffix 'mm', hence all values must be in px.
        convertedPoints = list()
        for p in points:
            x = self.pxPerMm*p[0]
            y = self.pxPerMm*p[1]
            convertedPoints.append((x, y))

        # create the object
        obj = self._drawing.polyline(convertedPoints, **extra)

        # and add it to either a specific group or symbol, or the default _drawing
        if groupId:
            group = self.groups[groupId]
            if group:
                group.add(obj)
            else:
                print('polyLine:  %s is not a valid group ID' % groupId)
                return
        else:
            self._drawing.add(obj)

#___________________________________________________________________________________________________ projectToScene
    def projectToScene(self, p):
        """ The given siteMap location p is projected to the corresponding scene point and returned.
            In the scene, x is positive to the left, and z is positive upwards.  In the siteMap, x
            is positive to the right and y is positive downwards. """

        if not self.siteMapReady:
            return

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

        if not self.siteMapReady:
            return

        xScene = p[0]
        yScene = p[1]
        xMap   = self.siteMap.xFederal - self.scaleToMap(xScene)
        yMap   = self.siteMap.yFederal - self.scaleToMap(yScene)

        return (xMap, yMap)

#___________________________________________________________________________________________________ rect
    def rect(self, center, width, height, scene =True, groupId =None, rx =None, ry =None, **extra):
        """ Adds a rect object to the SVG file, based on center and dimensions. If the boolean
            scene is True, the arguments are converted to
            'scaled mm', otherwise they are presumed to be in mm.  All coordinates are explicitly
            labled with 'mm' and passed to svgwrite. """

        if not self.siteMapReady:
            return

        xCenter = center[0]
        yCenter = center[1]

        # convert from scene coordinates to map coordinates as necessary
        if scene:
            xCenter = self.scaleToMap(xCenter)
            yCenter = self.scaleToMap(yCenter)
            width   = self.scaleToMap(width)
            height  = self.scaleToMap(height)

        # now compute the insert point, i.e., the upper left corner
        insert  = (xCenter - width/2, yCenter - height/2)

        # convert from (scaled) mm to px
        insert = (self.pxPerMm*insert[0], self.pxPerMm*insert[1])
        size   = (self.pxPerMm*width, self.pxPerMm*height)

        # create the object
        obj = self._drawing.rect(insert, size, rx, ry, **extra)

        # and add it to either a specific group or to the default _drawing
        if groupId:
            group = self.groups[groupId]
            if group:
                group.add(obj)
            else:
                print('rect:  %s is not a valid group ID' % groupId)
                return
        else:
            self._drawing.add(obj)

#___________________________________________________________________________________________________ save
    def save(self, toPDF=False):
        """ Writes the current _drawing in SVG format to the file specified at initialization. If
            one wishes to have create a PDF file (same file name as used for the .SVG, but with
            suffix .PDF), then call with toPDF True). """

        if not self.siteMapReady:
            return

        self._drawing.save()

        #  we're done if no PDF version is also required
        if not toPDF:
            return

        # strip any extension off of the file name
        basicName = self.fileName.split('.')[0]

        # load up the command
        cmd = [
            '/Applications/Inkscape.app/Contents/Resources/bin/inkscape',
            '-f',
            None,
            '-A',
            None]
        cmd[2] = basicName + '.svg'
        cmd[4] = basicName + '.pdf'

        # and execute it
        response = SystemUtils.executeCommand(cmd)
        if response['error']:
            print('response[error]=%s'%response['error'])

#___________________________________________________________________________________________________ scaleToMap
    def scaleToMap(self, v):
        """ Converts from scene coordinates (in cm) to siteMap coordinates ('scaled mm'). The
            siteMap is usually drawn in 50:1 scale. """

        if not self.siteMapReady:
            return

        return v/(0.1*self.siteMap.scale)

#___________________________________________________________________________________________________ scaleToScene
    def scaleToScene(self, value):
        """ Site maps (Adobe Illustrator .ai files) are typically in 50:1 scale, and use mm as their
            units.  Consequently a single unit in the site map corresponds to 50 mm in the 'real
            world'. The 3D scene on the other hand, uses cm scale.  This function converts the given
            value from the 'scaled mm' of the map into centimeter units of the 3D scene. For
            example, a value of 20 units corresponds to 100 cm in the scene, which is returned. """

        if not self.siteMapReady:
            return

        return 0.1*self.siteMap.scale*value

#___________________________________________________________________________________________________ text
    def text(self, textString, insert, scene =True, groupId =None, **extra):
        """ Adds a text of a given fill at the given insertion point. """

        if not self.siteMapReady:
            return

        # convert from scene coordinates to map coordinates as necessary
        if scene:
            insert = self.projectToMap(insert)

        # convert from (scaled) mm to px
        insert = (self.pxPerMm*insert[0], self.pxPerMm*insert[1])

        # create the object
        obj = self._drawing.text(textString, insert, **extra)

        # and add it to either a specific group or to the default _drawing
        if groupId:
            group = self.groups[groupId]
            if group:
                group.add(obj)
            else:
                print('text:  %s is not a valid group ID' % groupId)
                return
        else:

            self._drawing.add(obj)

#___________________________________________________________________________________________________ use
    def use(self, id, center,
            scene =True, rotation =None, rotationCenter =None, scale =None, scaleY =None, **extra):
        """ Groups are given an id when created.  This id is used to create instances that are
            added to the Cadence drawing (and hence the SVG file) by this function.  The group is
            placed in the drawing using map coordinates.  Rotation defaults to about the origin. A
            preferred usage would be to create a create a group relative to (i.e., centered upon)
            the origin, so that the rotation pivot is naturally at the group's center.  The group
            is then placed at the specfified center location (which either in map coordinates or
            scene coordinates depending upon the kwarg scene).  For example, for a group 'g' to
            be placed at some point (xScene, yScene) and rotated 45 degrees, and with 2x scale:
                use('g', (xScene, yScene), scene=True, rotation=45, scale = 2) """

        if not self.siteMapReady:
            return

        if scene:
            center = self.projectToMap(center)
            tx = self.pxPerMm*center[0]
            ty = self.pxPerMm*center[1]
        else:
            tx = center[0]
            ty = center[1]

        element = self.groups[id]
        if not element:
            print('CadenceDrawing.use:  %s is not a valid group id' % id)
            return

        instance = self._drawing.use(element, **extra)
        instance.translate(tx, ty)

        # right-handed coordinates, hence postive counterclockwise about y axis
        if rotation:
            instance.rotate(-rotation, center=rotationCenter)

        # scale anisotropically only if scaleY is specified, else isotropically
        if scale:
            if not scaleY:
                scaleY = scale
            instance.scale(scale, sy=scaleY)

        self._drawing.add(instance)

