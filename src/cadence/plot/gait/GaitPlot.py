# GaitPlot.py
# (C)2012 http://GaitGenerator.threeaddone.com
# Kent A. Stevens

import pylab as plt

from cadence.shared.io.CadenceData import CadenceData
from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.enum.TargetsEnum import TargetsEnum
from cadence.config.enum.GeneralConfigEnum import GeneralConfigEnum


#___________________________________________________________________________________________________ GaitPlot
class GaitPlot(object):

#===================================================================================================
#                                                                                   C L A S S
    """
    A GaitPlot instance can have multiple individual graphs arranged into a single column, one graph per row. The
    number of rows is determined at construction time, and defaults to 1. Multiple graphs are composed on
    successive rows, addressed numerically by row number (starting at one and increasing downward).  All graphs
    share a common specified width and are scaled to fit within the specified overall height of the GaitPlot figure.

    The GaitPlot class is designed for plotting Cadence GAIT_PHASE channel data, as loaded from a given Cadence
    data file. The duration of the data is stored in the read-only properties channelStartTime and channelStopTime,
    ase determined from the data.  By default all keys within this interval are plotted. A more restricted interval
    can be specified by setPlotInterval.

    The following indicates how to display two graphs within a GaitPlot, with a width of 8 inches and an overall
    height of 6 inches.
        gp = GaitPlot(2, 8, 6)
        gp.loadData(<fileName>)
        gp.setColorMap('rainbow')     # use one of the predefined color maps
        gp.setPlotInterval(0.0, 24.0) # only plot keys within the interval (0.0, 24.0)
        gp.plotGait(1)                # graph the GAIT_PHASE data in the top graph (other graphs will be below)
        gp.clearGraph(1, 'black')     # clear the top row's graph
        gp.plotCurve(1, xs, ys)       # plot a continuous curve into graph 1 from lists of x and y coordinates
        gp.save(<file>)               # save as a .png
        gp.show()                     # launch the display popup
    """
#___________________________________________________________________________________________________ __init__

    def __init__(self, rows=1, width=8, height=4):
        self._cd         = None
        self._channel_LH = None
        self._channel_LF = None
        self._channel_RF = None
        self._channel_RH = None
        self._colorMap   = None
        self._lineColor  = None
        self._background = None
        self._figureSize = None
        self._numberRows = rows
        self._figureSize = (width, height)
        self._figure     = plt.figure(figsize=self._figureSize)

        self._channelStartTime = None
        self._channelStopTime  = None
        self._plotStartTime    = None
        self._plotStopTime     = None

        self.setColorMap('Greys')
        self.setLineColor('sandybrown')

#===================================================================================================
#                                                                                   G E T / S E T

#__________________________________________________________________________________________________GS: channelStartTime
    @property
    def channelStartTime(self):
        return self._channelStartTime

#__________________________________________________________________________________________________GS: channelStopTime
    @property
    def channelStopTime(self):
        return self._channelStopTime

#__________________________________________________________________________________________________GS: plotStartTime
    @property
    def plotlStartTime(self):
        return self._plotStartTime

#__________________________________________________________________________________________________GS: plotStopTime
    @property
    def plotStopTime(self):
        return self._plotStopTime

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ loadGait

    def loadGait(self, fileName):
        """
        1) Loads the four GAIT_PHASE channels from the specified file
        2) sets _channelStartbTime and _channelStopTime based on the left hind limb channel
        3) sets _plotStart and _plotStopTime to the overall channel times by default
        """
        self._cd = CadenceData()
        self._cd.loadFile(fileName)
        channel_s = self._cd.getChannelsByKind(ChannelsEnum.GAIT_PHASE) # get the four gait phase channels
        for c in channel_s:
            if   c.target == TargetsEnum.LEFT_HIND:  self._channel_LH = c
            elif c.target == TargetsEnum.LEFT_FORE:  self._channel_LF = c
            elif c.target == TargetsEnum.RIGHT_FORE: self._channel_RF = c
            elif c.target == TargetsEnum.RIGHT_HIND: self._channel_RH = c
            else:
                raise Exception, "Unknown Channel_ Target:  " + str(c.target)

        # this method presumes that all channels have the same start and stop times
        # hence we use the left hind limb (channel_LH) as representative
        self._channelStartTime = self._channel_LH.keys[ 0].time
        self._channelStopTime  = self._channel_LH.keys[-1].time
        # and use that interval as the default plotting interval
        self.setPlotInterval(self._channelStartTime, self._channelStopTime)

        return True
    #___________________________________________________________________________________________________ setPlotInterval

    def setPlotInterval(self, startTime, stopTime):
        self._plotStartTime = startTime
        self._plotStopTime  = stopTime

    #___________________________________________________________________________________________________ setColorMap

    def setColorMap(self, name):
       self._colorMap = plt.get_cmap(name)

