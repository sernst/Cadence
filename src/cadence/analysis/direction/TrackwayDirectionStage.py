# TrackwayDirectionStage.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from collections import namedtuple
import math

from pyaid.number.NumericUtils import NumericUtils

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.shared.LineSegment2D import LineSegment2D
from cadence.analysis.shared.PositionValue2D import PositionValue2D
from cadence.analysis.shared.plotting.MultiScatterPlot import MultiScatterPlot
from cadence.svg.CadenceDrawing import CadenceDrawing

#*************************************************************************************************** TrackwayDirectionStage
class TrackwayDirectionStage(CurveOrderedAnalysisStage):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    SAMPLE_DATA_NT = namedtuple('SAMPLE_DATA_NT', [
        'directionAngle', # Angle  instance for the calculated trackway heading
        'position', # Spatial position of the angle reference point
        'curvePoint', # For plotting (curvePosition, directionAngle, curvePosUnc, directionAngleUnc)
        'curvePosition', # ValueUncertainty object representing position along curve
        'track' ]) # Track used to reference this sample

    MAPS_FOLDER_NAME = 'Trackway-Direction'

    COLORS = ['#AAAAAA', 'black', 'blue', 'green', 'red']

#_______________________________________________________________________________
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of TrackwayDirectionStage."""
        super(TrackwayDirectionStage, self).__init__(
            key, owner,
            label='Trackway Direction',
            **kwargs)
        self._paths = []

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def trackHeadingData(self):
        return self.owner.getStage('heading').trackwaysData

#_______________________________________________________________________________
    @property
    def trackwayDirectionData(self):
        return self.owner.cache.get('trackwayDirectionData')

#===============================================================================
#                                                                               P R O T E C T E D

#_______________________________________________________________________________
    def _preAnalyze(self):
        self.owner.cache.set('trackwayDirectionData', {})

#_______________________________________________________________________________
    def _analyzeSitemap(self, sitemap):
        """_analyzeSitemap doc..."""

        self._createDrawing(sitemap, 'SAMPLED-DIRECTION', self.MAPS_FOLDER_NAME)
        super(TrackwayDirectionStage, self)._analyzeSitemap(sitemap)
        self._saveDrawing(sitemap)

#_______________________________________________________________________________
    def _analyzeTrackway(self, trackway, sitemap):
        if trackway.uid not in self.trackHeadingData:
            return

        bundle = self.owner.getSeriesBundle(trackway)

        # Create a list of window sizes to test trimmed to account for small trackways with fewer
        # points than a specified size
        maxWindowSize = min(8, int(0.5*float(bundle.count)))
        windowSizes = [1, 2, 4, 6, 8]
        while maxWindowSize < windowSizes[-1]:
            windowSizes.pop()

        samples = []

        for i in windowSizes:
            # For each valid window size create a sample entry
            samples.append({'size':i + 1, 'values':self._sampleTrackway(trackway, i + 1) })

        self._plotTrackwaySamples(trackway, samples)
        self._drawTrackwaySamples(sitemap, samples)

        self.trackwayDirectionData[trackway.uid] = {'trackway':trackway, 'samples':samples}

#_______________________________________________________________________________
    def _drawTrackwaySamples(self, sitemap, samples):
        """_drawTrackwaySamples doc..."""

        drawing = sitemap.cache.get('drawing')

        for sample in samples:
            color = self.COLORS[samples.index(sample)]

            if len(sample['values']) < 2:
                continue

            prev = sample['values'][0].position

            for value in sample['values'][1:]:
                pos = value.position
                drawing.line(
                    prev.toMayaTuple(), pos.toMayaTuple(),
                    stroke=color, stroke_width=1, stroke_opacity='0.75')
                prev = pos

            for value in sample['values']:
                pos = value.position
                drawing.circle(
                    pos.toMayaTuple(), 5,
                    stroke='none', fill=color, fill_opacity='0.75')

#_______________________________________________________________________________
    def _plotTrackwaySamples(self, trackway, samples):
        """_plotTrackwaySamples doc..."""

        bundle = self.owner.getSeriesBundle(trackway)

        plot = MultiScatterPlot(
            title='%s Direction Sampling %s' % (trackway.name, bundle.echoStatus(asPercent=True)),
            xLabel='Trackway Curve Position (m)',
            yLabel='Direction (degrees)')

        for sample in samples:
            color = self.COLORS[samples.index(sample)]
            data = []

            for value in sample['values']:
                data.append(value.curvePoint)

            plot.addPlotSeries(data=data, color=color, line=True)

        self._paths.append(plot.save(self.getTempFilePath(extension='pdf')))

#_______________________________________________________________________________
    def _sampleTrackway(self, trackway, windowSize):
        """
            Samples the trackway and returns result
            @type trackway: * """

        window = []
        samples = []

        entries = self.trackHeadingData[trackway.uid]['entries']
        analysisTrackway = trackway.getAnalysisPair(self.analysisSession)

        for entry in entries:
            # For each track entry in the trackways data add that to the sample window and update
            # the samples result

            window.append(entry)

            if len(window) < windowSize:
                # Don't create a sample until the sub-sample list exceeds the sample window size
                continue

            xTests        = [] # X spatial position values
            yTests        = [] # Y spatial position values
            angleTests    = [] # Heading angle values
            curvePosTests = [] # Curve position values
            for item in window:
                # Calculate weighted averages for various properties of the current sample window

                angle = item.headingAngle
                angleTests.append(angle.valueDegrees)

                # Create a ValueUncertainty for the curve position by using the fractional
                # positional uncertainty over the spatial length of the curve
                posValue = item.track.positionValue
                posUnc = math.sqrt(posValue.xUnc**2 + posValue.yUnc**2)
                curvePos = item.track.getAnalysisPair(self.analysisSession).curvePosition
                curvePosUnc = abs(posUnc/analysisTrackway.curveLength)
                curvePosTests.append(NumericUtils.toValueUncertainty(curvePos, curvePosUnc))

                pv = item.track.positionValue
                xTests.append(pv.xValue)
                yTests.append(pv.yValue)

            directionAngleMean = NumericUtils.weightedAverage(*angleTests)
            curvePositionMean = NumericUtils.weightedAverage(*curvePosTests)
            xValue = NumericUtils.weightedAverage(*xTests)
            yValue = NumericUtils.weightedAverage(*yTests)
            position = PositionValue2D(
                x=xValue.raw, xUnc=xValue.rawUncertainty,
                y=yValue.raw, yUnc=yValue.rawUncertainty)

            # Remove the oldest sample from the to make room for a new sample in the next iteration
            window.pop(0)

            if len(samples) > 0:
                # Compare this sample to the previous one and if it does not differ
                # significantly then continue to continue to the next iteration
                last = samples[-1].directionAngle
                totalUnc = last.rawUncertainty + directionAngleMean.rawUncertainty
                deviation = abs(directionAngleMean.raw - last.raw)/totalUnc
                if deviation < 2.0:
                    continue

            samples.append(self.SAMPLE_DATA_NT(
                directionAngle=directionAngleMean,
                position=position,
                curvePoint=(
                    curvePositionMean.value, directionAngleMean.value,
                    curvePositionMean.uncertainty, directionAngleMean.uncertainty),
                curvePosition=curvePositionMean,
                track=entry.track ))

        self._extendSamplesToTrackwayStart(entries[0], samples)
        self._extendSampleToTrackwayEnd(entries[-1], samples)
        return samples

#_______________________________________________________________________________
    def _extendSamplesToTrackwayStart(self, firstEntry, samples):
        """_extendSamplesToTrackwayStart doc..."""

        if len(samples) < 2 or samples[0].track == firstEntry.track:
            # If there aren't enough samples, or the samples already extend to the end of the
            # trackway, return the samples without adding on an end point
            return

        line = LineSegment2D(
            start=samples[0].position.clone(),
            end=samples[1].position.clone())

        firstTrack = firstEntry.track
        analysisTrack = firstTrack.getAnalysisPair(self.analysisSession)
        position = line.closestPointOnLine(firstTrack.positionValue, False)

        samples.insert(0, self.SAMPLE_DATA_NT(
            directionAngle=samples[0].directionAngle.clone(),
            position=position,
            curvePoint=(
                analysisTrack.curvePosition, samples[0].directionAngle.value,
                0, samples[-1].directionAngle.uncertainty),
            curvePosition=samples[0].curvePosition.clone(),
            track=firstTrack ))

#_______________________________________________________________________________
    def _extendSampleToTrackwayEnd(self, lastEntry, samples):

        if len(samples) < 2 or samples[-1].track == lastEntry.track:
            # If there aren't enough samples, or the samples already extend to the end of the
            # trackway, return the samples without adding on an end point
            return

        line = LineSegment2D(
            start=samples[-2].position.clone(),
            end=samples[-1].position.clone())

        lastTrack = lastEntry.track
        analysisTrack = lastTrack.getAnalysisPair(self.analysisSession)
        position = line.closestPointOnLine(lastTrack.positionValue, False)

        ha = samples[-1].directionAngle.clone()
        samples.append(self.SAMPLE_DATA_NT(
            directionAngle=ha,
            position=position,
            curvePoint=(analysisTrack.curvePosition, ha.value, 0, ha.uncertainty),
            curvePosition=samples[-1].curvePosition.clone(),
            track=lastTrack ))

#_______________________________________________________________________________
    def _postAnalyze(self):
        self.mergePdfs(self._paths, 'Trackway-Direction.pdf')
