from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json

from pyaid.file.FileUtils import FileUtils
from pyaid.system.SystemUtils import SystemUtils

import pandas as pd
import tables

#_______________________________________________________________________________
def initialize(my_path):
    if os.path.isfile(my_path):
        my_path = FileUtils.getDirectoryOf(my_path)

    path = FileUtils.makeFolderPath(my_path, 'data')
    SystemUtils.remove(path)
    os.makedirs(path)

    return path

#_______________________________________________________________________________
def create_metadata_dict():
    return {}

#_______________________________________________________________________________
def write_metadata_file(path, metadata):
    with open(path, 'w') as f:
        f.write(json.dumps(
            obj=metadata,
            separators=(',', ': '),
            indent=2,
            sort_keys=True))

#_______________________________________________________________________________
def validate_h5_data(path, test_key = None):
    try:
        data = tables.open_file(path)
        data.close()
    except Exception as err:
        print('[ERROR] Failed to open generated data file')
        raise err

    if not test_key:
        return

    # Test loading one of the dataframes
    try:
        pd.read_hdf(path, test_key)
    except Exception as err:
        print('[ERROR] Failed to load dataframe from file')
        raise err