#___________________________________________________________________________________________________ setColorMap

    def setLineColor(self, name):
        self._lineColor = name

#___________________________________________________________________________________________________ setBackground

    def setBackground(self, name):
        self._background = name

#___________________________________________________________________________________________________mapValueToColor

    def mapValueToColor(self, v):
        return self._colorMap(v)

#___________________________________________________________________________________________________plotChannel

    def plotChannel(self, channel, graph, y, lineWidth=10):
        plt.axes(graph)
        prevKey = channel.keys[0]

        plt.xticks(plt.arange(self._plotStartTime, self._plotStopTime, 1.0))

        for key in channel.keys[1:]:
            if key.time >= self._plotStartTime and key.time <= self._plotStopTime:
                graph.plot([prevKey.time, key.time],
                           [y, y],
                           linewidth=lineWidth,
                           color=self.mapValueToColor(key.value))
            prevKey = key

#___________________________________________________________________________________________________ plotGait

    def plotGait(self, graphNumber=1, background='gray', lineWidth=10):
        graph = self._figure.add_subplot(self._numberRows, 1, graphNumber)

        self.setBackground(background)
        rect = graph.patch
        rect.set_facecolor(background)

        y_RH, y_RF, y_LF, y_LH = 0.2, 0.4, 0.6, 0.8

        self.plotChannel(self._channel_LH, graph, y_LH, lineWidth)
        self.plotChannel(self._channel_LF, graph, y_LF, lineWidth)
        self.plotChannel(self._channel_RF, graph, y_RF, lineWidth)
        self.plotChannel(self._channel_RH, graph, y_RH, lineWidth)

        plt.xlim([self._plotStartTime, self._plotStopTime])

        plt.ylim(0, 1)
        positions = (y_RH, y_RF, y_LF, y_LH)
        labels    = ('Right Hind', 'Right Fore', 'Left Fore','Left Hind')
  #      plt.xlim([self._plotStartTime, self._plotStopTime - 1])
        plt.yticks(positions, labels)
    #    plt.xticks(plt.arange(0.0, 24.0, 1.0))
        return True

#___________________________________________________________________________________________________ value

    def value(self, channel, time):
        prevKey = channel.keys[0]
        for key in channel.keys[1:]:
            if prevKey.time <= time and time <= key.time:
                return key.value
            prevKey = key
        return channel.keys[0].value

#___________________________________________________________________________________________________ values

    def values(self, channel, times):
        values = []

        for t in times:
            values.append(self.value(channel, t))
        return values

