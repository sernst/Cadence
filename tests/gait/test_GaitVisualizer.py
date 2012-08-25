# test_GaitVisualizer.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

import os
import random

from cadence.shared.io.CadenceData import CadenceData
from cadence.mayan.gait.GaitVisualizer import GaitVisualizer

#---------------------------------------------------------------------------------------------------
# GET CONFIG FILE
dataPath = os.path.join(CadenceData.ROOT_DATA_PATH, 'GaitGenerator')
items    = []
for f in os.listdir(dataPath):
    path = os.path.join(dataPath, f)
    if not os.path.isfile(path) or not f.endswith(CadenceData.EXTENSION):
        continue
    items.append(os.path.join('GaitGenerator', f))

dataFile = str(items[random.randint(0,len(items) - 1)])
print 'LOADING data file: ' + dataFile

gv = GaitVisualizer(dataFile)
gv.buildScene()
