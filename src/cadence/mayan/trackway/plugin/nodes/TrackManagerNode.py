# TrackManagerNode.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

try:
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    from maya import OpenMaya
    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    from maya import OpenMayaMPx
except Exception:
    maya = None

from elixir.nodes.ElixirNode import ElixirNode
from elixir.nodes.attrs.MessageNodeAttribute import MessageNodeAttribute
from elixir.nodes.attrs.NumericNodeAttribute import NumericNodeAttribute

#_______________________________________________________________________________
class TrackManagerNode(ElixirNode):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    NODE_NAME       = 'trackManager'
    NODE_ID         = 0x3F3F3F
    NODE_TYPE       = OpenMayaMPx.MPxNode.kDependNode
    NODE_LOCATION   = 'utility/general'

    input  = NumericNodeAttribute(
        'i', 'input', 0, OpenMaya.MFnNumericData.kInt, affects='output')
    output = NumericNodeAttribute(
        'o', 'output', 0, OpenMaya.MFnNumericData.kInt, compute='outputCompute')
    tracks = MessageNodeAttribute('ts', 'trackSet')

#_______________________________________________________________________________
    def __init__(self):
        """Creates a new instance of TrackManagerNode."""
        ElixirNode.__init__(self)

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    # noinspection PyMethodMayBeStatic
    def outputCompute(self, data):
        value = data.inHandles.input.asInt()
        data.outHandles.output.setInt(2*value)
        data.outHandles.cleanAll()


