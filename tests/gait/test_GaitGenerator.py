import sys

from cadence.generator.gait.GaitGenerator import GaitGenerator
from cadence.shared.io.CadenceData import CadenceData

g = GaitGenerator(gaitConfig='gait/PH-20_DF-70_OFF-50.cfg')
if g.run():
    print 'SUCCESS: GaitGenerator.run()'
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