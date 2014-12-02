# StrideLengthStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import math

import numpy as np
from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.enums.SnapshotDataEnum import SnapshotDataEnum


#*************************************************************************************************** StrideLengthStage
class StrideLengthStage(AnalysisStage):
    """ The primary analysis stage for validating the stride lengths between the digitally entered
        data and the catalog data measured in the field. """

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
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

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preDeviations
    def _preAnalyze(self):
        """_preDeviations doc..."""
        self.noData = 0
        self.entries = []

        csv = CsvWriter()
        csv.path = self.getPath('Stride-Length-Deviations.csv', isFile=True)
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('entered', 'Entered (m)'),
            ('measured', 'Measured (m)'),
            ('dev', 'Deviation (sigma)'),
            ('delta', 'Fractional Error (%)'))
        self._csv = csv

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
            if track.next != nextTrack.uid:
                self.logger.write(
                    '[ERROR]: Invalid track ordering (%s -> %s)' % (track.uid, nextTrack.uid))

            # Convert entered positions from centimeters to meters
            x     = 0.01*float(track.x)
            z     = 0.01*float(track.z)
            xNext = 0.01*float(nextTrack.x)
            zNext = 0.01*float(nextTrack.z)

            distance = math.sqrt(math.pow(xNext - x, 2) + math.pow(zNext - z, 2))
            if not distance:
                self.logger.write([
                    '[WARNING]: Invalid track separation of 0.0. Ignoring track',
                    'TRACK: %s [%s]' % (track.fingerprint, track.uid),
                    'NEXT: %s [%s]' % (nextTrack.fingerprint, track.uid)])
                continue

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

            entered = NumericUtils.toValueUncertainty(distance, distanceError)
            measured = NumericUtils.toValueUncertainty(stride, 0.06)

            delta      = entered.value - measured.value
            deviation  = delta/(measured.uncertainty + entered.uncertainty)
            fractional = delta/measured.value

            entry = dict(
                track=track,
                    # Absolute difference between calculated and measured distance
                delta=delta,
                    # Calculated distance from AI-based data entry
                entered=entered,
                    # Measured distance from the catalog
                measured=measured,
                    # Fractional error between calculated and measured distance
                fractional=fractional,
                    # Sigma deviations between
                deviation=deviation)

            self.entries.append(entry)
            track.cache.set('strideData', entry)

#___________________________________________________________________________________________________ _postAnalyze
    def _postAnalyze(self):
        """_postAnalyze doc..."""
        self._paths = []

        self.logger.write('='*80 + '\nFRACTIONAL ERROR (Measured vs Entered)')
        self._process()

        self.mergePdfs(self._paths)

#___________________________________________________________________________________________________ _getFooterArgs
    def _getFooterArgs(self):
        return [
            'Processed %s tracks' % len(self.entries),
            '%s tracks with no stride data' % self.noData]

#___________________________________________________________________________________________________ _process
    def _process(self):
        """_processDeviations doc..."""
        errors  = []

        for entry in self.entries:
            errors.append(entry['fractional'])

        res = NumericUtils.getMeanAndDeviation(errors)
        self.logger.write('Fractional Stride Error %s' % res.label)

        label = 'Fractional Stride Errors'
        d     = errors
        self._paths.append(self._makePlot(label, d, histRange=(-1.0, 1.0)))
        self._paths.append(self._makePlot(label, d, isLog=True, histRange=(-1.0, 1.0)))

        # noinspection PyUnresolvedReferences
        d = np.absolute(np.array(d))
        self._paths.append(self._makePlot('Absolute ' + label, d, histRange=(0.0, 1.0)))
        self._paths.append(self._makePlot('Absolute ' + label, d, isLog=True, histRange=(0.0, 1.0)))

        highDeviationCount = 0

        for entry in self.entries:
            sigmaMag = 0.03 + res.uncertainty
            sigmaCount = NumericUtils.roundToOrder(abs(entry['delta']/sigmaMag), -2)
            entry['meanDeviation'] = sigmaCount
            entry['highMeanDeviation'] = False

            if sigmaCount >= 2.0:
                entry['highMeanDeviation'] = True
                highDeviationCount += 1
                track = entry['track']
                delta = NumericUtils.roundToSigFigs(100.0*abs(entry['delta']), 3)

                self._csv.addRow({
                    'fingerprint':track.fingerprint,
                    'uid':track.uid,
                    'measured':entry['measured'].label,
                    'entered':entry['entered'].label,
                    'dev':sigmaCount,
                    'delta':delta})

        if not self._csv.save():
            self.logger.write('[ERROR]: Failed to save CSV file %s' % self._csv.path)

        percentage = NumericUtils.roundToOrder(100.0*float(highDeviationCount)/float(len(self.entries)), -2)
        self.logger.write('%s significant %ss (%s%%)' % (highDeviationCount, label.lower(), percentage))
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

