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

from cadence.enums.ImportFlagsEnum import ImportFlagsEnum

#*******************************************************************************
class LengthWidthStage(AnalysisStage):
    """ Analysis stage for comparison of length and width between the field
        measurements for length and width track parameters and the map measured
        values. """

    #___________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of LengthWidthStage."""
        super(LengthWidthStage, self).__init__(
            key, owner,
            label='Length & Width Comparison',
            **kwargs)
        self._paths = []

    #===========================================================================
    #                                                             G E T / S E T

    #___________________________________________________________________________
    @property
    def trackDeviations(self):
        return self.cache.get('trackDeviations')

    #___________________________________________________________________________
    @property
    def entries(self):
        return self.cache.get('entries')

    #___________________________________________________________________________
    @property
    def noWidths(self):
        return self.cache.get('noWidths', 0)
    @noWidths.setter
    def noWidths(self, value):
        self.cache.set('noWidths', value)

    #___________________________________________________________________________
    @property
    def noLengths(self):
        return self.cache.get('noLengths', 0)
    @noLengths.setter
    def noLengths(self, value):
        self.cache.set('noLengths', value)

    #===========================================================================
    #                                                         P R O T E C T E D

    #___________________________________________________________________________
    def _preAnalyze(self):
        """ Initialize the entries to empty and sets to zero the counters of
            those tracks with no width measurement, and those with no length
            measurement.
        """
        self.cache.set('trackDeviations', {})
        self.cache.set('entries', [])
        self.cache.set('noWidth', 0)
        self.cache.set('noLength', 0)

    #___________________________________________________________________________
    def _calculateDeviation(
            self, track, value, uncertainty, highMeasuredUncertainty, measured,
            prefix, label
    ):
        if not measured:
            return None

        out = dict()

        measuredUncertainty = measured*(
            0.12 if highMeasuredUncertainty else 0.06)

        v = NumericUtils.toValueUncertainty(value, uncertainty)
        mv = NumericUtils.toValueUncertainty(measured, measuredUncertainty)
        unc = math.sqrt(v.uncertainty**2 + mv.uncertainty**2)

        deviation = v.value - mv.value
        out['%sDev' % prefix] = deviation/measured

        try:
            out['%sDelta' % prefix] = abs(deviation)/unc
        except ZeroDivisionError:
            self.logger.write([
                '[ERROR]: Track without %s uncertainty' % label,
                'TRACK: %s (%s)' % (track.fingerprint, track.uid) ])
            raise

        return out

    #___________________________________________________________________________
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """ Performs analysis on each track. A dictionary is created to be
            added to the entries list.  That dictionary contains track,
            wDev (the fractional difference in width between that estimated
            from the map and that measured in the field), ldev (the
            corresponding fractional difference in length), and if either of
            those field measurements are missing, the corresponding counter is
            incremented.
        """
        data = dict(track=track)

        result = self._calculateDeviation(
            track=track,
            value=track.width,
            uncertainty=track.widthUncertainty,
            measured=track.widthMeasured,
            highMeasuredUncertainty=track.hasImportFlag(
                ImportFlagsEnum.HIGH_WIDTH_UNCERTAINTY),
            prefix='w',
            label='Width')
        if result:
            data.update(result)

        result = self._calculateDeviation(
            track=track,
            value=track.length,
            uncertainty=track.lengthUncertainty,
            measured=track.lengthMeasured,
            highMeasuredUncertainty=track.hasImportFlag(
                ImportFlagsEnum.HIGH_LENGTH_UNCERTAINTY),
            prefix='l',
            label='Length')
        if result:
            data.update(result)

        aspect         = track.width/track.length
        wErr           = track.widthUncertainty/track.width
        lErr           = track.lengthUncertainty/track.length
        aspectUnc      = abs(aspect)*math.sqrt(wErr*wErr + lErr*lErr)
        value          = NumericUtils.toValueUncertainty(aspect, aspectUnc)
        data['aspect'] = value

        self.entries.append(data)

    #___________________________________________________________________________
    def _postAnalyze(self):
        """ Write the logs. """

        self._paths = []

        self.logger.write(
            '%s\nFRACTIONAL ERROR (Measured vs Entered)' % ('='*80))
        self._process('Error', 'wDev', 'lDev', self.trackDeviations)

        self.logger.write('%s\nFRACTIONAL UNCERTAINTY ERROR' % ('='*80))
        self._process(
            'Uncertainty Error', 'wDelta', 'lDelta', None, absoluteOnly=True)

        csv = CsvWriter(
            path=self.getPath('Length-Width-Deviations.csv'),
            autoIndexFieldName='Index',
            fields=[
                ('uid', 'UID'),
                ('fingerprint', 'Fingerprint'),
                ('wDelta', 'Width Deviation'),
                ('lDelta', 'Length Deviation') ])

        for entry in self.entries:
            track = entry['track']
            csv.createRow(
                uid=track.uid,
                fingerprint=track.fingerprint,
                wDelta=entry.get('wDelta', -1.0),
                lDelta=entry.get('lDelta', -1.0) )
        csv.save()

        self._processAspectRatios()

        self.mergePdfs(self._paths)

    #___________________________________________________________________________
    def _getFooterArgs(self):
        return [
            'Processed %s tracks' % len(self.entries),
            '%s tracks with no measured width' % self.cache.get('noWidths'),
            '%s tracks with no measured length' % self.cache.get('noLengths') ]

    #___________________________________________________________________________
    def _process(
            self, label, widthKey, lengthKey, trackDeviations,
            absoluteOnly =False
    ):
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
                    self._makePlot(
                        label, d, data,
                        histRange=(-1.0, 1.0)))
                self._paths.append(
                    self._makePlot(
                        label, d, data,
                        isLog=True,
                        histRange=(-1.0, 1.0)))

            # noinspection PyUnresolvedReferences
            d = np.absolute(np.array(data[1]))
            self._paths.append(
                self._makePlot(
                    'Absolute ' + label, d, data,
                    histRange=(0.0, 1.0)))
            self._paths.append(
                self._makePlot(
                    'Absolute ' + label, d, data,
                    isLog=True,
                    histRange=(0.0, 1.0)))

        self.owner.createFigure('twoD')
        pl.hist2d(w2D, l2D, bins=20, range=([-1, 1], [-1, 1]))
        pl.title('2D %s Distribution' % label)
        pl.xlabel('Width %s' % label)
        pl.ylabel('Length %s' % label)
        pl.xlim(-1.0, 1.0)
        pl.ylim(-1.0, 1.0)
        path = self.getTempPath(
            '%s.pdf' % StringUtils.getRandomString(16),
            isFile=True)
        self.owner.saveFigure('twoD', path)
        self._paths.append(path)

        csv = CsvWriter()
        csv.path = self.getPath(
            '%s-Deviations.csv' % label.replace(' ', '-'),
            isFile=True)
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('wSigma', 'Width Deviation'),
            ('lSigma', 'Length Deviation') )

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

                csv.createRow(
                    uid=track.uid,
                    fingerprint=track.fingerprint,
                    **data)

        if not csv.save():
            self.logger.write(
                '[ERROR]: Failed to save CSV file to %s' % csv.path)

        percentage = NumericUtils.roundToOrder(
            100.0*float(count)/float(len(self.entries)), -2)
        self.logger.write('%s significant %ss (%s%%)' % (
            count, label.lower(), percentage))
        if percentage > (100.0 - 95.45):
            self.logger.write(
                '[WARNING]: Large deviation count exceeds' +
                'normal distribution expectations.')

    #___________________________________________________________________________
    def _makePlot(self, label, data, attrs, isLog =False, histRange =None):
        """_makePlot doc..."""

        pl = self.plot
        self.owner.createFigure(attrs[0])

        pl.hist(
            data, 31,
            range=histRange,
            log=isLog,
            facecolor=attrs[3],
            alpha=0.75)
        pl.title(
            '%s %s Distribution%s' % (
                attrs[2], label, ' (log)' if isLog else ''))
        pl.xlabel('Deviation')
        pl.ylabel('Frequency')
        pl.grid(True)

        axis = pl.gca()
        xlims = axis.get_xlim()
        pl.xlim((max(histRange[0], xlims[0]), min(histRange[1], xlims[1])))

        path = self.getTempPath(
            '%s.pdf' % StringUtils.getRandomString(16),
            isFile=True)
        self.owner.saveFigure(attrs[0], path)
        return path

    #___________________________________________________________________________
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
        self.logger.write('Total: %s' %
            NumericUtils.getMeanAndDeviation(aspects).label)
        self.logger.write('Pes: %s' %
            NumericUtils.getMeanAndDeviation(pesAspects).label)
        self.logger.write('Manus: %s' %
            NumericUtils.getMeanAndDeviation(manAspects).label)

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
