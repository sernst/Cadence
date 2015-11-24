from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pyaid.file.CsvWriter import CsvWriter
from pyaid.file.FileUtils import FileUtils

from collections import namedtuple
import six
from cadence import reporting
from cadence.analysis.shared import DataLoadUtils
from cadence.enums.TrackCsvColumnEnum import TrackCsvColumnEnum
from cadence.enums.TrackPropEnum import TrackPropEnum

MY_DIR = FileUtils.getDirectoryOf(__file__)
DATA_DIR = FileUtils.makeFolderPath(MY_DIR, 'data')
OUT_PATH = FileUtils.makeFilePath(DATA_DIR, 'beb500.h5')
METADATA_FILE = FileUtils.makeFilePath(DATA_DIR, 'beb500.metadata.json')

TCCE = TrackCsvColumnEnum
TPE = TrackPropEnum

ENTRY = namedtuple('ENTRY', ['label', 'src', 'dest'])

CONVERSIONS = [
    ENTRY('Index', TCCE.INDEX, None),
    ENTRY('Tracksite', TCCE.TRACKSITE, TPE.SITE),
    ENTRY('Level', TCCE.LEVEL, TPE.LEVEL),
    ENTRY('Trackway', TCCE.TRACKWAY, None),
    ENTRY('Excavation Area', TCCE.SECTOR, TPE.SECTOR),
    ENTRY('E', TCCE.ENTRY_AZIMUTH, ''),
    ENTRY('S', TCCE.EXIT_AZIMUTH, ''),
    ENTRY('D', TCCE.TOTAL_AZIMUTH, ''),
    ENTRY('Trackway Length m', TCCE.TRACKWAY_LENGTH, ''),
    ENTRY('Comment', TCCE.COMMENT, ''),
    ENTRY('deviation E-S', TCCE.AZIMUTH_DEVIATION, ''),
    ENTRY('Mean_ES', TCCE.AZIMUTH_MEAN, ''),
    ENTRY('Mean_ES-D', TCCE.AZIMUTH_MEAN_DEVIATION, ''),
    ENTRY('Orientation', TCCE.ORIENTATIONS, ''),
    ENTRY('Outline drawing on plastic sheet', TCCE.OUTLINE_DRAWING, ''),
    ENTRY('Sample', TCCE.PRESERVED, 'non'),
    ENTRY('Cast', TCCE.CAST, 'non'),
    ENTRY('Name "Cast"', TCCE.MEASURED_BY, ''),
    ENTRY('Date "Cast"', TCCE.MEASURED_DATE, ''),
    ENTRY('Name data entry', TCCE.DATA_ENTERED_BY, 'CADENCE'),
    ENTRY('Date data entry', TCCE.DATA_ENTRY_DATE, ''),
    ENTRY('Pes / Manus', TCCE.TRACK_NAME, None),
    ENTRY('Missing', TCCE.MISSING, ''),
    ENTRY('Pes length cm', TCCE.PES_LENGTH, TPE.LENGTH),
    ENTRY('Pes length cm*', TCCE.PES_LENGTH_GUESS, ''),
    ENTRY('Pes width cm', TCCE.PES_WIDTH, TPE.WIDTH),
    ENTRY('Pes width cm*', TCCE.PES_WIDTH_GUESS, ''),
    ENTRY('Pes depth cm', TCCE.PES_DEPTH, ''),
    ENTRY('Pes depth cm*', TCCE.PES_DEPTH_GUESS, ''),
    ENTRY('LP rotation degree', TCCE.LEFT_PES_ROTATION, ''),
    ENTRY('LP rotation degree*', TCCE.LEFT_PES_ROTATION_GUESS, ''),
    ENTRY('RP rotation degree', TCCE.RIGHT_PES_ROTATION, ''),
    ENTRY('RP rotation degree*', TCCE.RIGHT_PES_ROTATION_GUESS, ''),
    ENTRY('Manus length cm', TCCE.MANUS_LENGTH, TPE.LENGTH),
    ENTRY('Manus length cm*', TCCE.MANUS_LENGTH_GUESS, ''),
    ENTRY('Manus width cm', TCCE.MANUS_WIDTH, TPE.WIDTH),
    ENTRY('Manus width cm*', TCCE.MANUS_WIDTH_GUESS, ''),
    ENTRY('Manus depth cm', TCCE.MANUS_DEPTH, ''),
    ENTRY('Manus depth cm*', TCCE.MANUS_DEPTH_GUESS, ''),
    ENTRY('LM rotation degree', TCCE.LEFT_MANUS_ROTATION, ''),
    ENTRY('LM rotation degree*', TCCE.LEFT_MANUS_ROTATION_GUESS, ''),
    ENTRY('RM rotation degree', TCCE.RIGHT_MANUS_ROTATION, ''),
    ENTRY('RM rotation degree*', TCCE.RIGHT_MANUS_ROTATION_GUESS, ''),
    ENTRY('P stride cm', TCCE.PES_STRIDE, ''),
    ENTRY('P stride cm*', TCCE.PES_STRIDE_GUESS, ''),
    ENTRY('P stride factor', TCCE.PES_STRIDE_FACTOR, ''),
    ENTRY('P stride factor', TCCE.PES_STRIDE_FACTOR, '')
]

