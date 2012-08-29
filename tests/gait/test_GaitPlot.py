__author__ = 'kent'

import sys

from cadence.plot.gait.GaitPlot import GaitPlot

gp = GaitPlot('1', 10, 8)

#___________________________________________________________________________________________________ loadData test
if gp.loadGait():
    print 'SUCCESS: GaitPlot.loadData()'
else:
    print 'FAILED: GaitPlot.loadData()'
    sys.exit(1)

#___________________________________________________________________________________________________ plotGait test
if gp.plotGait():
    print 'SUCCESS: GaitPlot.plotGait()'
else:
    print 'FAILED: GaitPlot.plotGait()'
    sys.exit(1)

#___________________________________________________________________________________________________ overlayCurve test
if gp.testOverlayCurve(gp.lowerGraph, 'white', 0.5) and gp.testOverlayCurve(gp.upperGraph, 'green', 0.15):
    print 'SUCCESS: GaitPlot.testOverlayCurve()'
else:
    print 'FAILED: GaitPlot.testOverlayCurve()'
    sys.exit(1)

gp.testOverlayCurve(gp.upperGraph, 'blue', 0.75)
gp.show()

