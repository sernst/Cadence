# PaceLengthStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import numpy as np
from pyaid.list.ListUtils import ListUtils
from pyaid.number.NumericUtils import NumericUtils
from pyaid.string.StringUtils import StringUtils

from cadence.analysis.AnalysisStage import AnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter
from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.enums.SnapshotDataEnum import SnapshotDataEnum
from cadence.svg.CadenceDrawing import CadenceDrawing


#*************************************************************************************************** PaceLengthStage
class PaceLengthStage(AnalysisStage):
    """ The primary analysis stage for validating the stride lengths between the digitally entered
        data and the catalog data measured in the field. """

#===================================================================================================
#                                                                                       C L A S S

    MAPS_FOLDER_NAME = 'Pace-Lengths'

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of PaceLengthStage."""
        super(PaceLengthStage, self).__init__(
            key, owner,
            label='Pace Length',
            **kwargs)

        self.noData  = 0
        self.count   = 0
        self.ignored = 0
        self.entries = []

        self._paths     = []
        self._csv       = None
        self._errorCsv  = None
        self._drawing   = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preDeviations
    def _preAnalyze(self):
        """_preDeviations doc..."""
        self.noData = 0
        self.entries = []
        self._paths = []

        self.initializeFolder(self.MAPS_FOLDER_NAME)

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

        csv = CsvWriter()
        csv.path = self.getPath('Pace-Match-Errors.csv', isFile=True)
        csv.autoIndexFieldName = 'Index'
        csv.addFields(
            ('uid', 'UID'),
            ('fingerprint', 'Fingerprint'),
            ('measured', 'Measured (m)') )
        self._errorCsv = csv

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        """_analyzeSitemap doc..."""

        self._drawing = CadenceDrawing(
            self.getPath(
                self.MAPS_FOLDER_NAME,
                '%s-%s-PACE.svg' % (sitemap.name, sitemap.level),
                isFile=True),
            sitemap)

        self._drawing.grid()
        self._drawing.federalCoordinates()

        super(PaceLengthStage, self)._analyzeSitemap(sitemap)

        self._drawing.save()
        self._drawing = None

#___________________________________________________________________________________________________ _analyzeTrackSeries
    def _analyzeTrackway(self, trackway, sitemap):
        bundle = self.owner.getSeriesBundle(trackway)

        for series in bundle.asList():
            self._drawSeries(self._drawing, series)

        tests = [
            (bundle.leftPes, bundle.rightPes),
            (bundle.leftManus, bundle.rightManus) ]

        for entry in tests:
            # Test both manus and pes pace pairings

            l = entry[0]
            r = entry[1]
            if l.count and l.isReady and r.count and r.isReady:
                self._analyzeSeriesPair(l, r)
                self._analyzeSeriesPair(r, l)
                continue

            for t in l.tracks + r.tracks:
                # Check all tracks in skipped series for pace measurements and log any tracks
                # with such measurements as errors
                if t.snapshotData.get(SnapshotDataEnum.PACE) is not None:
                    self._logUnresolvableTrack(t, 'Pace field measurement exists invalid series')

#___________________________________________________________________________________________________ _logUnresolvableTrack
    def _logUnresolvableTrack(self, track, message):
        """_logUnresolvableTrack doc..."""
        measured = NumericUtils.toValueUncertainty(
            track.snapshotData.get(SnapshotDataEnum.PACE), 0.06)

        self.ignored += 1
        self.logger.write([
            '[ERROR]: %s' % message,
            'TRACK: %s [%s]' % (track.fingerprint, track.uid),
            'PACE[field]: %s' % measured.label ])

        self._errorCsv.addRow({
            'uid':track.uid,
            'fingerprint':track.fingerprint,
            'measured':measured.label })

        self._drawing.circle(
            track.positionValue.toMayaTuple(), 10,
            stroke='none', fill='red', fill_opacity=0.5)

#___________________________________________________________________________________________________ _analyzeSeriesPair
    def _analyzeSeriesPair(self, series, pairSeries):
        """_analyzeSeriesPair doc..."""

        for index in ListUtils.range(series.count):
            track       = series.tracks[index]
            data        = track.snapshotData
            measured    = data.get(SnapshotDataEnum.PACE)
            if measured is None:
                self.noData += 1
                continue

            measured = NumericUtils.toValueUncertainty(measured, 0.06)

            pairTrack = self._getPairedTrack(track, series, pairSeries)
            if pairTrack is None:
                self._logUnresolvableTrack(track, 'Unable to determine pairSeries track')
                continue

            position = track.positionValue
            pairPosition = pairTrack.positionValue
            paceLine = LineSegment2D(position, pairPosition)

            if not paceLine.isValid:
                self._logUnresolvableTrack(track, 'Invalid track separation of 0.0. Ignoring track')
                continue

            entered    = paceLine.length
            delta      = entered.raw - measured.raw
            deviation  = delta/(measured.rawUncertainty + entered.rawUncertainty)
            fractional = delta/measured.raw
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
            self._drawPaceLine(self._drawing, paceLine, series.pes)
            track.cache.set('paceData', entry)

#___________________________________________________________________________________________________ _drawSeries
    @classmethod
    def _drawSeries(cls, drawing, series):
        """_drawSeries doc..."""

        if series.count == 0:
            return

        if series.pes:
            color = '#0033FF'
        else:
            color = '#00CC00'

        for track in series.tracks[:-1]:
            nextTrack = series.tracks[series.tracks.index(track) + 1]

            drawing.line(
                track.positionValue.toMayaTuple(),
                nextTrack.positionValue.toMayaTuple(),
                stroke=color, stroke_width=1, stroke_opacity='0.1')

            hasPace = bool(track.snapshotData.get(SnapshotDataEnum.PACE) is not None)
            drawing.circle(
                track.positionValue.toMayaTuple(), 5,
                stroke='none', fill=color, fill_opacity='0.75' if hasPace else '0.1')

        track = series.tracks[-1]
        hasPace = bool(track.snapshotData.get(SnapshotDataEnum.PACE) is not None)
        drawing.circle(
            track.positionValue.toMayaTuple(), 5,
            stroke='none', fill=color, fill_opacity='0.75' if hasPace else '0.1')

#___________________________________________________________________________________________________ _drawPaceLine
    @classmethod
    def _drawPaceLine(cls, drawing, line, isPes):
        """_drawPaceLine doc..."""

        drawing.line(
            line.start.toMayaTuple(), line.end.toMayaTuple(),
            stroke='black' if isPes else '#666666', stroke_width=1, stroke_opacity='1.0')

        drawing.circle(
            line.end.toMayaTuple(), 3, stroke='none', fill='black', fill_opacity='0.25')

        drawing.circle(
            line.start.toMayaTuple(), 3, stroke='none', fill='black', fill_opacity='0.25')

#___________________________________________________________________________________________________ _getPairedTrack
    def _getPairedTrack(self, track, trackSeries, pairSeries):
        """_getPairedTrack doc..."""

        analysisTrack = track.getAnalysisPair(self.analysisSession)

        index = trackSeries.tracks.index(track)
        nextTrack = trackSeries.tracks[index + 1] if index < (trackSeries.count - 1) else None
        nextAnalysisTrack = nextTrack.getAnalysisPair(self.analysisSession) if nextTrack else None

        for pt in pairSeries.tracks:
            # Iterate through all the tracks in the pair series and find the one that comes
            # immediately after the target track, and before the next track in the target series if
            # such a track exists

            apt = pt.getAnalysisPair(self.analysisSession)
            if apt.curvePosition < analysisTrack.curvePosition:
                # If the pair track appears before the target track, skip to the next track
                continue

            if nextAnalysisTrack and apt.curvePosition > nextAnalysisTrack.curvePosition:
                # If the pair track is past the next track position there is no pair track for this
                # pace segment
                return None

            return pt

        return None

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

        if not self._errorCsv.save():
            self.logger.write('[ERROR]: Failed to save CSV file %s' % self._errorCsv.path)

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


