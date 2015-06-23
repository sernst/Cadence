# KMeansClusterStage.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import os

import pandas as pd

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.analysis.AnalysisStage import AnalysisStage


#*************************************************************************************************** KMeansClusterStage
class KMeansClusterStage(AnalysisStage):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    COLORS = ['#CCCCCC', 'red', 'orange', 'green', 'blue', 'purple']

#___________________________________________________________________________________________________ __init__
    def __init__(self, key, owner, **kwargs):
        """Creates a new instance of KMeansClusterStage."""
        super(KMeansClusterStage, self).__init__(
            key, owner,
            label='Track Priority Report',
            **kwargs)

        self._frame = None

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _preAnalyze
    def _preAnalyze(self):
        self._frame = None

        path = CadenceEnvironment.getPath(
            '..', 'statistics', 'output', 'Clustered-Tracks.csv', isFile=True)

        if not os.path.exists(path):
            return

        self._frame = pd.read_csv(path)

#___________________________________________________________________________________________________ _analyzeSitemap
    def _analyzeSitemap(self, sitemap):
        if self._frame is None:
            return

        self._createDrawing(sitemap, 'TRACK-CLUSTERS', 'Track-Clusters')
        super(KMeansClusterStage, self)._analyzeSitemap(sitemap)
        self._saveDrawing(sitemap)

#___________________________________________________________________________________________________ _analyzeTrack
    def _analyzeTrack(self, track, series, trackway, sitemap):
        color = self.COLORS[0]
        try:
            data = self._frame.loc[self._frame['uid'] == track.uid]
            color = self.COLORS[int(data.cluster)]
        except Exception:
            color = self.COLORS[0]

        sitemap.cache.get('drawing').circle(
            track.positionValue.toMayaTuple(), 5, stroke='none', fill=color, fill_opacity='0.5')