#_______________________________________________________________________________
def get_key(entry):
    try:
        return entry.name
    except:
        try:
            return entry['name']
        except:
            return entry

#_______________________________________________________________________________
def convert_value(spec, track, tracks):
    is_left = track[TPE.LEFT.name]
    is_pes = track[TPE.PES.name]

    if spec.src == TCCE.TRACKWAY:
        return '{} {}'.format(
            track[TPE.TRACKWAY_TYPE.name],
            track[TPE.TRACKWAY_NUMBER.name])

    if spec.src == TCCE.TRACK_NAME:
        return '{}{}{}'.format(
            'L' if is_left else 'R',
            'P' if is_pes else 'M',
            track[TPE.NUMBER.name])

    if spec.src in [TCCE.PES_WIDTH, TCCE.PES_LENGTH]:
        if not is_pes:
            return ''
        return 100.0*track[get_key(spec.dest)]

    if spec.src in [TCCE.MANUS_WIDTH, TCCE.MANUS_LENGTH]:
        if is_pes:
            return ''
        return 100.0*track[get_key(spec.dest)]

    if not spec.dest:
        return ''
    elif isinstance(spec.dest, six.string_types):
        return spec.dest

    return track[get_key(spec.dest)]

#_______________________________________________________________________________
def create_export_entry(index, track, tracks):
    out = {TCCE.INDEX.name:index}
    for spec in CONVERSIONS:
        if spec.src == TCCE.INDEX:
            continue

        out[get_key(spec.src)] = convert_value(spec, track, tracks)
    return out

#_______________________________________________________________________________
def generateData(tracks):
    trackway_number = tracks.iloc[0]['trackwayNumber']
    metadata = {
        'key':'/trackway/tw_{}'.format(trackway_number),
        'count':len(tracks)
    }

    df = tracks.sort_values(['number', 'pes', 'left'], ascending=[1, 0, 0])
    df = df.copy()
    df['number'] = df['number'].str.lstrip('0')

    fields = []
    for entry in CONVERSIONS:
        fields.append((get_key(entry.src), entry.label))

    csv = CsvWriter(
        path=FileUtils.makeFilePath(
            DATA_DIR,
            'BEB-500 S-{}.csv'.format(trackway_number)),
        fields=fields)

    for index, track in df.iterrows():
        csv.addRow(create_export_entry(index, track, tracks))

    csv.save()
    df.to_hdf(OUT_PATH, key=metadata['key'], mode='a')

    return metadata

#_______________________________________________________________________________
def run(args):

    reporting.initialize(__file__)
    metadata = reporting.create_metadata_dict()

    tracks = DataLoadUtils.readTable('tracks')
    tracks = tracks.query('site == "BEB" and level == "500"').copy()
    tracks['number'] = tracks['number'].str.zfill(4)

    for trackwayNumber in tracks['trackwayNumber'].unique():
        metadata[trackwayNumber] = generateData(
            tracks=tracks.query('trackwayNumber == "{}"'.format(
                trackwayNumber) ))

    reporting.write_metadata_file(METADATA_FILE, metadata)
    reporting.validate_h5_data(OUT_PATH, test_key='/trackway/tw_1')

#_______________________________________________________________________________
if __name__ == '__main__':
    from argparse import ArgumentParser
    from textwrap import dedent
    parser = ArgumentParser()

    parser.description = dedent("""
        ValidationPaper does...""")

    run(parser.parse_args())

