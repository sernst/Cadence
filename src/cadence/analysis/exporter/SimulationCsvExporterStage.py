# SimulationCsvExporterStage.py
# (C)2015
# Scott Ernst

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from pyaid.file.FileUtils import FileUtils

from cadence.analysis.CurveOrderedAnalysisStage import CurveOrderedAnalysisStage
from cadence.analysis.shared.CsvWriter import CsvWriter


class SimulationCsvExporterStage(CurveOrderedAnalysisStage):
    """A class for..."""

    def __init__(self, key, owner, **kwargs):
        super(SimulationCsvExporterStage, self).__init__(
            key, owner,
            label='Simulation Exporter',
            **kwargs
        )

        self.entries = None

    def _analyzeTrackway(self, trackway, sitemap):
        """

        @param trackway:
        @param sitemap:
        @return:
        """

        self.entries = dict(lp=[], rp=[], lm=[], rm=[])

        super(SimulationCsvExporterStage, self)._analyzeTrackway(
            trackway=trackway,
            sitemap=sitemap
        )

        csv = CsvWriter(
            autoIndexFieldName='Index',
            fields=[
                'lp_name', 'lp_uid', 'lp_x', 'lp_dx', 'lp_y', 'lp_dy',
                'rp_name', 'rp_uid', 'rp_x', 'rp_dx', 'rp_y', 'rp_dy',
                'lm_name', 'lm_uid', 'lm_x', 'lm_dx', 'lm_y', 'lm_dy',
                'rm_name', 'rm_uid', 'rm_x', 'rm_dx', 'rm_y', 'rm_dy'
            ]
        )

        length = max(
            len(self.entries['lp']),
            len(self.entries['rp']),
            len(self.entries['lm']),
            len(self.entries['rm']),
        )

        for index in range(length):
            items = []
            for limb_id, entries in self.entries.items():
                if index < len(entries):
                    items += entries[index].items()
                else:
                    items += self._create_entry(limb_id).items()
            csv.addRow(dict(items))

        path = self.owner.settings.fetch('EXPORT_DATA_PATH')
        if path is None:
            path = self.owner.getLocalPath('Simulation', 'data', isFile=True)
        path = FileUtils.makeFilePath(path, trackway.name, 'source.csv')

        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if csv.save(path):
            print('[SAVED]:', path)
        else:
            print('[ERROR]: Unable to save CSV at "{}"'.format(path))

    def _analyzeTrack(self, track, series, trackway, sitemap):
        """

        @param track:
        @param series:
        @param trackway:
        @param sitemap:
        @return:
        """

        limb_id = '{}{}'.format(
            'l' if track.left else 'r',
            'p' if track.pes else 'm'
        )

        self.entries[limb_id].append(self._create_entry(limb_id, track))

    @classmethod
    def _create_entry(cls, limb_id, track = None):
        """

        @param limb_id:
        @param track:
        @return:
        """

        pos = track.positionValueRaw if track else None
        return dict([
            (limb_id + '_x', pos.x if pos else ''),
            (limb_id + '_dx', pos.xUnc if pos else ''),
            (limb_id + '_y', pos.y if pos else ''),
            (limb_id + '_dy', pos.yUnc if pos else ''),
            (limb_id + '_name', track.fingerprint if track else ''),
            (limb_id + '_uid', track.uid if track else '')
        ])
