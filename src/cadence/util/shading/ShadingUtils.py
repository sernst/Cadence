# ShadingUtils..py
# (C)2013
# Kent A. Stevens

from nimble import cmds

from cadence.util.maya.MayaUtils import MayaUtils





#___________________________________________________________________________________________________ ShadingUtils.
class ShadingUtils(object):
    """A utility class for loading and manipulating shaders, to provide material properties."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________
    @classmethod
    def applyShader(cls, shaderConfig, transforms):
        shader, shaderEngine = cls.createShaderFromConfig(shaderConfig)

        priorSelection = MayaUtils.getSelectedTransforms()
        MayaUtils.setSelection(transforms)
        cmds.sets(forceElement=shaderEngine)
        MayaUtils.setSelection(priorSelection)

#___________________________________________________________________________________________________
    @classmethod
    def createShaderFromConfig(cls, shaderConfig):
        """create a shader and engine if not already available"""

        if not cls.shaderExistsInScene(shaderConfig):
            shader = cmds.shadingNode(
                shaderConfig['type'],
                name=shaderConfig['uid'],
                asShader=True)
            shaderEngine = cmds.sets(
                renderable=True,
                noSurfaceShader=True,
                empty=True,
                name=shader + '_SG')
            cmds.connectAttr(shader + '.outColor', shaderEngine + '.surfaceShader')
        else:
            shader = shaderConfig['uid']
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

#___________________________________________________________________________________________________
    @classmethod
    def shaderExistsInScene(cls, shaderConfig):
       return cmds.objExists(shaderConfig['uid'])





