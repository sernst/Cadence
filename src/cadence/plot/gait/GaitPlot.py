# GaitPlot.py
# (C)2012 http://GaitGenerator.threeaddone.com
# Kent A. Stevens

import pylab as plt


from cadence.shared.io.CadenceData import CadenceData
from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.enum.TargetsEnum import TargetsEnum


#___________________________________________________________________________________________________ GaitPlot
class GaitPlot(object):


#===================================================================================================
#                                                                                       C L A S S

    LH = 0.8
    LF = 0.6
    RF = 0.4
    RH = 0.2
    BACKGROUND_COLOR = 'gray'

#___________________________________________________________________________________________________ __init__

    def __init__(self, name, width=8, height=4):
        self.channel_LH  = None
        self.channel_LF  = None
        self.channel_RF  = None
        self.channel_RH  = None
        self._name       = name
        self._figure     = plt.figure(name, figsize=(width, height))
        self._upperGraph = plt.subplot(2, 1, 1)
        self._lowerGraph = plt.subplot(2, 1, 2)
        rect = self._upperGraph.patch
        rect.set_facecolor(GaitPlot.BACKGROUND_COLOR)
        rect = self._lowerGraph.patch
        rect.set_facecolor(GaitPlot.BACKGROUND_COLOR)

        self._channelStartTime = None
        self._channelStopTime  = None
        self._plotStartTime    = None
        self._plotStopTime     = None
        self._lineWidth = 10


#===================================================================================================
#                                                                                   G E T / S E T


#__________________________________________________________________________________________________GS: upperAxes
    @property
    def upperGraph(self):
        return self._upperGraph

#__________________________________________________________________________________________________GS: lowerAxes
    @property
    def lowerGraph(self):
        return self._lowerGraph

#__________________________________________________________________________________________________GS: channelStartTime
    @property
    def channelStartTime(self):
        return self.channelStartTime

#__________________________________________________________________________________________________GS: channelStopTime
    @property
    def channelStopTime(self):
        return self.channelStopTime

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ setPlotInterval

    def setPlotInterval(self, startTime, stopTime):
        self._plotStartTime = startTime
        self._plotStopTime  = stopTime

#__________________________________________________________________________________________________loadGait

    def loadGait(self,
                 fileName ="GaitGenerator/PH-0_F-50_H-50.cadence"):
        """
        1) Loads the four GAIT_PHASE channels from the specified file
        2) sets channelStartTime and _channelStopTime based on the left hind limb channel
        3) sets the plot times to the overall channel times by default

        """
        self._cd = CadenceData()
        self._cd.loadFile(fileName)
        channel_s = self._cd.getChannelsByKind(ChannelsEnum.GAIT_PHASE) # get the four gait phase channel_s
        for c in channel_s:
            if   c.target == TargetsEnum.LEFT_HIND:  self.channel_LH = c
            elif c.target == TargetsEnum.LEFT_FORE:  self.channel_LF = c
            elif c.target == TargetsEnum.RIGHT_FORE: self.channel_RF = c
            elif c.target == TargetsEnum.RIGHT_HIND: self.channel_RH = c
            else:
                raise Exception, "Unknown Channel_ Target:  " + str(c.target)
        # this method presumes that all channels have the same start and stop times
        # hence we use the left hind limb (channel_LH) as representative

        self._channelStartTime = self.channel_LH.keys[ 0].time
        self._channelStopTime  = self.channel_LH.keys[-1].time
        self._plotStartTime    = self._channelStartTime
        self._plotStopTime     = self._channelStopTime

        return True

#___________________________________________________________________________________________________mapValueToColor

    def mapValueToColor(self, v):
        return 'sandybrown' if v else 'lightslategray'

#___________________________________________________________________________________________________plotChannel

    def plotChannel(self, channel, graph, y, lineWidth):
        plt.axes(graph)
        prevKey = channel.keys[0]

        for key in channel.keys[1:]:
            self._lowerGraph.plot([prevKey.time, key.time],
                                  [y, y],
                                  linewidth=lineWidth,
                                  color=self.mapValueToColor(key.value))
            prevKey = key




#___________________________________________________________________________________________________ plotGait

    def plotGait(self):
        plt.figure(self._name)
        plt.axes(self._lowerGraph)

        self.plotChannel(self.channel_LH, self._lowerGraph, GaitPlot.LH, self._lineWidth)
        self.plotChannel(self.channel_LF, self._lowerGraph, GaitPlot.LF, self._lineWidth)
        self.plotChannel(self.channel_RF, self._lowerGraph, GaitPlot.RF, self._lineWidth)
        self.plotChannel(self.channel_RH, self._lowerGraph, GaitPlot.RH, self._lineWidth)

#       rect = self._ax1.patch
#       rect.set_facecolor(GaitPlot.BACKGROUND_COLOR)

        plt.xlim([self._plotStartTime, self._plotStopTime])
        print "channel start time = %s; stop time = %s" % (self._channelStartTime, self._channelStopTime)
        print "plot start time = %s; stop time = %s" % (self._plotStartTime, self._plotStopTime)

        plt.ylim(0, 1)
        positions = [GaitPlot.LH, GaitPlot.LF, GaitPlot.RF, GaitPlot.RH]
        labels    = ('Left Hind', 'Left Fore', 'Right Fore','Right Hind')
        plt.yticks(positions, labels)
        return True

#___________________________________________________________________________________________________ clear
    def clearUpper(self):
        self._upperGraph.clear()
        return True

#___________________________________________________________________________________________________ show
    def show(self):
        plt.figure(self._name)
        plt.show()
        return True

#___________________________________________________________________________________________________testOverlayCurve

    def testOverlayCurve(self, graph, color, amplitude=0.5):
        plt.figure(self._name)
        plt.axes(graph)
        t = []
        for key in self.channel_LH.keys:
            t.append(key.time)

        #s = plt.sin(2*plt.pi*t) WHY DOESN'T THIS COMPILE???  AS A WORKAROUND, I DID EXPLICIT ITERATION:
        s = []
        for time in t:
            s.append(0.5 + amplitude*plt.sin(2*plt.pi*time/100))

        plt.figure(self._name)
        plt.axes(graph)
        graph.plot(t, s, linewidth=1.0, color=color)
        return True


