import sys

from cadence.config.enum.GeneralConfigEnum import GeneralConfigEnum
from cadence.shared.io.CadenceData import CadenceData

filename = 'GaitGenerator/p0.0_f0.5_h0.5.cadence'

cd = CadenceData()
if cd.loadFile(filename):
    print 'SUCCESS: CadenceData.loadFile()'
    print 'Loaded from output file: ' + filename
else:
    print 'FAILED: CadenceData.loadFile()'
    print 'Unable to load output file: ' + filename
    sys.exit(1)

print cd.configs
if cd.configs:
    print 'SUCCESS: Configs available'
    print cd.configs.toDict()

print '\n',100*'-'
print 'CONFIGS TESTS:'
print 'TEST [GeneralConfigEnum.STEPS]:', cd.configs.get(GeneralConfigEnum.STEPS)
print 'TEST [GeneralConfigEnum.START_TIME]:', cd.configs.get(GeneralConfigEnum.START_TIME)

print '\n',100*'-'
print 'CHANNEL ACCESS TESTS:'
print 'TEST [getChannelByName()]:', cd.getChannelByName(cd.channels[0].name)
print 'TEST [getChannelsByKind()]:', cd.getChannelsByKind(cd.channels[0].kind)
print 'TEST [getChannelsByTarget()]:', cd.getChannelsByTarget(cd.channels[0].target)

channel = cd.channels[0]

print '\n',100*'-'
print 'CHANNEL TESTS:'
print 'TEST [channel.times]:', channel.times
print 'TEST [channel.values]:', channel.values

print 'Test complete.'