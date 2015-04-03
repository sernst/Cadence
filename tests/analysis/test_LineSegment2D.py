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

#___________________________________________________________________________________________________ test_closestPointOnLine
    def test_closestPointOnLine(self):
        """ doc... """

        for i in range(1000):
            origin = PositionValue2D(1.0, 1.0)
            angle = Angle(degrees=random.uniform(-1000.0, 1000.0))
            # angle = Angle(degrees=-674.528925361)

            start = PositionValue2D(0.0, 0.0, 0.1, 0.1)
            start.rotate(angle, origin=origin)

            end = PositionValue2D(2.0, 2.0, 0.1, 0.1)
            end.rotate(angle, origin=origin)

            point = PositionValue2D(2.0, 0.0, 0.1, 0.1)
            point.rotate(angle, origin=origin)

            line = LineSegment2D(start, end)

            # Catches any issues where an incorrect rotation in a point value changes the length
            # of the line instance
            self.assertAlmostEqual(line.length.raw, math.sqrt(8.0), msg='Incorrect line length')

            pointOnLine = line.closestPointOnLine(point)
            debug = {
                'ANGLE':angle, 'RAW_ANGLE':angle.degrees,
                'POINT':point, 'RESULT':pointOnLine,
                'START':start, 'END':end }

            self.assertAlmostEqual(
                pointOnLine.x, 1.0,
                msg='BAD RESULT:\n' + DictUtils.prettyPrint(debug, delimiter='\n'))

            self.assertAlmostEqual(
                pointOnLine.y, 1.0,
                msg='BAD RESULT:\n' + DictUtils.prettyPrint(debug, delimiter='\n'))

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(test_LineSegment2D)
    unittest.TextTestRunner(verbosity=2).run(suite)



