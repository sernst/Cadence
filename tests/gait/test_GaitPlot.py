__author__ = 'kent'

import sys
import numpy as np
import pylab as plt


from cadence.plot.gait.GaitPlot import GaitPlot

gp = GaitPlot(3, 8, 8)

#___________________________________________________________________________________________________ loadData test
#if gp.loadGait("GaitGenerator/PH-50_F-50_H-50.cadence"):
if gp.loadGait("GaitGenerator/PH-0_F-50_H-50.cadence"):
#if gp.loadGait("GaitGenerator/PH-20_F-70_H-70.cadence"):
    print 'SUCCESS: GaitPlot.loadData()'
else:
    print 'FAILED: GaitPlot.loadData()'
    sys.exit(1)

# note that you can get a list of named color maps by colorNames()
# print gp.colorMapNames()

gp.setColorMap('gray') # choose a monochrome color map

gp.setPlotInterval(0.0, 24.0)
#___________________________________________________________________________________________________ plotGait test

# plotGait creates a gait plot without colorizing for support; use plotGait2 to show colors
if gp.plotGait2(1):
    print 'SUCCESS: GaitPlot.plotGait()'
else:
    print 'FAILED: GaitPlot.plotGait()'
    sys.exit(1)

#___________________________________________________________________________________________________ plotCurve test
# this data series has x values 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, and 0.9, and is piecewise-linearly plotted
# between these data values:

amplitude = 0.5
values    = []
times     = np.arange(0.0, 24, 1.0)

for t in times:
    values.append(0.5 + amplitude*plt.sin(2*plt.pi*t/10.0))

# note that you can get a list of named colors by colorNames()
#print gp.colorNames()

gp.clearGraph(2, 'darkslateblue')
gp.plotCurve(times, values, 2, "white", 1.0)

gp.clearGraph(3, 'blue')
gp.plotCurve(times, values, 3, "red", 5.0)

gp.show()

