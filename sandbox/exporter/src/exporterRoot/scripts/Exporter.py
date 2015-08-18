# Exporter.py
# (C)2014
# Kent A. Stevens

from nimble import cmds
from nimble import NimbleScriptBase

from cadence.enums.TrackPropEnum import TrackPropEnum
from exporterRoot.scripts.Track import Track

#*******************************************************************************
class Exporter(NimbleScriptBase):
    """A class for exporting the attributes of a Maya scene to JSON."""

#===============================================================================
#                                                                   C L A S S


#===============================================================================
#                                                                 P U B L I C

#_______________________________________________________________________________
    def isTrackNode(self, n):
        return cmds.attributeQuery(TrackPropEnum.SITE.name, node=n, exists=True)

#_______________________________________________________________________________
    def run(self):
        selectedNodes = cmds.ls(selection=True, exactType='transform')
        tracks = list()

        for n in selectedNodes:
            if self.isTrackNode(n):
                tracks.append(Track(n))

        print "number tracks = %s" % len(tracks)

        dicts = list()
        for t in tracks:
            dicts.append(t.getProperties())
        self.put('dictionaryList', dicts)