#___________________________________________________________________________________________________ plotGait_v2

    def plotGait2(self, graphNumber=1, background='gray', lineWidth=10):
        graph = self._figure.add_subplot(self._numberRows, 1, graphNumber)

        self.setBackground(background)
        rect = graph.patch
        rect.set_facecolor(background)

        y_RH, y_RF, y_LF, y_LH = 0.2, 0.4, 0.6, 0.8

        stop  = self._cd.configs.get(GeneralConfigEnum.STOP_TIME)
        start = self._cd.configs.get(GeneralConfigEnum.START_TIME)
        steps = self._cd.configs.get(GeneralConfigEnum.STEPS)
        delta = (stop - start)/steps

        times  = plt.arange(self._plotStartTime, self._plotStopTime, delta)
        valuesRH = self.values(self._channel_RH, times)
        valuesRF = self.values(self._channel_RF, times)
        valuesLF = self.values(self._channel_LF, times)
        valuesLH = self.values(self._channel_LH, times)

        self.setColorMap('RdYlGn')

        for i in range(len(times)):
            time  = times[i]
            lh, lf, rf, rh = valuesLH[i], valuesLF[i], valuesRF[i], valuesRH[i]

            if   lh and lf and rf and rh:                  support = 1.0
            elif (lh and rf and rh) or (lh and lf and rh): support = 0.95
            elif (lh and lf and rf) or (lf and rf and rh): support = 0.85
            elif lh and rh:                                support = 0.75
            elif (lh and rf) or (lf and rh):               support = 0.7
            elif lf and rf:                                support = 0.2
            elif (lh and lf) or (rf and rh):               support = 0.1
            else:                                          support = 0.0
            if support > 0.0:
                plt.axvspan(time - 2.0*delta, time, fc=self.mapValueToColor(support), ec='none')

        self.setColorMap('gray')
        self.plotChannel(self._channel_LH, graph, y_LH, lineWidth)
        self.plotChannel(self._channel_LF, graph, y_LF, lineWidth)
        self.plotChannel(self._channel_RF, graph, y_RF, lineWidth)
        self.plotChannel(self._channel_RH, graph, y_RH, lineWidth)

        plt.xlim([self._plotStartTime, self._plotStopTime - 1])

        plt.ylim(0, 1)
        positions = (y_RH, y_RF, y_LF, y_LH)
        labels    = ('Right Hind', 'Right Fore', 'Left Fore','Left Hind')
        plt.yticks(positions, labels)
        return True

    #___________________________________________________________________________________________________ clearGraph

    def clearGraph(self, graphNumber=1, background='black'):
        graph = self._figure.add_subplot(self._numberRows, 1, graphNumber)
        rect = graph.patch
        rect.set_facecolor(background)

#___________________________________________________________________________________________________ save

    def save(self, fileName, backgroundColor=None):
        """ Specifying backgroundColor overrides the GaitPlot's background color."""
        if backgroundColor == None:
            backgroundColor = self._figure.get_facecolor()
        self._figure.saveFig(fileName, backgroundColor=backgroundColor)

#___________________________________________________________________________________________________plotCurve

    def plotCurve(self, xValues, yValues, graphNumber, color='black', lineWidth=1.0):
        graph = self._figure.add_subplot(self._numberRows, 1, graphNumber)
        graph.plot(xValues, yValues, linewidth=lineWidth, color=color)
        graph.xaxis.grid(color='darkgray')
        plt.xlim([self._plotStartTime, self._plotStopTime-1])
       # plt.xticks(xValues)
        return True

#___________________________________________________________________________________________________ show

    def show(self):
        plt.show()
        return True

