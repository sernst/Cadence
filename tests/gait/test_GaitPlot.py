__author__ = 'kent'

import sys

from cadence.plot.gait.GaitPlot import GaitPlot

gp = GaitPlot('1')

#___________________________________________________________________________________________________ loadData test
if gp.loadData():
    print 'SUCCESS: GaitPlot.loadData()'
else:
    print 'FAILED: GaitPlot.loadData()'
    sys.exit(1)

#___________________________________________________________________________________________________ plotData test
if gp.plotData():
    print 'SUCCESS: GaitPlot.plotData()'
else:
    print 'FAILED: GaitPlot.plotData()'
    sys.exit(1)

#___________________________________________________________________________________________________ overlayCurve test
if gp.testOverlayCurve('white') and gp.testOverlayCurve('green', 0.25):
    print 'SUCCESS: GaitPlot.testOverlayCurve()'
else:
    print 'FAILED: GaitPlot.testOverlayCurve()'
    sys.exit(1)

gp.show()


