# LengthWidthStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

import numpy as np

from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.analysis.shared.plotting.Histogram import Histogram

from cadence.svg.CadenceDrawing import CadenceDrawing

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

        self._currentDrawing = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: deviations
    @property
    def deviations(self):
        return self.cache.get('deviations')

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

        self.cache.set('entries', [])
        self.cache.set('noWidth', 0)
        self.cache.set('noLength', 0)

#___________________________________________________________________________________________________  _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        """ Start a drawing for the SVG and PDF files for this site. """

        fileName = sitemap.name + "_" + sitemap.level + '_lengthWidth.svg'
        path = self.getPath(fileName, isFile=True)
        self._currentDrawing = CadenceDrawing(path, sitemap)

        # create a pointer for map annotation
        self._currentDrawing.createGroup('pointer')
        self._currentDrawing.line((0, 0), (0, -20), scene=False, groupId='pointer')

        # and place a grid and the federal coordinates in the drawing file
        self._currentDrawing.grid()
        self._currentDrawing.federalCoordinates()

        # do what needs to be done
        super(LengthWidthStage, self)._analyzeSitemap(sitemap)

        # then when back, save the drawing
        if self._currentDrawing:
            self._currentDrawing.save()

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        """ Performs analysis on each track. A dictionary is created to be added to the entries
            list.  That dictionary contains track, wDev (the fractional difference in width between
            that estimated from the map and that measured in the field), ldev (the corresponding
            fractional difference in length, and if either of those field measurements are missing,
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
            data['wDelta'] = abs(d)/track.widthUncertainty

        l  = track.length
        lm = track.lengthMeasured
        if not lm:
            self.noLengths += 1
        else:
            d = l - lm
            data['lDev'] = d/lm
            data['lDelta'] = abs(d)/track.lengthUncertainty

        aspect = w/l
        wErr   = track.widthUncertainty/w
        lErr   = track.lengthUncertainty/l
        aspectUnc = abs(aspect)*math.sqrt(wErr*wErr + lErr*lErr)
        value = NumericUtils.toValueUncertainty(aspect, aspectUnc)
        data['aspect'] = value

        self.entries.append(data)

        # visualize track width and length compared to measured values for these dimensions
        self.drawTrack(track, self._currentDrawing, 'pointer')

#___________________________________________________________________________________________________ drawTrack
    def drawTrack(self, track, drawing, group, thickness =1.0, tolerance =0.20):
        """ The dimensions of a given track is drawn, and added to a given drawing, using the given
            CadenceDrawing group (a line oriented with the SVG positive Y direction. """

        # indicate the length (per track.length)
        drawing.use(group,
                    (track.x, track.z),
                    scale=2.0,
                    scaleY=track.lengthRatio*track.length,
                    rotation=track.rotation,
                    scene=True,
                    fill='none',
                    stroke='blue',
                    stroke_width=2.0,
                    stroke_opacity= 1.0,
                    fill_opacity=1.0)
        drawing.use(group,
                    (track.x, track.z),
                    scale=2.0,
                    scaleY=(1.0 - track.lengthRatio)*track.length,
                    rotation=track.rotation + 180.0,
                    scene=True,
                    fill='none',
                    stroke='blue',
                    stroke_width=2.0,
                    stroke_opacity=1.0,
                    fill_opacity=1.0)

        # and the same for the width (per track.width)
        drawing.use(group,
                    (track.x, track.z),
                    scale=2.0,
                    scaleY=track.width/2.0,
                    rotation=track.rotation + 90.0,
                    scene=True,
                    fill='none',
                    stroke='blue',
                    stroke_width=2.0,
                    stroke_opacity=1.0,
                    fill_opacity=1.0)
        drawing.use(group,
                    (track.x, track.z),
                    scale=2.0,
                    scaleY=track.width/2.0,
                    rotation=track.rotation - 90.0,
                    scene=True,
                    fill='none',
                    stroke='blue',
                    stroke_width=2.0,
                    stroke_opacity=1.0,
                    fill_opacity=1.0)

        # now render the measured dimensions, if provided, starting with lengthMeasured
        if track.lengthMeasured != 0:
            if abs(track.length - track.lengthMeasured)/track.lengthMeasured > tolerance:
                strokeWidth = 8
                opacity     = 0.5
                color       = 'red'
            else:
                strokeWidth = 8
                opacity     = 0.25
                color       = 'green'
            drawing.use(group,
                        (track.x, track.z),
                        scale=thickness,
                        scaleY=track.lengthRatio*track.lengthMeasured,
                        rotation=track.rotation,
                        scene=True,
                        fill='none',
                        stroke=color,
                        stroke_width=strokeWidth,
                        stroke_opacity=opacity,
                        fill_opacity=opacity)
            drawing.use('pointer',
                        (track.x, track.z),
                        scale=thickness,
                        scaleY=(1.0 - track.lengthRatio)*track.lengthMeasured,
                        rotation=track.rotation + 180.0,
                        scene=True,
                        fill='none',
                        stroke=color,
                        stroke_width=strokeWidth,
                        stroke_opacity=opacity,
                        fill_opacity=opacity)

        # and likewise for widthMeasured
        if track.widthMeasured != 0:
            if abs(track.width - track.widthMeasured)/track.widthMeasured > tolerance:
                strokeWidth = 8
                opacity     = 0.5
                color       = 'red'
            else:
                strokeWidth = 8
                opacity     = 0.25
                color       = 'green'
            drawing.use('pointer',
                        (track.x, track.z),
                        scale=2.0*thickness,
                        scaleY=track.widthMeasured/2.0,
                        rotation=track.rotation + 90.0,
                        scene=True,
                        fill='none',
                        stroke=color,
                        stroke_width=strokeWidth,
                        stroke_opacity=opacity,
                        fill_opacity=opacity)
            drawing.use('pointer',
                        (track.x, track.z),
                        scale=2.0*thickness,
                        scaleY=track.widthMeasured/2.0,
                        rotation=track.rotation - 90.0,
                        scene=True,
                        fill='none',
                        stroke=color,
                        stroke_width=strokeWidth,
                        stroke_opacity=opacity,
                        fill_opacity=opacity)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """ Write the logs. """

        self._paths = []

        self.logger.write('='*80 + '\nFRACTIONAL ERROR (Measured vs Entered)')
        self._process('Error', 'wDev', 'lDev')

        self.logger.write('='*80 + '\nFRACTIONAL UNCERTAINTY ERROR')
        self._process('Uncertainty Error', 'wDelta', 'wDelta', absoluteOnly=True)

        self._processAspectRatios()

        self.mergePdfs(self._paths)

#___________________________________________________________________________________________________ _getFooterArgs
    def _getFooterArgs(self):
        return [
            'Processed %s tracks' % len(self.entries),
            '%s tracks with no measured width' % self.cache.get('noWidths'),
            '%s tracks with no measured length' % self.cache.get('noLengths') ]

#___________________________________________________________________________________________________ _process
    def _process(self, label, widthKey, lengthKey, absoluteOnly =False):
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
                self.deviations[track.uid] = data

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

        self.logger.write('='*80 + '\nASPECT RATIO')
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