#___________________________________________________________________________________________________ colorNames

    def colorNames(self):
        """ These are named colors available in matplotlib"""
        return {
        'aliceblue':'#F0F8FF','antiquewhite':'#FAEBD7','aqua':'#00FFFF','aquamarine':'#7FFFD4','azure':'#F0FFFF',
        'beige':'#F5F5DC','bisque':'#FFE4C4','black':'#000000','blanchedalmond':'#FFEBCD','blue':'#0000FF',
        'blueviolet':'#8A2BE2','brown':'#A52A2A','burlywood':'#DEB887','cadetblue':'#5F9EA0','chartreuse':'#7FFF00',
        'chocolate':'#D2691E','coral':'#FF7F50','cornflowerblue':'#6495ED','cornsilk':'#FFF8DC','crimson':'#DC143C',
        'cyan':'#00FFFF', 'darkblue':'#00008B', 'darkcyan':'#008B8B', 'darkgoldenrod':'#B8860B','darkgray':'#A9A9A9',
        'darkgreen':'#006400', 'darkkhaki':'#BDB76B', 'darkmagenta':'#8B008B','darkolivegreen':'#556B2F',
        'darkorange':'#FF8C00', 'darkorchid':'#9932CC', 'darkred':'#8B0000','darksalmon':'#E9967A',
        'darkseagreen':'#8FBC8F', 'darkslateblue':'#483D8B', 'darkslategray':'#2F4F4F', 'darkturquoise':'#00CED1',
        'darkviolet':'#9400D3', 'deeppink':'#FF1493', 'deepskyblue':'#00BFFF', 'dimgray':'#696969',
        'dodgerblue':'#1E90FF', 'firebrick':'#B22222','floralwhite':'#FFFAF0', 'forestgreen':'#228B22',
        'fuchsia':'#FF00FF', 'gainsboro':'#DCDCDC', 'ghostwhite':'#F8F8FF', 'gold':'#FFD700', 'goldenrod':'#DAA520',
        'gray':'#808080','green':'#008000', 'greenyellow':'#ADFF2F', 'honeydew':'#F0FFF0', 'hotpink':'#FF69B4',
        'indianred':'#CD5C5C', 'indigo':'#4B0082', 'ivory':'#FFFFF0', 'khaki':'#F0E68C', 'lavender':'#E6E6FA',
        'lavenderblush':'#FFF0F5', 'lawngreen':'#7CFC00', 'lemonchiffon':'#FFFACD', 'lightblue':'#ADD8E6',
        'lightcoral':'#F08080', 'lightcyan':'#E0FFFF', 'lightgoldenrodyellow':'#FAFAD2', 'lightgreen':'#90EE90',
        'lightgray':'#D3D3D3', 'lightpink':'#FFB6C1', 'lightsalmon':'#FFA07A', 'lightseagreen':'#20B2AA',
        'lightskyblue':'#87CEFA', 'lightslategray':'#778899', 'lightsteelblue':'#B0C4DE', 'lightyellow':'#FFFFE0',
        'lime':'#00FF00', 'limegreen':'#32CD32', 'linen':'#FAF0E6', 'magenta':'#FF00FF', 'maroon':'#800000',
        'mediumaquamarine':'#66CDAA', 'mediumblue':'#0000CD', 'mediumorchid':'#BA55D3', 'mediumpurple':'#9370DB',
        'mediumseagreen':'#3CB371', 'mediumslateblue':'#7B68EE', 'mediumspringgreen':'#00FA9A',
        'mediumturquoise':'#48D1CC', 'mediumvioletred':'#C71585', 'midnightblue':'#191970', 'mintcream':'#F5FFFA',
        'mistyrose':'#FFE4E1', 'moccasin':'#FFE4B5', 'navajowhite':'#FFDEAD', 'navy':'#000080', 'oldlace':'#FDF5E6',
        'olive':'#808000', 'olivedrab':'#6B8E23', 'orange':'#FFA500', 'orangered':'#FF4500', 'orchid':'#DA70D6',
        'palegoldenrod':'#EEE8AA', 'palegreen':'#98FB98', 'palevioletred':'#AFEEEE', 'papayawhip':'#FFEFD5',
        'peachpuff':'#FFDAB9', 'peru':'#CD853F', 'pink':'#FFC0CB', 'plum':'#DDA0DD', 'powderblue':'#B0E0E6',
        'purple':'#800080', 'red':'#FF0000', 'rosybrown':'#BC8F8F', 'royalblue':'#4169E1', 'saddlebrown':'#8B4513',
        'salmon':'#FA8072', 'sandybrown':'#FAA460', 'seagreen':'#2E8B57', 'seashell':'#FFF5EE', 'sienna':'#A0522D',
        'silver':'#C0C0C0',  'skyblue':'#87CEEB', 'slateblue':'#6A5ACD', 'slategray':'#708090', 'snow':'#FFFAFA',
        'springgreen':'#00FF7F', 'steelblue':'#4682B4', 'tan':'#D2B48C', 'teal':'#008080', 'thistle':'#D8BFD8',
        'tomato':'#FF6347', 'turquoise':'#40E0D0', 'violet':'#EE82EE', 'wheat':'#F5DEB3', 'white':'#FFFFFF',
        'whitesmoke':'#F5F5F5', 'yellow':'#FFFF00', 'yellowgreen':'#9ACD32',
        }

#___________________________________________________________________________________________________ colorMapNames
    def colorMapNames(self):
        """ These are named color maps available in matplotlib"""
        maps = [m for m in plt.cm.datad if not m.endswith("_r")]
        return maps



