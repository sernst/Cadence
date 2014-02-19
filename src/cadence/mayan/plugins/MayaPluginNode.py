# MayaPluginNode.py
# (C)2014
# Scott Ernst

import sys

from maya import OpenMaya
from maya import OpenMayaMPx

from pyaid.reflection.Reflection import Reflection

from cadence.mayan.plugins.attrs.NodeAttribute import NodeAttribute

#___________________________________________________________________________________________________ MayaPluginNode
class MayaPluginNode(OpenMayaMPx.MPxNode):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    NODE_NAME       = 'unknownNode'
    NODE_ID         = 0
    NODE_TYPE       = OpenMayaMPx.MPxNode.kDependNode
    NODE_LOCATION   = 'utility/general'

    __nodeAttrDefs__ = {}

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        """Creates a new instance of MayaPluginNode."""
        OpenMayaMPx.MPxNode.__init__(self)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ compute
    def compute(self, plug, dataBlock):
        for attrDef in self.__nodeAttrDefs__.itervalues():
            if plug == attrDef.attr:
                if not attrDef.isComputable:
                    break

                try:
                    return attrDef.compute(self, plug, dataBlock)
                except:
                    sys.stderr.write('ERROR: Failed "%s" node computation on %s' % (
                        self.NODE_NAME, attrDef.name))
                    raise

        return self._computeImpl(plug, dataBlock)

#___________________________________________________________________________________________________ register
    @classmethod
    def register(cls, plugin, *args, **kwargs):
        """Doc..."""

        def createNode():
            return OpenMayaMPx.asMPxPtr(cls())

        def initNode():
            return cls._initializeNode()

        try:
            plugin.registerNode(
                cls.NODE_NAME, OpenMaya.MTypeId(cls.NODE_ID), createNode, initNode,
                cls.NODE_TYPE, cls.NODE_LOCATION)
        except:
            sys.stderr.write('ERROR: Unable to register node: ' + cls.NODE_NAME)
            raise

#___________________________________________________________________________________________________ deregister
    @classmethod
    def deregister(cls, plugin):
        try:
            plugin.deregisterNode(OpenMaya.MTypeId(cls.NODE_ID))
        except Exception, err:
            sys.stderr.write('ERROR: Unable to deregister node: ' + cls.NODE_NAME)
            raise

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _initializeNode
    @classmethod
    def _initializeNode(cls):
        attrs = cls.__nodeAttrDefs__
        for name,value in Reflection.getReflectionDict(cls).iteritems():
            if isinstance(value, NodeAttribute):
                # Create the attribute from the definition
                value.initializeAttribute(cls, name)
                attrs[name] = value

                # Add attribute to node
                setattr(cls, name, value.attr)
                cls.addAttribute(getattr(cls, name))

        # Iterate through each attribute created and connect them according to their affects
        for attrDef in attrs.itervalues():
            for target in attrDef.affects:
                cls.attributeAffects(attrDef.attr, getattr(cls, target))

        cls._initializeImpl(attrs)

#___________________________________________________________________________________________________ _initializeImpl
    @classmethod
    def _initializeImpl(cls, attrs):
        pass

#___________________________________________________________________________________________________ _computeImpl
    def _computeImpl(self, plug, dataBlock):
        """Doc..."""
        pass




