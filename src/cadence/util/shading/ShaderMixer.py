# ShaderMixer.py
# (C)2013
# Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division
from pyaid.string.StringUtils import StringUtils

from cadence.util.shading.ShadingUtils import ShadingUtils

#_______________________________________________________________________________
class ShaderMixer(object):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

#_______________________________________________________________________________
    def __init__(self, shaderConfig):
        """Creates a new instance of ShaderMixer."""
        self._shaderConfig = shaderConfig

#===============================================================================
#                                                                                   G E T / S E T

#_______________________________________________________________________________
    @property
    def uid(self):
        return self._shaderConfig['uid']

#_______________________________________________________________________________
    @property
    def materialType(self):
        return self._shaderConfig['type']

#===============================================================================
#                                                                                     P U B L I C

#_______________________________________________________________________________
    def create(self):
         ShadingUtils.createShaderFromConfig(self._shaderConfig)

#_______________________________________________________________________________
    def shade(self, transforms):
        ShadingUtils.applyShader(self._shaderConfig, transforms)

#_______________________________________________________________________________
    def getShaded(self):
        return ShadingUtils.getAllShaded(self._shaderConfig)

#===============================================================================
#                                                                               I N T R I N S I C

#_______________________________________________________________________________
    def __repr__(self):
        return self.__str__()

#_______________________________________________________________________________
    def __unicode__(self):
        return StringUtils.toUnicode(self.__str__())

#_______________________________________________________________________________
    def __str__(self):
        return '<%s>' % self.__class__.__name__
