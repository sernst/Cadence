
from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.shared.LineSegment2D import LineSegment2D
from pyaid.number.PositionValue2D import PositionValue2D

p1 = PositionValue2D(0.0, 0.0, 0.1, 0.1)
p2 = PositionValue2D(4.0, 0.0, 0.1, 0.1)
line = LineSegment2D(p1, p2)
length = line.length.value
print('L0:', length)
line.postExtendLine(10.0)
print('[TEST]: Post Extend Line %s' % 'PASSED' if line.length.value == (length + 10.0) else 'FAILED')

length = line.length.value
print('L1:', length)
line.preExtendLine(10.0)
print('[TEST]: Pre Extend Line %s' % 'PASSED' if line.length.value == (length + 10.0) else 'FAILED')

print(line.start.x, line.start.y, '|', line.end.x, line.end.y)
length = line.length.value
print('L2:', length)

point = PositionValue2D(3.0, 10.0, 0.1, 0.1)
distance = line.distanceToPoint(point)
print('DISTANCE:', distance)
