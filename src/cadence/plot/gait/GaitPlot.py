__author__ = 'kent'

# from other packages
import pylab as plt

# from project
from cadence.shared.io.CadenceData import CadenceData
from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.enum.TargetsEnum import TargetsEnum

class GaitPlot(object):
    LH = 0.8
    LF = 0.6
    RF = 0.4
    RH = 0.2
    BACKGROUND_COLOR = 'gray'

    def __init__(self, name):
        self.channel_LH = None
        self.channel_LF = None
        self.channel_RF = None
        self.channel_RH = None
        self._name      = name
        self._figure    = plt.figure(name, figsize=(8, 3))
        self._ax1       = plt.subplot(111)
        self._cd        = None
        self._startTime = None
        self._stopTime  = None
        self._lineWidth = 10


#===================================================================================================
#                                                                                   G E T / S E T



#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ loadData

    def loadData(self, fileName ="GaitGenerator/PH-0_F-50_H-50.cadence"):
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
        return True

#___________________________________________________________________________________________________ mapValueToColor

    def mapValueToColor(self, v):
        return 'sandybrown' if v else 'lightslategray'

#___________________________________________________________________________________________________ plotChannel
    def plotChannel(self, channel, y, lineWidth):
        prevKey = channel.keys[0]

        for key in channel.keys[1:]:
            self._ax1.plot([prevKey.time, key.time], [y, y], linewidth=lineWidth, color=self.mapValueToColor(key.value))
            prevKey = key

#___________________________________________________________________________________________________ labelChannels

    def labelChannels(self):
        positions = [GaitPlot.LH, GaitPlot.LF, GaitPlot.RF, GaitPlot.RH]
        labels    = ('Left Hind', 'Left Fore', 'Right Fore','Right Hind')
        plt.yticks(positions, labels)

#___________________________________________________________________________________________________ testOverlayCurve

    def testOverlayCurve(self, color, amplitude=0.5):
        t = []
        for key in self.channel_LH.keys:
            t.append(key.time)
        print plt.sin(plt.pi*2*t[3])

        #s = plt.sin(2*plt.pi*t) WHY DOESN'T THIS COMPILE???  AS A WORKAROUND, I DID EXPLICIT ITERATION:
        s = []
        for time in t:
            s.append(0.5 + amplitude*plt.sin(2*plt.pi*time/100))

        plt.figure(self._name)
        plt.axes(self._ax1)
        self._ax1.plot(t, s, linewidth=1.0, color=color)
        return True


#___________________________________________________________________________________________________ plotData

    def plotData(self):
        plt.figure(self._name)
        plt.axes(self._ax1)

        # this method presumes that all channels have the same start and stop times; using LF channel_ as representative
        self._startTime = self.channel_LF.keys[ 0].time
        self._stopTime  = self.channel_LF.keys[-1].time

        self.plotChannel(self.channel_LH, GaitPlot.LH, self._lineWidth)
        self.plotChannel(self.channel_LF, GaitPlot.LF, self._lineWidth)
        self.plotChannel(self.channel_RF, GaitPlot.RF, self._lineWidth)
        self.plotChannel(self.channel_RH, GaitPlot.RH, self._lineWidth)

        rect = self._ax1.patch
        rect.set_facecolor(GaitPlot.BACKGROUND_COLOR)

        plt.xlim([self._startTime, self._stopTime])
        plt.ylim(0, 1)
        self.labelChannels()
        return True

#___________________________________________________________________________________________________ show
    def show(self):
        plt.figure(self._name)
        plt.show()
        return True
