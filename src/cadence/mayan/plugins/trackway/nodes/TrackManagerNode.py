# TrackManagerNode.py
# (C)2014
# Scott Ernst

from maya import OpenMaya
from maya import OpenMayaMPx

from cadence.mayan.plugins.MayaPluginNode import MayaPluginNode
from cadence.mayan.plugins.attrs.MessageNodeAttribute import MessageNodeAttribute
from cadence.mayan.plugins.attrs.NumericNodeAttribute import NumericNodeAttribute

#___________________________________________________________________________________________________ TrackManagerNode
class TrackManagerNode(MayaPluginNode):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    NODE_NAME       = 'trackManager'
    NODE_ID         = 0x3F3F3F
    NODE_TYPE       = OpenMayaMPx.MPxNode.kDependNode
    NODE_LOCATION   = 'utility/general'

    input  = NumericNodeAttribute(
        'i', 'input', 0, OpenMaya.MFnNumericData.kInt, affects='output')
    output = NumericNodeAttribute(
        'o', 'output', 0, OpenMaya.MFnNumericData.kInt, compute='outputCompute')
    tracks = MessageNodeAttribute('ts', 'tracks', array=True)

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        """Creates a new instance of TrackManagerNode."""
        MayaPluginNode.__init__(self)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ outputCompute
    def outputCompute(self, data):
        value = data.inHandles.input.asInt()
        data.outHandles.output.setInt(2*value)
        data.outHandles.cleanAll()


