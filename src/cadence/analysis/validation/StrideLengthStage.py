# StrideLengthStage.py
# (C)2014
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import math

import numpy as np
from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.enums.AnalysisFlagsEnum import AnalysisFlagsEnum
from cadence.enums.ImportFlagsEnum import ImportFlagsEnum
from cadence.enums.SnapshotDataEnum import SnapshotDataEnum
from cadence.svg.CadenceDrawing import CadenceDrawing


#*******************************************************************************
class StrideLengthStage(AnalysisStage):
    """ The primary analysis stage for validating the stride lengths between
        the digitally entered
        data and the catalog data measured in the field.
    """

    MEASURED_UNCERTAINTY = 0.01
    HIGH_MEASURED_UNCERTAINTY = 0.03

    MAPS_FOLDER_NAME = 'Stride-Lengths'

    #___________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of StrideLengthStage."""
        super(StrideLengthStage, self).__init__(
            key, owner,
            label='Stride Length',
            **kwargs)
        self._paths  = []
        self._csv    = None
        self.noData  = 0
        self.entries = []

    #===========================================================================
    #                                                         P R O T E C T E D

    #___________________________________________________________________________
    def _preAnalyze(self):
        """_preDeviations doc..."""
        self.noData = 0
        self.entries = []
        self._paths = []

        csv = CsvWriter()
        csv.path = self.getPath('Stride-Length-Deviations.csv', isFile=True)
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('entered', 'Entered'),
            ('measured', 'Measured'),
            ('dev', 'Deviation'),
            ('delta', 'Fractional Error'))
        self._csv = csv

    #___________________________________________________________________________
    def _analyzeSitemap(self, sitemap):

        drawing = CadenceDrawing(
            self.getPath(
                self.MAPS_FOLDER_NAME,
                '%s-%s-STRIDE.svg' % (sitemap.name, sitemap.level),
                isFile=True),
            sitemap)

        drawing.grid()
        drawing.federalCoordinates()
        sitemap.cache.set('drawing', drawing)

        super(StrideLengthStage, self)._analyzeSitemap(sitemap)

        try:
            sitemap.cache.extract('drawing').save()
        except Exception:
            self.logger.write('[WARNING]: No sitemap saved for %s-%s' % (
                sitemap.name, sitemap.level))

    #___________________________________________________________________________
    def _analyzeTrackSeries(self, series, trackway, sitemap):

        for index in range(series.count):
            track = series.tracks[index]
            stride = self.getStride(track)
            aTrack = track.getAnalysisPair(self.analysisSession)
            aTrack.strideLength = 0.0
            aTrack.strideLengthUnc = 0.0

            if stride is None:
                # Count tracks with no measured stride
                self.noData += 1

            if series.count < 2:
                # Series of length 1 should not have a measured stride length
                if stride:
                    # Check for a stride to make sure data is consistent
                    # instead of assuming that is not true.
                    self.logger.write([
                        '[ERROR]: Stride information on a single track series',
                        'TRACK: %s (%s)' % (track.fingerprint, track.uid) ])
                continue

            isLastTrack = (index == (series.count - 1))
            pairTrack = series.tracks[index + (-1 if isLastTrack else 1)]

            if isLastTrack and pairTrack.next != track.uid:
                self.logger.write([
                    '[ERROR]: Invalid track ordering (last track)',
                    'PREV: %s (%s)' % (pairTrack.fingerprint, pairTrack.uid),
                    'TRACK: %s (%s)' % (track.fingerprint, track.uid) ])
            elif not isLastTrack and track.next != pairTrack.uid:
                self.logger.write([
                    '[ERROR]: Invalid track ordering',
                    'TRACK: %s (%s)' % (track.fingerprint, track.uid),
                    'NEXT: %s (%s)' % (pairTrack.fingerprint, pairTrack.uid) ])

            posTrack = track.positionValue
            posPair  = pairTrack.positionValue

            try:
                entered = posTrack.distanceTo(posPair)
            except Exception:
                self.logger.write([
                    '[WARNING]: Invalid track separation of 0.0.',
                    'TRACK: %s [%s]' % (track.fingerprint, track.uid),
                    'NEXT: %s [%s]' % (pairTrack.fingerprint, track.uid)])
                continue

            entry = dict(
                track=track,
                # Calculated distance from AI-based data entry
                entered=entered)

            if stride and stride > 0.0:
                highDeviation = track.hasImportFlag(
                    ImportFlagsEnum.HIGH_STRIDE_UNCERTAINTY)
                # If stride measurement exists do comparison
                meas = NumericUtils.toValueUncertainty(
                    value=float(stride),
                    uncertainty=self.HIGH_MEASURED_UNCERTAINTY
                        if highDeviation
                        else self.MEASURED_UNCERTAINTY)
                delta = entered.value - meas.value

                deviation = abs(delta/math.sqrt(
                    meas.uncertainty**2 +
                    entered.uncertainty**2))
                if highDeviation and deviation > 3:
                    styles = ('orange', 10)
                else:
                    # Measured distance from the catalog
                    entry['measured'] = meas
                    # Absolute difference between calculated and measured distance
                    entry['delta'] = delta
                    # Sigma trackDeviations between
                    entry['deviation'] = deviation
                    # Fractional error between calculated and measured distance
                    entry['fractional'] = delta/meas.value

                    styles = ('red', 10) \
                        if entry['deviation'] > 2.0 \
                        else ('green', 5)
            else:
                styles = ('purple', 5)

            drawing = sitemap.cache.get('drawing')

            if not isLastTrack:
                aTrack.strideLength = entered.raw
                aTrack.strideLengthUnc = entered.rawUncertainty

                drawing.line(
                    posTrack.toMayaTuple(), posPair.toMayaTuple(),
                    stroke=styles[0], stroke_width=1, stroke_opacity='0.1')

            drawing.circle(
                posTrack.toMayaTuple(), styles[1],
                stroke='none', fill=styles[0], fill_opacity=0.5)

            self.entries.append(entry)
            track.cache.set('strideData', entry)

    #___________________________________________________________________________
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        self._paths = []

        self.logger.write(
            '%s\nFRACTIONAL ERROR (Measured vs Entered)' % ('='*80))
        self._process()

        self.mergePdfs(self._paths)

    #___________________________________________________________________________
    def _getFooterArgs(self):
        return [
            'Processed %s tracks' % len(self.entries),
            '%s tracks with no stride data' % self.noData]

    #___________________________________________________________________________
    def _process(self):
        """_processDeviations doc..."""
        errors  = []

        for entry in self.entries:
            if 'fractional' in entry:
                errors.append(entry['fractional'])

        res = NumericUtils.getMeanAndDeviation(errors)
        self.logger.write('Fractional Stride Error %s' % res.label)

        label = 'Fractional Stride Errors'
        self._paths.append(self._makePlot(
            label=label,
            data=errors,
            histRange=(-1.0, 1.0) ))
        self._paths.append(self._makePlot(
            label=label,
            data=errors,
            isLog=True,
            histRange=(-1.0, 1.0) ))

        # noinspection PyUnresolvedReferences
        d = np.absolute(np.array(errors))
        self._paths.append(self._makePlot(
            label='Absolute %s' % label,
            data=d, histRange=(0.0, 1.0) ))
        self._paths.append(self._makePlot(
            label='Absolute %s' % label,
            data=d,
            isLog=True,
            histRange=(0.0, 1.0) ))

        highDeviationCount = 0

        for entry in self.entries:
            if 'measured' not in entry:
                # Skip tracks that have no measured stride value for comparison
                continue

            if entry['deviation'] > 2.0:
                highDeviationCount += 1

            track = entry['track']
            delta = NumericUtils.roundToSigFigs(100.0*abs(entry['delta']), 3)

            self._csv.addRow({
                'fingerprint':track.fingerprint,
                'uid':track.uid,
                'measured':entry['measured'].label,
                'entered':entry['entered'].label,
                'dev':entry['deviation'],
                'delta':delta})

        if not self._csv.save():
            self.logger.write(
                '[ERROR]: Failed to save CSV file %s' % self._csv.path)

        percentage = NumericUtils.roundToOrder(
            100.0*float(highDeviationCount)/float(len(self.entries)), -2)
        self.logger.write(
            '%s significant %s (%s%%)' % (
                highDeviationCount,
                label.lower(),
                percentage))

        if percentage > (100.0 - 95.45):
            self.logger.write(
                '[WARNING]: Large deviation count exceeds normal ' +
                'distribution expectations.')

    #___________________________________________________________________________
    def _makePlot(self, label, data, color ='b', isLog =False, histRange =None):
        """_makePlot doc..."""

        pl = self.plot
        self.owner.createFigure('makePlot')

        pl.hist(
            data, 31,
            range=histRange,
            log=isLog,
            facecolor=color,
            alpha=0.75)
        pl.title('%s Distribution%s' % (label, ' (log)' if isLog else ''))
        pl.xlabel('Fractional Deviation')
        pl.ylabel('Frequency')
        pl.grid(True)

        axis = pl.gca()
        xlims = axis.get_xlim()
        pl.xlim((max(histRange[0], xlims[0]), min(histRange[1], xlims[1])))

        path = self.getTempPath(
            '%s.pdf' % StringUtils.getRandomString(16), isFile=True)
        self.owner.saveFigure('makePlot', path)
        return path

    #___________________________________________________________________________
    @classmethod
    def getStride(cls, track):
        """ Returns the field stride measurement for the specified track if
            the track recorded a stride length """
        if track.analysisFlags & AnalysisFlagsEnum.IGNORE_STRIDE:
            return None
        out = track.snapshotData.get(SnapshotDataEnum.STRIDE_LENGTH)
        return out if out and out > 0.0 else None
