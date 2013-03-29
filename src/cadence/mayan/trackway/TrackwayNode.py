# TrackwayNode.py
# (C)2012 http://cadence.ThreeAddOne.com
# Scott Ernst

import sys
import inspect

from maya.api import OpenMaya

#___________________________________________________________________________________________________ TrackwayNode
class TrackwayNode(OpenMaya.MNodeClass):

    NODE_NAME = 'cadenceTrackway'
    NODE_ID   = OpenMaya.MTypeId(0xABC001)

#___________________________________________________________________________________________________ __init__
    def __init__(self):
        OpenMaya.MNodeClass.__init__(self)

#___________________________________________________________________________________________________ initialize
    @classmethod
    def initialize(cls):
        pass

#___________________________________________________________________________________________________ create
    @classmethod
    def create(cls):
        pass

#___________________________________________________________________________________________________ register
    @classmethod
    def register(cls, pluginFn):
        try:
            pluginFn.registerNode(
                cls.getAttrFromClass('NODE_NAME'),
                cls.getAttrFromClass('NODE_ID'),
                cls.create,
                cls.initialize
            )
        except Exception, err:
            sys.stderr.write('Failed to register node: %s\n' % cls.NODE_NAME)
            raise

#___________________________________________________________________________________________________ getAttrFromClass
    @classmethod
    def getAttrFromClass(cls, attr, defaultValue =None):

        # Search through class and its parent classes if necessary to find the attr value
        out = defaultValue
        if hasattr(cls, attr):
            out = getattr(cls, attr, defaultValue)
        else:
            bases = inspect.getmro(cls)
            for b in bases:
                if hasattr(b, attr):
                    out = getattr(b, attr, defaultValue)
                    break

                if isinstance(b, object):
                    break

        return out