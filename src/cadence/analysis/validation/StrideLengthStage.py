# StrideLengthStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import csv
import math

import numpy as np
from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils
from pyaid.time.TimeUtils import TimeUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.enums.SnapshotDataEnum import SnapshotDataEnum


#*************************************************************************************************** StrideLengthStage
class StrideLengthStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of StrideLengthStage."""
        super(StrideLengthStage, self).__init__(key, owner, **kwargs)
        self._paths = []

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: widths
    @property
    def entries(self):
        return self.cache.get('entries')

#___________________________________________________________________________________________________ GS: noWidths
    @property
    def noData(self):
        return self.cache.get('noData', 0)
    @noData.setter
    def noData(self, value):
        self.cache.set('noData', value)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preDeviations
    def _preAnalyze(self):
        """_preDeviations doc..."""
        self.cache.set('entries', [])
        self.cache.set('noData', 0)

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackSeries(self, series, trackway, sitemap):

        for index in range(series.count - 1):
            track   = series.tracks[index]
            data    = track.snapshotData
            stride  = data.get(SnapshotDataEnum.STRIDE_LENGTH)
            if stride is None:
                self.noData += 1
                continue

            stride    = float(stride)
            nextTrack = series.tracks[index + 1]

            x     = 0.01*float(track.x)
            z     = 0.01*float(track.z)
            xNext = 0.01*float(nextTrack.x)
            zNext = 0.01*float(nextTrack.z)

            distance  = math.sqrt(math.pow(xNext - x, 2) + math.pow(zNext - z, 2))

            trackUncertainty = math.sqrt(
                math.pow(track.widthUncertainty, 2) +
                math.pow(track.lengthUncertainty, 2))

            nextUncertainty = math.sqrt(
                math.pow(nextTrack.widthUncertainty, 2) +
                math.pow(nextTrack.lengthUncertainty, 2))

            # Use the absolute value because the derivatives in error propagation are always
            # absolute values
            xDelta = abs(xNext - x)
            zDelta = abs(zNext - z)

            errorTrackX     = trackUncertainty*xDelta/distance
            errorTrackZ     = trackUncertainty*zDelta/distance
            errorNextTrackX = nextUncertainty*xDelta/distance
            errorNextTrackZ = nextUncertainty*zDelta/distance
            distanceError   = errorNextTrackX + errorTrackX + errorNextTrackZ + errorTrackZ

            delta      = distance - stride
            fractional = delta/distance

            self.entries.append(dict(
                track=track,
                delta=delta,
                    # Absolute difference between calculated and measured distance
                distance=distance,
                    # Calculated distance from AI-based data entry
                measured=stride,
                    # Distance measured in the field
                error=distanceError,
                    # Uncertainty in calculated distance
                fractional=fractional))
                    # Fractional error between calculated and measured distance

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        self._paths = []

        outputHeader = [
            'STRIDE LENGTH ANALYSIS',
            'Run on %s' % TimeUtils.toZuluFormat().replace('T', ' at '),
            'Processed %s tracks' % len(self.entries),
            '%s tracks with no stride data' % self.noData]
        self.logger.write('\n'.join(outputHeader))

        self.logger.write('='*80 + '\nFRACTIONAL ERROR (Measured vs Entered)')
        self._process()

        self.mergePdfs(self._paths)

#___________________________________________________________________________________________________ _process
    def _process(self):
        """_processDeviations doc..."""
        pl      = self.plot
        errors  = []

        for entry in self.entries:
            errors.append(entry['fractional'])

        res = self.getMeanAndDeviation(errors, 'Fractional Stride Error')

        label = 'Fractional Stride Errors'
        d     = errors
        self._paths.append(self._makePlot(label, d, histRange=(-1.0, 1.0)))
        self._paths.append(self._makePlot(label, d, isLog=True, histRange=(-1.0, 1.0)))

        # noinspection PyUnresolvedReferences
        d = np.absolute(np.array(d))
        self._paths.append(self._makePlot('Absolute ' + label, d, histRange=(0.0, 1.0)))
        self._paths.append(self._makePlot('Absolute ' + label, d, isLog=True, histRange=(0.0, 1.0)))

        count = 0

        with open(self.getPath('Stride-Length-Deviations.csv'), 'wb') as csvfile:
            fieldnames = ['UID', 'Fingerprint', 'Deviation', 'Value (m)']
            writer = csv.DictWriter(
                csvfile, fieldnames=fieldnames, dialect=csv.excel)
            writer.writeheader()

            for entry in self.entries:
                sigmaMag = 0.03 + res.std
                sigmaCount = NumericUtils.roundToOrder(abs(entry['delta']/sigmaMag), -2)
                if sigmaCount >= 2.0:
                    count += 1
                    track = entry['track']
                    valuePU = self.toValueUncertainty(abs(entry['delta']), entry['error'])

                    writer.writerow({
                        'Fingerprint':track.fingerprint,
                        'UID':track.uid,
                        'Deviation':sigmaCount,
                        'Value (m)':valuePU.label.encode('latin-1')})

                    self.logger.write('  * %s%s%s%s' % (
                        StringUtils.extendToLength(track.fingerprint, 32),
                        StringUtils.extendToLength('%s' % sigmaCount, 16),
                        StringUtils.extendToLength('(%s m)' % valuePU.label, 20),
                        track.uid))

        percentage = NumericUtils.roundToOrder(100.0*float(count)/float(len(self.entries)), -2)
        self.logger.write('%s significant %ss (%s%%)' % (count, label.lower(), percentage))
        if percentage > (100.0 - 95.45):
            self.logger.write(
                '[WARNING]: Large deviation count exceeds normal distribution expectations.')

#___________________________________________________________________________________________________ _makePlot
    def _makePlot(self, label, data, color ='b', isLog =False, histRange =None):
        """_makePlot doc..."""

        pl = self.plot
        self.owner.createFigure('makePlot')

        pl.hist(data, 31, range=histRange, log=isLog, facecolor=color, alpha=0.75)
        pl.title('%s Distribution%s' % (label, ' (log)' if isLog else ''))
        pl.xlabel('Fractional Deviation')
        pl.ylabel('Frequency')
        pl.grid(True)

        axis = pl.gca()
        xlims = axis.get_xlim()
        pl.xlim((max(histRange[0], xlims[0]), min(histRange[1], xlims[1])))

        path = self.getTempPath('%s.pdf' % StringUtils.getRandomString(16), isFile=True)
        self.owner.saveFigure('makePlot', path)
        return path

