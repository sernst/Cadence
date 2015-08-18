# test_PositionValue2D.py [UNIT TEST]
# (C) 2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math
import random
import unittest

from pyaid.number.Angle import Angle

from cadence.analysis.shared.PositionValue2D import PositionValue2D

#*************************************************************************************************** test_PositionValue2D
class test_PositionValue2D(unittest.TestCase):

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def setUp(self):
        pass

#_______________________________________________________________________________
    def test_angleBetween(self):
        """test_angleBetween doc..."""
        p1 = PositionValue2D(2.0, 0.0, 0.1, 0.1)
        p2 = PositionValue2D(0.0, 2.0, 0.1, 0.1)

        a = p1.angleBetween(p2)
        self.assertAlmostEquals(a.degrees, 90.0, 'Invalid angle between')

#_______________________________________________________________________________
    def test_rotate(self):
        HALF_SQRT_2 = 0.5*math.sqrt(2.0)
        HALF_SQRT_3 = 0.5*math.sqrt(3.0)

        tests = [
            (90.0, 0.0, 1.0), (-90.0, 0.0, -1.0),
            (180.0, -1.0, 0.0), (-180.0, -1.0, 0.0),
            (270.0, 0.0, -1.0), (-270.0, 0.0, 1.0),
            (360.0, 1.0, 0.0), (-360.0, 1.0, 0.0),
            (45.0, HALF_SQRT_2, HALF_SQRT_2), (-45.0, HALF_SQRT_2, -HALF_SQRT_2),
            (315.0, HALF_SQRT_2, -HALF_SQRT_2), (-315.0, HALF_SQRT_2, HALF_SQRT_2),
            (30.0, HALF_SQRT_3, 0.5), (-30.0, HALF_SQRT_3, -0.5),
            (330.0, HALF_SQRT_3, -0.5), (-330.0, HALF_SQRT_3, 0.5) ]

        for test in tests:
            radius = random.uniform(0.001, 1000.0)
            p = PositionValue2D(radius, 0.0, 0.25, 0.25)

            p.rotate(Angle(degrees=test[0]))
            self.assertAlmostEqual(p.x, radius*test[1])
            self.assertAlmostEqual(p.y, radius*test[2])

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(test_PositionValue2D)
    unittest.TextTestRunner(verbosity=2).run(suite)



