# ShadingUtils..py
# (C)2013
# Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division

from nimble import cmds

from cadence.util.maya.MayaUtils import MayaUtils

#___________________________________________________________________________________________________ ShadingUtils.
class ShadingUtils(object):
    """A utility class for loading and manipulating shaders, to provide material properties."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ applyShader
    @classmethod
    def applyShader(cls, shaderConfig, transforms):
        shader, shaderEngine = cls.createShaderFromConfig(shaderConfig)

        priorSelection = MayaUtils.getSelectedTransforms()
        MayaUtils.setSelection(transforms)
        cmds.sets(forceElement=shaderEngine)
        MayaUtils.setSelection(priorSelection)

#___________________________________________________________________________________________________ createShaderFromConfig
    @classmethod
    def createShaderFromConfig(cls, shaderConfig):
        """create a shader and engine if not already available"""

        if not cls.shaderExistsInScene(shaderConfig):
            shader = cmds.shadingNode(
                shaderConfig['type'],
                name=shaderConfig['uid'],
                asShader=True)
            cmds.setAttr(shader + '.color', *shaderConfig['color'], type='double3')
            if 'transparency' in shaderConfig:
                cmds.setAttr(
                    shader + '.transparency',
                    *shaderConfig['transparency'], type='double3')

            shaderEngine = cmds.sets(
                renderable=True,
                noSurfaceShader=True,
                empty=True,
                name=shader + '_SG')
            cmds.connectAttr(shader + '.outColor', shaderEngine + '.surfaceShader')
        else:
            shader  = shaderConfig['uid']
            engines = cmds.listConnections(shader + '.outColor')
            if engines:
                shaderEngine = engines[0]
            else:
                shaderEngine = cmds.sets(
                    renderable=True,
                    noSurfaceShader=True,
                    empty=True,
                    name=shader + '_SG')
                cmds.connectAttr(shader + '.outColor', shaderEngine + '.surfaceShader')

        return shader, shaderEngine

#___________________________________________________________________________________________________ shaderExistsInScene
    @classmethod
    def shaderExistsInScene(cls, shaderConfig):
       return cmds.objExists(shaderConfig['uid'])

#___________________________________________________________________________________________________ getAllShaded
    @classmethod
    def getAllShaded(cls, shaderConfig):
        """ Returns the list of transform nodes that have a geometry nodeName shaded by the
            specified shader configuration data. """

        engine = cls.createShaderFromConfig(shaderConfig)[1]
        geos   = cmds.ls(geometry=True)
        out    = []

        for geo in geos:
            if engine in cmds.listSets(type=1, object=geo):
                transforms = cmds.listRelatives([geo], allParents=True, type='transform')
                out       += transforms

        return out




