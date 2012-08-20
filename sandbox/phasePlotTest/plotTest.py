__author__ = 'kent'


# from other packages
import pylab as plt

# from project
from cadence.shared.io.CadenceData import CadenceData
from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.enum.TargetsEnum import TargetsEnum

class PlotTest(object):
    LH = 0.8
    LF = 0.6
    RF = 0.4
    RH = 0.2
    BACKGROUND_COLOR = 'lightslategray'

    def __init__(self, name):
        self.channelLH = None
        self.channelLF = None
        self.channelRF = None
        self.channelRH = None
        self._name     = name
        self._figure   = plt.figure(name, figsize=(8, 3))
        self._ax1      = plt.subplot(111)
        self._cd       = None

        
    def loadData(self, fileName ="GaitGenerator/PH-0_F-50_H-50.cadence"):
        self._cd = CadenceData()
        self._cd.loadFile(fileName)


    def mapValueToColor(self, v):
        return 'yellow' if v else 'blue'
        
    def plotData(self):
        plt.figure(self._name)
        plt.axes(self._ax1)
        channels = self._cd.getChannelsByKind(ChannelsEnum.GAIT_PHASE) # get the four gait phase channels
        for c in channels:
            if   c.target == TargetsEnum.LEFT_HIND:  self.channelLH = c
            elif c.target == TargetsEnum.LEFT_FORE:  self.channelLF = c
            elif c.target == TargetsEnum.RIGHT_FORE: self.channelRF = c
            elif c.target == TargetsEnum.RIGHT_HIND: self.channelRH = c
            else:
                raise Exception, "Unknown Channel Target:  " + str(c.target)

        prevKey   = self.channelLF.keys[0]
        startTime = prevKey.time
        stopTime  = self.channelLF.keys[-1].time

        for key in self.channelRF.keys[1:]:
            self._ax1.plot([prevKey.time, key.time], [PlotTest.LH, PlotTest.LH], linewidth=10, color=self.mapValueToColor(prevKey.value))
            prevKey = key

        rect = self._ax1.patch
        rect.set_facecolor(PlotTest.BACKGROUND_COLOR)

        plt.xlim([startTime, stopTime])
        plt.show()

pt = PlotTest('1')
pt.loadData()
pt.plotData()





