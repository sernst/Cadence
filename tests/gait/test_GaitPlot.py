__author__ = 'kent'

import sys

from cadence.plot.gait.GaitPlot import GaitPlot

pt = GaitPlot('1')

if pt.loadData():
    print 'SUCCESS: GaitPlot.loadData()'
else:
    print 'FAILED: GaitPlot.loadData()'
    sys.exit(1)


if pt.plotData():
    print 'SUCCESS: GaitPlot.plotData()'
else:
    print 'FAILED: GaitPlot.plotData()'
    sys.exit(1)



