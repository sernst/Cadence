# ShaderMixer.py
# (C)2013
# Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.string.StringUtils import StringUtils

from cadence.util.shading.ShadingUtils import ShadingUtils

#___________________________________________________________________________________________________ ShaderMixer
class ShaderMixer(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, shaderConfig):
        """Creates a new instance of ShaderMixer."""
        self._shaderConfig = shaderConfig

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: uid
    @property
    def uid(self):
        return self._shaderConfig['uid']

#___________________________________________________________________________________________________ GS: materialType
    @property
    def materialType(self):
        return self._shaderConfig['type']

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ create
    def create(self):
         ShadingUtils.createShaderFromConfig(self._shaderConfig)

#___________________________________________________________________________________________________ shade
    def shade(self, transforms):
        ShadingUtils.applyShader(self._shaderConfig, transforms)

#___________________________________________________________________________________________________ getShaded
    def getShaded(self):
        return ShadingUtils.getAllShaded(self._shaderConfig)

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __repr__
    def __repr__(self):
        return self.__str__()

#___________________________________________________________________________________________________ __unicode__
    def __unicode__(self):
        return StringUtils.toUnicode(self.__str__())

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        return '<%s>' % self.__class__.__name__
