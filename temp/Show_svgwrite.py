from __future__ import print_function, absolute_import, unicode_literals, division

import svgwrite
from svgwrite import shapes, masking
from svgwrite import path as svg_path

def drawRing(filename, size, colorPalette, border, center, outerRadius, innerRadius):
    drawing = svgwrite.Drawing(filename=filename, size=('%spx' % size[0], '%spx' % size[1]))
    drawing.viewbox(0, 0, size[0], size[1])

    mask = drawing.defs.add(masking.Mask(id='hole'))
    mask.add(shapes.Rect((0, 0), size)).fill('white')
    mask.add(shapes.Circle(center.toTuple(), r=innerRadius - border)).fill('black')

    drawing.add(shapes.Circle(center.toTuple(), r=outerRadius + border, mask='url(#hole)'))

    start = 0.0
    for index in range(data):
        value = data[index]
        end = start + value
        color = colorPalette[index % len(colorPalette)]

        points = makeSegmentPath(start, end, outerRadius, innerRadius, center)
        cmds = [('M', points[0].x, points[0].y)]

        for p in points[1:]:
            cmds.append(('L', p.x, p.y))
        cmds.append('Z',)

        drawing.add(svg_path.Path(cmds)).fill(color)
        start = end

    drawing.save()
