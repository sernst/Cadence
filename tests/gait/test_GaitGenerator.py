import os
import sys
import random

from cadence.config.ConfigReader import ConfigReader
from cadence.generator.gait.GaitGenerator import GaitGenerator
from cadence.shared.io.CadenceData import CadenceData

#---------------------------------------------------------------------------------------------------
# GET CONFIG FILE
configPath = os.path.join(ConfigReader.DEFAULT_CONFIG_PATH, 'gait')
cfgs       = []
for f in os.listdir(configPath):
    path = os.path.join(configPath, f)
    if not os.path.isfile(path) or not f.endswith(ConfigReader.EXTENSION):
        continue
    cfgs.append(os.path.join('gait', f))

configFile = str(cfgs[random.randint(0,len(cfgs) - 1)])
print 'INITIALIZING Config file: ' + configFile

#---------------------------------------------------------------------------------------------------
# GET CONFIG FILE
g = GaitGenerator(gaitConfig=configFile)
if g.run():
    print 'SUCCESS: GaitGenerator.run()'
    g.echo()
else:
    print 'FAILED: GaitGenerator.run()'
    sys.exit(1)

if g.saveToFile():
    print 'SUCCESS: GaitGenerator.saveToFile()'
    print 'Saved output as: ' + g.name
else:
    print 'FAILED: GaitGenerator.saveToFile()'
    print 'Unable to save output as: ' + g.name
    sys.exit(1)

cd = CadenceData()
if cd.loadFile(g.dataFilename):
    print 'SUCCESS: CadenceData.loadFile()'
    print 'Loaded from output file: ' + g.dataFilename
else:
    print 'FAILED: CadenceData.loadFile()'
    print 'Unable to load output file: ' + g.dataFilename
    sys.exit(1)

print 'Test complete.'
