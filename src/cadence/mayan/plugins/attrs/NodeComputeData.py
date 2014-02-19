# NodeComputeData.py
# (C)2014
# Scott Ernst

from cadence.mayan.plugins.attrs.NodeComputeHandles import NodeComputeHandles

#___________________________________________________________________________________________________ NodeComputeData
class NodeComputeData(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, node, definition, plug, dataBlock):
        """Creates a new instance of NodeComputeData."""
        self._node          = node
        self._definition    = definition
        self._plug          = plug
        self._dataBlock     = dataBlock

        self._inputHandles  = None
        self._outputHandles = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: inHandles
    @property
    def inHandles(self):
        if self._inputHandles is None:
            self._inputHandles = NodeComputeHandles(self, True)
        return self._inputHandles

#___________________________________________________________________________________________________ GS: outHandles
    @property
    def outHandles(self):
        if self._outputHandles is None:
            self._outputHandles = NodeComputeHandles(self, False)
        return self._outputHandles

#___________________________________________________________________________________________________ GS: node
    @property
    def node(self):
        return self._node

#___________________________________________________________________________________________________ GS: definition
    @property
    def definition(self):
        return self._definition

#___________________________________________________________________________________________________ GS: plug
    @property
    def plug(self):
        return self._plug

#___________________________________________________________________________________________________ GS: dataBlock
    @property
    def dataBlock(self):
        return self._dataBlock

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return unicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
