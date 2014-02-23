# exporter.py
# (C)2013
# Kent A. Stevens


import sys

from pyaid.file.FileUtils import FileUtils
from pyaid.json.JSON import JSON
import nimble

# Add the src path for this example to the python system path for access to the scripts
scriptPath = FileUtils.createPath(FileUtils.getDirectoryOf(__file__), 'src', isDir=True)
sys.path.append(scriptPath)

from exporterRoot.scripts import Exporter

conn = nimble.getConnection()

result = conn.addToMayaPythonPath(scriptPath)
if not result.success:
    print 'Unable to modify Maya Python path. Are you sure Maya is running a Nimble server?'
    print result
    sys.exit(1)

result = conn.runPythonModule(Exporter, runInMaya=True)
if not result.success:
    print 'Oh no, something went wrong!', result
    sys.exit(1)
else:
    dicts = result.payload['dictionaryList']

JSON.toFile('test.json', dicts, gzipped=False)
