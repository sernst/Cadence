# DeviationsStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import numpy as np
from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils
from pyaid.time.TimeUtils import TimeUtils

from cadence.analysis.AnalysisStage import AnalysisStage


#*************************************************************************************************** DeviationsStage
class DeviationsStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of DeviationsStage."""
        super(DeviationsStage, self).__init__(key, owner, **kwargs)
        self._paths = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: widths
    @property
    def entries(self):
        return self.cache.get('entries')

#___________________________________________________________________________________________________ GS: noWidths
    @property
    def noWidths(self):
        return self.cache.get('noWidths', 0)
    @noWidths.setter
    def noWidths(self, value):
        self.cache.set('noWidths', value)

#___________________________________________________________________________________________________ GS: noLengths
    @property
    def noLengths(self):
        return self.cache.get('noLengths', 0)
    @noLengths.setter
    def noLengths(self, value):
        self.cache.set('noLengths', value)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preDeviations
    def _preAnalyze(self):
        """_preDeviations doc..."""
        self.cache.set('entries', [])
        self.cache.set('noWidth', 0)
        self.cache.set('noLength', 0)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """Doc..."""
        data = dict(track=track)

        w  = track.width
        wm = track.widthMeasured

        if not wm:
            self.noWidths += 1
        else:
            d = w - wm
            data['wDev'] = d/wm
            data['wDelta'] = abs(d)/track.widthUncertainty

        l  = track.length
        lm = track.lengthMeasured
        if not lm:
            self.noLengths += 1
        else:
            d = l - lm
            data['lDev'] = d/lm
            data['lDelta'] = abs(d)/track.lengthUncertainty

        self.entries.append(data)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        self._paths = []

        outputHeader = [
            'DEVIATION INTEGRITY ANALYSIS',
            'Run on %s' % TimeUtils.toZuluFormat().replace('T', ' at '),
            'Processed %s tracks' % len(self.entries),
            '%s tracks with no measured width' % self.cache.get('noWidths'),
            '%s tracks with no measured length' % self.cache.get('noLengths') ]
        self.logger.write('\n'.join(outputHeader))

        self.logger.write('='*80 + '\nFRACTIONAL ERROR (Measured vs Entered)')
        self._process('Error', 'wDev', 'lDev')

        self.logger.write('='*80 + '\nFRACTIONAL UNCERTAINTY ERROR')
        self._process('Uncertainty Error', 'wDelta', 'wDelta', absoluteOnly=True)

        self.mergePdfs(self._paths)

#___________________________________________________________________________________________________ _process
    def _process(self, label, widthKey, lengthKey, absoluteOnly =False):
        """_processDeviations doc..."""
        pl  = self.plot
        ws  = []
        ls  = []
        w2D = []
        l2D = []

        for entry in self.entries:
            if widthKey in entry:
                ws.append(entry[widthKey])
                if lengthKey in entry:
                    w2D.append(entry[widthKey])

            if lengthKey in entry:
                ls.append(entry[lengthKey])
                if widthKey in entry:
                    l2D.append(entry[lengthKey])

        plotList = [
            ('widths', ws, 'Width', 'b'),
            ('lengths', ls, 'Length', 'r')]


        wRes = self.getMeanAndDeviation(ws, 'Width %ss' % label)
        lRes = self.getMeanAndDeviation(ls, 'Length %ss' % label)

        for data in plotList:
            if not absoluteOnly:
                d = data[1]
                self._paths.append(self._makePlot(label, d, data, histRange=(-1.0, 1.0)))
                self._paths.append(self._makePlot(label, d, data, isLog=True, histRange=(-1.0, 1.0)))

            # noinspection PyUnresolvedReferences
            d = np.absolute(np.array(data[1]))
            self._paths.append(self._makePlot('Absolute ' + label, d, data, histRange=(0.0, 1.0)))
            self._paths.append(self._makePlot(
                'Absolute ' + label, d, data, isLog=True, histRange=(0.0, 1.0)))

        self.owner.createFigure('twoD')
        pl.hist2d(w2D, l2D, bins=20, range=([-1, 1], [-1, 1]))
        pl.title('2D %s Distribution' % label)
        pl.xlabel('Width %s' % label)
        pl.ylabel('Length %s' % label)
        pl.xlim(-1.0, 1.0)
        pl.ylim(-1.0, 1.0)
        path = self.getTempPath('%s.pdf' % StringUtils.getRandomString(16), isFile=True)
        self.owner.saveFigure('twoD', path)
        self._paths.append(path)

        count = 0
        for entry in self.entries:
            widthDevSigma  = NumericUtils.roundToOrder(abs(entry.get(widthKey, 0.0)/wRes.std), -2)
            lengthDevSigma = NumericUtils.roundToOrder(abs(entry.get(lengthKey, 0.0)/lRes.std), -1)
            if widthDevSigma > 2.0 or lengthDevSigma > 2.0:
                count += 1
                track = entry['track']
                self.logger.write('  * %s%s%s' % (
                    StringUtils.extendToLength(track.fingerprint, 32),
                    StringUtils.extendToLength('(%s, %s)' % (widthDevSigma, lengthDevSigma), 16),
                    track.uid))

        percentage = NumericUtils.roundToOrder(100.0*float(count)/float(len(self.entries)), -2)
        self.logger.write('%s significant %ss (%s%%)' % (count, label.lower(), percentage))
        if percentage > (100.0 - 95.45):
            self.logger.write(
                '[WARNING]: Large deviation count exceeds normal distribution expectations.')

#___________________________________________________________________________________________________ _makePlot
    def _makePlot(self, label, data, attrs, isLog =False, histRange =None):
        """_makePlot doc..."""

        pl = self.plot
        self.owner.createFigure(attrs[0])

        pl.hist(data, 31, range=histRange, log=isLog, facecolor=attrs[3], alpha=0.75)
        pl.title('%s %s Distribution%s' % (attrs[2], label, ' (log)' if isLog else ''))
        pl.xlabel('Deviation')
        pl.ylabel('Frequency')
        pl.grid(True)

        axis = pl.gca()
        xlims = axis.get_xlim()
        pl.xlim((max(histRange[0], xlims[0]), min(histRange[1], xlims[1])))

        path = self.getTempPath('%s.pdf' % StringUtils.getRandomString(16), isFile=True)
        self.owner.saveFigure(attrs[0], path)
        return path
