# LengthWidthStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

import numpy as np

from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.analysis.shared.plotting.Histogram import Histogram


#*************************************************************************************************** LengthWidthStage
class LengthWidthStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of LengthWidthStage."""
        super(LengthWidthStage, self).__init__(
            key, owner,
            label='Length & Width Comparison',
            **kwargs)
        self._paths = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: trackDeviations
    @property
    def trackDeviations(self):
        return self.cache.get('trackDeviations')

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

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        """ Initialize the entries to empty and sets to zero the counters of those tracks with no
            width measurement, and those with no length measurement. """

        self.cache.set('trackDeviations', {})
        self.cache.set('entries', [])
        self.cache.set('noWidth', 0)
        self.cache.set('noLength', 0)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """ Performs analysis on each track. A dictionary is created to be added to the entries
            list.  That dictionary contains track, wDev (the fractional difference in width between
            that estimated from the map and that measured in the field), ldev (the corresponding
            fractional difference in length), and if either of those field measurements are missing,
            the corresponding counter is incremented. """

        data = dict(track=track)

        # accumulate width information for entry to add to entries
        w  = track.width
        wm = track.widthMeasured

        if not wm:
            self.noWidths += 1
        else:
            d = w - wm
            data['wDev'] = d/wm

            try:
                data['wDelta'] = abs(d)/track.widthUncertainty
            except ZeroDivisionError:
                self.logger.write([
                    '[ERROR]: Track without width uncertainty'
                    'TRACK: %s (%s)' % (track.fingerprint, track.uid) ])
                raise

        l  = track.length
        lm = track.lengthMeasured
        if not lm:
            self.noLengths += 1
        else:
            d = l - lm
            data['lDev'] = d/lm

            try:
                data['lDelta'] = abs(d)/track.lengthUncertainty
            except ZeroDivisionError:
                self.logger.write([
                    '[ERROR]: Track without length uncertainty'
                    'TRACK: %s (%s)' % (track.fingerprint, track.uid) ])
                raise

        aspect         = w/l
        wErr           = track.widthUncertainty/w
        lErr           = track.lengthUncertainty/l
        aspectUnc      = abs(aspect)*math.sqrt(wErr*wErr + lErr*lErr)
        value          = NumericUtils.toValueUncertainty(aspect, aspectUnc)
        data['aspect'] = value

        self.entries.append(data)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """ Write the logs. """

        self._paths = []

        self.logger.write('%s\nFRACTIONAL ERROR (Measured vs Entered)' % ('='*80))
        self._process('Error', 'wDev', 'lDev', self.trackDeviations)

        self.logger.write('%s\nFRACTIONAL UNCERTAINTY ERROR' % ('='*80))
        self._process('Uncertainty Error', 'wDelta', 'lDelta', None, absoluteOnly=True)

        self._processAspectRatios()

        self.mergePdfs(self._paths)

#___________________________________________________________________________________________________ _getFooterArgs
    def _getFooterArgs(self):
        return [
            'Processed %s tracks' % len(self.entries),
            '%s tracks with no measured width' % self.cache.get('noWidths'),
            '%s tracks with no measured length' % self.cache.get('noLengths') ]

#___________________________________________________________________________________________________ _process
    def _process(self, label, widthKey, lengthKey, trackDeviations, absoluteOnly =False):
        """_process doc..."""
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

        wRes = NumericUtils.getMeanAndDeviation(ws)
        self.logger.write('Width %ss' % wRes.label)
        lRes = NumericUtils.getMeanAndDeviation(ls)
        self.logger.write('Length %ss' % lRes.label)

        for data in plotList:
            if not absoluteOnly:
                d = data[1]
                self._paths.append(
                    self._makePlot(label, d, data, histRange=(-1.0, 1.0)))
                self._paths.append(
                    self._makePlot(label, d, data, isLog=True, histRange=(-1.0, 1.0)))

            # noinspection PyUnresolvedReferences
            d = np.absolute(np.array(data[1]))
            self._paths.append(
                self._makePlot('Absolute ' + label, d, data, histRange=(0.0, 1.0)))
            self._paths.append(
                self._makePlot('Absolute ' + label, d, data, isLog=True, histRange=(0.0, 1.0)))

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

        csv = CsvWriter()
        csv.path = self.getPath('%s-Deviations.csv' % label.replace(' ', '-'), isFile=True)
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('wSigma', 'Width Deviation'),
            ('lSigma', 'Length Deviation'))

        count = 0
        for entry in self.entries:
            widthDevSigma  = NumericUtils.roundToOrder(
                abs(entry.get(widthKey, 0.0)/wRes.uncertainty), -2)
            lengthDevSigma = NumericUtils.roundToOrder(
                abs(entry.get(lengthKey, 0.0)/lRes.uncertainty), -1)
            if widthDevSigma > 2.0 or lengthDevSigma > 2.0:
                count += 1
                track = entry['track']
                data = dict(
                    wSigma=widthDevSigma,
                    lSigma=lengthDevSigma)

                if trackDeviations is not None:
                    trackDeviations[track.uid] = data

                csv.createRow(uid=track.uid, fingerprint=track.fingerprint, **data)

        if not csv.save():
            self.logger.write('[ERROR]: Failed to save CSV file to %s' % csv.path)

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

#___________________________________________________________________________________________________ _processAspectRatios
    def _processAspectRatios(self):
        """_processAspectRatios doc..."""
        aspects    = []
        pesAspects = []
        manAspects = []

        for entry in self.entries:
            value = entry['aspect'].value
            aspects.append(value)
            if entry['track'].pes:
                pesAspects.append(value)
            else:
                manAspects.append(value)

        self.logger.write('%s\nASPECT RATIO' % ('='*80))
        self.logger.write('Total: %s' % NumericUtils.getMeanAndDeviation(aspects).label)
        self.logger.write('Pes: %s' % NumericUtils.getMeanAndDeviation(pesAspects).label)
        self.logger.write('Manus: %s' % NumericUtils.getMeanAndDeviation(manAspects).label)

        h = Histogram(data=aspects, color='green')
        h.title = 'Aspect Ratios'
        h.yLabel = 'Count'
        h.xLabel = 'Aspect Ratio (width/length)'
        self._paths.append(h.save(self.getTempFilePath(extension='pdf')))

        h = Histogram(data=pesAspects, color='green')
        h.title = 'Aspect Ratios (Pes)'
        h.yLabel = 'Count'
        h.xLabel = 'Aspect Ratio (width/length)'
        self._paths.append(h.save(self.getTempFilePath(extension='pdf')))

        h = Histogram(data=manAspects, color='green')
        h.title = 'Aspect Ratios (Manus)'
        h.yLabel = 'Count'
        h.xLabel = 'Aspect Ratio (width/length)'
        self._paths.append(h.save(self.getTempFilePath(extension='pdf')))
