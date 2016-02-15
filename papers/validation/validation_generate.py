from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from pyaid.file.FileUtils import FileUtils
from pyaid.system.SystemUtils import SystemUtils

import numpy as np
import os
import pandas as pd
import tables
from cadence.analysis.comparison.ComparisonAnalyzer import ComparisonAnalyzer
from cadence.analysis.shared import DataLoadUtils, PlotConfigs
from cadence.analysis.validation.ValidationAnalyzer import ValidationAnalyzer
from scipy.stats import norm

MY_DIR = FileUtils.getDirectoryOf(__file__)
DATA_DIR = FileUtils.makeFolderPath(MY_DIR, 'data')
OUT_PATH = FileUtils.makeFilePath(DATA_DIR, 'deviation.h5')
METADATA_FILE = FileUtils.makeFilePath(DATA_DIR, 'deviation.metadata.json')

#_______________________________________________________________________________
def generateData(name, df, key, binCount):
    """ Creates the data

    @param name:
        Name of the data file to be generated
    @param df:
        The source dataframe on which to generate data
    @param key:
        The key for the data within the dataframe
    @param binCount:
        Number of bins to use when generating histogram data

    @return:
        A list of dictionaries containing structural information for the data
        saved to output data file
    """

    structure = []
    xMin = df[key].min()
    xMax = min(3.0, df[key].max())
    count = df.shape[0]
    xValues = np.linspace(xMin, xMax, 64)
    bins = np.linspace(xMin, xMax, int(binCount))

    metadata = {
        'xMin':xMin,
        'xMax':xMax,
        'count':count,
        'size_counts':{},
        'bins':list(bins),
        'structure':structure
    }

    expected = []
    for x in xValues:
        expected.append(100.0*(1.0 - (norm.cdf(x) - norm.cdf(-x))))
    expectedDf = pd.DataFrame({
        'x': xValues,
        'y': expected
    })
    expectedDf.to_hdf(OUT_PATH, '{}/expected'.format(name))

    # Calculate for all size classes, including an "all"
    sizes = [{'id':'all'}] + PlotConfigs.SIZE_CLASSES

    for sizeClass in sizes:
        if 'index' in sizeClass:
            dataSlice = df.query('sizeClass == {}'.format(sizeClass['index']))
        else:
            dataSlice = df
        metadata['size_counts'][sizeClass['id']] = dataSlice.shape[0]

        sizeCount = dataSlice.shape[0]
        dataSlice = dataSlice.query('{} <= {}'.format(key, xMax))

        histValues = np.histogram(a=dataSlice[key].values, bins=bins)
        percentValues = histValues[0]/count
        soloPercentValues = histValues[0]/sizeCount

        histDf = pd.DataFrame({
            'x':histValues[1],
            'y':np.append(histValues[0], [0]),
            'y_fractional':np.append(percentValues, [0]),
            'y_fractional_solo':np.append(soloPercentValues, [0])})

        structure.append({
            'key':'{}/{}/histogram'.format(name, sizeClass['id']),
            'columns':list(histDf.columns.values)
        })

        histDf.to_hdf(OUT_PATH, key=structure[-1]['key'], mode='a')

        histValues = np.histogram(a=dataSlice[key].values, bins=xValues)
        areaValues = (sizeCount - np.cumsum(histValues[0]))/count
        soloAreaValues = (sizeCount - np.cumsum(histValues[0]))/sizeCount

        cdfDf = pd.DataFrame({
            'x':histValues[1],
            'y':np.append(areaValues, [0]),
            'y_solo':np.append(soloAreaValues, [0])
        })

        structure.append({
            'key':'{}/{}/cumulative'.format(name, sizeClass['id']),
            'columns':list(cdfDf.columns.values)
        })

        cdfDf.to_hdf(OUT_PATH, key=structure[-1]['key'], mode='a')

    return metadata

#_______________________________________________________________________________
def initialize():
    path = FileUtils.makeFolderPath(MY_DIR, 'data')
    SystemUtils.remove(path)
    os.makedirs(path)

    tracks = DataLoadUtils.getTrackWithAnalysis()
    return tracks[['uid', 'site', 'width', 'sizeClass']]

#_______________________________________________________________________________
def writeStructureFile(structure):
    with open(METADATA_FILE, 'w') as f:
        f.write(json.dumps(
            obj=structure,
            separators=(',', ': '),
            indent=2,
            sort_keys=True))

#_______________________________________________________________________________
def validate():
    try:
        data = tables.open_file(OUT_PATH)
        data.close()
    except Exception as err:
        print('[ERROR] Failed to open generated data file')
        raise err

    # Test loading one of the dataframes
    try:
        pd.read_hdf(OUT_PATH, '/stride/all/cumulative')
    except Exception as err:
        print('[ERROR] Failed to load dataframe from file')
        raise err

#_______________________________________________________________________________
def run(args):

    tracks = initialize()
    structure = {}

    #--- TRACK LENGTH & WIDTH ---#
    df = DataLoadUtils.getAnalysisData(
        analyzerClass=ComparisonAnalyzer,
        filename='Length-Width-Deviations.csv',
        renames={
            'Width Deviation':'widthDeviation',
            'Length Deviation':'lengthDeviation',
            'Fingerprint':'fingerprint',
            'UID':'uid'})

    df = pd.merge(df, tracks, left_on='uid', right_on='uid')

    structure['width'] = generateData( # Track Width
        name='width',
        key='widthDeviation',
        df=df.query('widthDeviation >= 0.0'),
        binCount=10.0)

    structure['length'] = generateData( # Track Length
        name='length',
        key='lengthDeviation',
        df=df.query('lengthDeviation >= 0.0'),
        binCount=10.0)

    #--- STRIDE LENGTH ---#
    df = DataLoadUtils.getAnalysisData(
        analyzerClass=ValidationAnalyzer,
        filename='Stride-Length-Deviations.csv',
        renames={'UID':'uid'})

    df = pd.merge(df, tracks, on='uid')

    structure['stride'] = generateData('stride', df, 'Deviation', 10.0)

    #--- PACE LENGTH ---#
    df = DataLoadUtils.getAnalysisData(
        analyzerClass=ValidationAnalyzer,
        filename='Pace-Length-Deviations.csv',
        renames={'UID':'uid'})

    df = pd.merge(df, tracks, on='uid')

    structure['pace'] = generateData('pace', df, 'Deviation', 10.0)

    writeStructureFile(structure)

    validate()

#_______________________________________________________________________________
if __name__ == '__main__':
    from argparse import ArgumentParser
    from textwrap import dedent
    parser = ArgumentParser()

    parser.description = dedent("""
        ValidationPaper does...""")

    run(parser.parse_args())
