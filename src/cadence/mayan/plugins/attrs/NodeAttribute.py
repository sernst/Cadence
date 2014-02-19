# NodeAttribute.py
# (C)2014
# Scott Ernst

from maya import OpenMaya

from pyaid.ArgsUtils import ArgsUtils

from cadence.mayan.plugins.attrs.NodeComputeData import NodeComputeData

#___________________________________________________________________________________________________ NodeAttribute
class NodeAttribute(OpenMaya.MObject):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, shortFlag, longFlag, **kwargs):
        """Creates a new instance of NodeAttribute."""
        OpenMaya.MObject.__init__(self)
        self._shortFlag     = shortFlag
        self._longFlag      = longFlag
        self._kwargs        = kwargs
        self.name           = None
        self.nodeClass      = None
        self.attr           = None
        self._affects       = ArgsUtils.getAsList('affects', kwargs)
        self._computeName   = ArgsUtils.get('compute', None, kwargs)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: isComputable
    @property
    def isComputable(self):
        return self._computeName is not None

#___________________________________________________________________________________________________ GS: affects
    @property
    def affects(self):
        return self._affects

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getInputHandle
    def getInputHandle(self, dataBlock):
        return dataBlock.inputValue(self.attr)

#___________________________________________________________________________________________________ getOutputHandle
    def getOutputHandle(self, dataBlock):
        return dataBlock.outputValue(self.attr)

#___________________________________________________________________________________________________ initializeAttribute
    def initializeAttribute(self, nodeClass, name):
        self.nodeClass = nodeClass
        self.name      = name

        attrFn         = self._createAttributeFn()
        attr           = self._createAttribute(attrFn)

        if not attr:
            return attr

        attrFn.setWritable(ArgsUtils.get('writable', True, self._kwargs))
        attrFn.setStorable(ArgsUtils.get('storable', True, self._kwargs))
        attrFn.setHidden(ArgsUtils.get('hidden', False, self._kwargs))
        attrFn.setArray(ArgsUtils.get('array', False, self._kwargs))
        attrFn.setCached(ArgsUtils.get('cached', False, self._kwargs))
        attrFn.setConnectable(ArgsUtils.get('connectable', True, self._kwargs))

        self.attr = attr
        return attr

#___________________________________________________________________________________________________ compute
    def compute(self, node, plug, dataBlock):
        if not self._computeName:
            return

        computeFunc = getattr(node, self._computeName)
        if computeFunc is None:
            return
        return computeFunc(NodeComputeData(node, self, plug, dataBlock))

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _createAttributeFn
    def _createAttributeFn(self):
        return None

#___________________________________________________________________________________________________ _createAttribute
    def _createAttribute(self, attrFn):
        return None
