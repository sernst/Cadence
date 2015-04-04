# test_LineSegment2D.py [UNIT TEST]
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math
import random
import unittest
from pyaid.dict.DictUtils import DictUtils

from pyaid.number.Angle import Angle

from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.analysis.shared.PositionValue2D import PositionValue2D

#*************************************************************************************************** test_LineSegment2D
class test_LineSegment2D(unittest.TestCase):

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ setUp
    def setUp(self):
        pass

#___________________________________________________________________________________________________ test_getParametricPosition
    def test_getParametricPosition(self):
        """getParametricPosition doc..."""
        start = PositionValue2D(0.0, 0.0, 0.1, 0.1)
        end   = PositionValue2D(2.0, 2.0, 0.1, 0.1)
        line  = LineSegment2D(start, end)

        result = line.getParametricPosition(0.5)
        self.assertAlmostEqual(result.x, 1.0, msg='Invalid x value %s' % result.x)
        self.assertAlmostEqual(result.y, 1.0, msg='Invalid y value %s' % result.y)

        result = line.getParametricPosition(2.0, clamp=False)
        self.assertAlmostEqual(result.x, 4.0, msg='Invalid x value %s' % result.x)
        self.assertAlmostEqual(result.y, 4.0, msg='Invalid y value %s' % result.y)

#___________________________________________________________________________________________________ test_adjustPointAlongLine
    def test_adjustPointAlongLine(self):
        """test_ doc..."""
        start = PositionValue2D(0.0, 0.0, 0.1, 0.1)
        end   = PositionValue2D(2.0, 2.0, 0.1, 0.1)
        line  = LineSegment2D(start, end)
        point = start.clone()

        result = line.adjustPointAlongLine(point, math.sqrt(2.0), inPlace=False)
        self.assertAlmostEqual(result.x, 1.0, msg='Invalid x value %s' % result.x)
        self.assertAlmostEqual(result.y, 1.0, msg='Invalid y value %s' % result.y)

        for i in range(1000):
            offset = random.uniform(0.1, 1000.0)
            point  = line.getParametricPosition(random.uniform(0.0, 1.0))
            result = line.adjustPointAlongLine(point, offset, inPlace=False)

            coordinate = math.sqrt(0.5*offset*offset)
            self.assertAlmostEqual(
                result.x, point.x + coordinate,
                msg='Invalid x value %s' % result.x)

            self.assertAlmostEqual(
                result.y, point.y + coordinate,
                msg='Invalid y value %s' % result.y)

#___________________________________________________________________________________________________ test_closestPointOnLine
    def test_closestPointOnLine(self):
        """ doc... """
        count = 5000
        bound = 10000.0

        for i in range(count):
            start = PositionValue2D(
                x=random.uniform(-bound, bound),
                y=random.uniform(-bound, bound),
                xUnc=0.1,
                yUnc=0.1)

            end = PositionValue2D(
                x=random.uniform(-bound, bound) + start.x,
                y=random.uniform(-bound, bound) + start.y,
                xUnc=0.1,
                yUnc=0.1)

            line = LineSegment2D(start, end)
            if not line.isValid:
                continue

            target = line.getParametricPosition(random.uniform(0.0, 1.0))
            offset = random.uniform(1.0, bound)
            point  = line.adjustPointAlongLine(target, offset, inPlace=False)

            debug  = {
                'POINT':point,      'TARGET':target,
                'OFFSET':offset,    'DISTANCE':point.distanceTo(target) }

            self.assertAlmostEqual(
                offset, point.distanceTo(target).raw,
                msg='Invalid offset distance:\n'
                    + DictUtils.prettyPrint(debug, delimiter='\n'))

            point.rotate(Angle(degrees=90.0*random.choice([1.0, -1.0])), target)

            self.assertAlmostEqual(
                offset, point.distanceTo(target).raw,
                msg='Invalid rotated offset distance:\n'
                    + DictUtils.prettyPrint(debug, delimiter='\n'))

            pointOnLine = line.closestPointOnLine(point)
            xUnc = math.sqrt(pointOnLine.xUnc*pointOnLine.xUnc + target.xUnc*target.xUnc)
            yUnc = math.sqrt(pointOnLine.yUnc*pointOnLine.yUnc + target.yUnc*target.yUnc)
            debug = {
                'POINT':point,  'RESULT':pointOnLine,
                'INDEX':i,      'TARGET':target,
                'START':start,  'END':end,
                'X_UNC':xUnc,   'Y_UNC':yUnc }

            self.assertAlmostEqual(
                pointOnLine.x, target.x, delta=2.0*xUnc,
                msg='BAD RESULT [X]:\n' + DictUtils.prettyPrint(debug, delimiter='\n'))

            self.assertAlmostEqual(
                pointOnLine.y, target.y, delta=2.0*yUnc,
                msg='BAD RESULT [Y]:\n' + DictUtils.prettyPrint(debug, delimiter='\n'))

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(test_LineSegment2D)
    unittest.TextTestRunner(verbosity=2).run(suite)



