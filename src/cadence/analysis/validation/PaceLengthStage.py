# PaceLengthStage.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import numpy as np
from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.enums.SnapshotDataEnum import SnapshotDataEnum



#*************************************************************************************************** PaceLengthStage
class PaceLengthStage(AnalysisStage):
    """ The primary analysis stage for validating the stride lengths between the digitally entered
        data and the catalog data measured in the field. """

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of PaceLengthStage."""
        super(PaceLengthStage, self).__init__(
            key, owner,
            label='Pace Length',
            **kwargs)
        self._paths  = []
        self._csv    = None
        self.noData  = 0
        self.count   = 0
        self.entries = []

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preDeviations
    def _preAnalyze(self):
        """_preDeviations doc..."""
        self.noData = 0
        self.entries = []

        csv = CsvWriter()
        csv.path = self.getPath('Pace-Length-Deviations.csv', isFile=True)
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('entered', 'Entered (m)'),
            ('measured', 'Measured (m)'),
            ('dev', 'Deviation (sigma)'),
            ('delta', 'Fractional Error (%)'),
            ('pairedFingerprint', 'Track Pair Fingerprint'),
            ('pairedUid', 'Track Pair UID') )
        self._csv = csv

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackway(self, trackway, sitemap):
        data = self.owner.getTrackwaySeries(trackway)
        l = data['leftManus']
        r = data['rightManus']

        if l.count and l.isReady and r.count and r.isReady:
            self._analyzeSeriesPair(l, r)
            self._analyzeSeriesPair(r, l)

        l = data['leftPes']
        r = data['rightPes']

        if l.count and l.isReady and r.count and r.isReady:
            self._analyzeSeriesPair(l, r)
            self._analyzeSeriesPair(r, l)

#___________________________________________________________________________________________________ _analyzeSeriesPair
    def _analyzeSeriesPair(self, series, pair):
        """_analyzeSeriesPair doc..."""

        for index in range(series.count):
            track   = series.tracks[index]
            data    = track.snapshotData
            pace    = data.get(SnapshotDataEnum.PACE)
            if pace is None:
                self.noData += 1
                continue

            pace = float(pace)
            position = track.positionValue

            if track != series.tracks[-1]:
                nextTrack = series.tracks[index + 1]
                if track.next != nextTrack.uid:
                    self.logger.write('[ERROR]: Invalid track ordering (%s -> %s)' % (
                        track.uid, nextTrack.uid))
                nextPosition = nextTrack.positionValue
            elif index == 0:
                continue
            else:
                # Extrapolate using the position of the previous print to get a nextPosition
                # value for use in finding the pace track pair
                lastTrack = series.tracks[index - 1]
                line = LineSegment2D(start=lastTrack.positionValue, end=position)
                try:
                    line.postExtendLine(line.length.raw)
                except Exception:
                    self.logger.write([
                        '[ERROR]: Invalid separation between tracks',
                        'TRACK: %s' % track,
                        'LAST TRACK: %s' % lastTrack])
                    continue

                nextPosition = line.end.clone()

            pairTrack = None
            distance = 1.0e8

            if track.fingerprint.startswith('BEB-515-2009-1-S-21-L-M'):
                print(track.fingerprint)

            for pt in pair.tracks:
                try:
                    pos = pt.positionValue
                    d = nextPosition.distanceTo(pos).raw + position.distanceTo(pos).raw
                except Exception:
                    continue

                if d < distance:
                    pairTrack = pt
                    distance = d

            if not pairTrack:
                self.logger.write([
                    '[ERROR]: No pair track found for pace calculation',
                    'TRACK: %s' % track,
                    'NEXT TRACK: %s' % nextTrack])
                continue

            try:
                entered = position.distanceTo(pairTrack.positionValue)
            except Exception:
                self.logger.write([
                    '[WARNING]: Invalid track separation of 0.0. Ignoring track',
                    'TRACK: %s [%s]' % (track.fingerprint, track.uid),
                    'NEXT: %s [%s]' % (nextTrack.fingerprint, track.uid)])
                continue

            measured   = NumericUtils.toValueUncertainty(pace, 0.06)
            delta      = entered.value - measured.value
            deviation  = delta/(measured.uncertainty + entered.uncertainty)
            fractional = delta/measured.value
            self.count += 1

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
                    # Sigma trackDeviations between
                deviation=deviation,
                pairTrack=pairTrack)

            self.entries.append(entry)
            track.cache.set('paceData', entry)

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
            '%s tracks with no pace data' % self.noData]

#___________________________________________________________________________________________________ _process
    def _process(self):
        """_processDeviations doc..."""
        errors  = []

        for entry in self.entries:
            errors.append(entry['fractional'])

        res = NumericUtils.getMeanAndDeviation(errors)
        self.logger.write('Fractional Pace Error %s' % res.label)

        label = 'Fractional Pace Errors'
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

                pairTrack = entry.get('pairTrack')
                if pairTrack:
                    pairedFingerprint = pairTrack.fingerprint
                    pairedUid         = pairTrack.uid
                else:
                    pairedFingerprint = ''
                    pairedUid         = ''

                self._csv.addRow({
                    'fingerprint':track.fingerprint,
                    'uid':track.uid,
                    'measured':entry['measured'].label,
                    'entered':entry['entered'].label,
                    'dev':sigmaCount,
                    'delta':delta,
                    'pairedUid':pairedUid,
                    'pairedFingerprint':pairedFingerprint})

        if not self._csv.save():
            self.logger.write('[ERROR]: Failed to save CSV file %s' % self._csv.path)

        percentage = NumericUtils.roundToOrder(100.0*float(highDeviationCount)/float(len(self.entries)), -2)
        self.logger.write('%s significant %s (%s%%)' % (highDeviationCount, label.lower(), percentage))
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


