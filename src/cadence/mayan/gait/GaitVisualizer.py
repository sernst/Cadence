# GaitVisualizer.py
# (C)2012 http://cadence.threeaddone.com
# Scott Ernst

from cadence.config.enum.GaitConfigEnum import GaitConfigEnum
from cadence.config.enum.GeneralConfigEnum import GeneralConfigEnum
from cadence.config.enum.SkeletonConfigEnum import SkeletonConfigEnum
from cadence.shared.enum.ChannelsEnum import ChannelsEnum
from cadence.shared.enum.TargetsEnum import TargetsEnum
from cadence.shared.io.CadenceData import CadenceData
from cadence.util.ArgsUtils import ArgsUtils
from nimble import cmds

#___________________________________________________________________________________________________ GaitVisualizer
class GaitVisualizer(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, *args, **kwargs):
        """Creates a new instance of GaitVisualizer."""

        self._data = CadenceData()

        self._filename = ArgsUtils.get('filename', None, kwargs)
        if self._filename:
            self._data.loadFile(self._filename)
        else:
            data = ArgsUtils.get('data', None, kwargs)
            if isinstance(data, CadenceData):
                self._data = data
            elif data:
                self._data.load(data)
            else:
                self._data = None

        self._group     = None
        self._leftHind  = None
        self._rightHind = None
        self._leftFore  = None
        self._rightFore = None
        self._hips      = None
        self._pecs      = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: filename
    @property
    def filename(self):
        return self._filename

#___________________________________________________________________________________________________ GS: data
    @property
    def data(self):
        return self._data

#___________________________________________________________________________________________________ GS: group
    @property
    def group(self):
        return self._group

#___________________________________________________________________________________________________ GS: leftHind
    @property
    def leftHind(self):
        return self._leftHind if not self.group else (self.group + u'|' + self._leftHind)

#___________________________________________________________________________________________________ GS: rightHind
    @property
    def rightHind(self):
        return self._rightHind if not self.group else (self.group + u'|' + self._rightHind)

#___________________________________________________________________________________________________ GS: leftFore
    @property
    def leftFore(self):
        return self._leftFore if not self.group else (self.group + u'|' + self._leftFore)

#___________________________________________________________________________________________________ GS: rightFore
    @property
    def rightFore(self):
        return self._rightFore if not self.group else (self.group + u'|' + self._rightFore)

#___________________________________________________________________________________________________ GS: hips
    @property
    def hips(self):
        return self._hips if not self.group else (self.group + u'|' + self._hips)

#___________________________________________________________________________________________________ GS: pecs
    @property
    def pecs(self):
        return self._pecs if not self.group else (self.group + u'|' + self._pecs)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ buildScene
    def buildScene(self):
        """Doc..."""

        groupItems = []
        hinds      = []
        fores      = []

        for c in self._data.getChannelsByKind(ChannelsEnum.POSITION):
            isHind = c.target in [TargetsEnum.LEFT_HIND, TargetsEnum.RIGHT_HIND]
            radius = 20 if isHind else 15
            res    = cmds.polySphere(radius=radius, name=c.target)
            groupItems.append(res[0])
            if isHind:
                hinds.append(res[0])
            else:
                fores.append(res[0])

            if c.target == TargetsEnum.LEFT_HIND:
                self._leftHind = res[0]
            elif c.target == TargetsEnum.RIGHT_HIND:
                self._rightHind = res[0]
            elif c.target == TargetsEnum.RIGHT_FORE:
                self._rightFore = res[0]
            elif c.target == TargetsEnum.LEFT_FORE:
                self._leftFore = res[0]

            for k in c.keys:
                frames = [
                    ['translateX', k.value.x, k.inTangentMaya[0], k.outTangentMaya[0]],
                    ['translateY', k.value.y, k.inTangentMaya[1], k.outTangentMaya[1]],
                    ['translateZ', k.value.z, k.inTangentMaya[2], k.outTangentMaya[2]]
                ]
                for f in frames:
                    cmds.setKeyframe(
                        res[0],
                        attribute=f[0],
                        time=k.time,
                        value=f[1],
                        inTangentType=f[2],
                        outTangentType=f[3]
                    )

                if k.event == 'land':
                    printResult = cmds.polyCylinder(
                        name=c.target + '_print1',
                        radius=radius,
                        height=(1.0 if isHind else 5.0)
                    )
                    cmds.move(k.value.x, k.value.y, k.value.z, printResult[0])
                    groupItems.append(printResult[0])

        cfg = self._data.configs
        name = 'cyc' + str(int(cfg.get(GaitConfigEnum.CYCLES))) + \
               '_ph' + str(int(cfg.get(GaitConfigEnum.PHASE))) + \
               '_gad' + str(int(cfg.get(SkeletonConfigEnum.FORE_OFFSET).z)) + \
               '_step' + str(int(cfg.get(SkeletonConfigEnum.STRIDE_LENGTH)))

        cube        = cmds.polyCube(name='pelvic_reference', width=20, height=20, depth=20)
        self._hips  = cube[0]
        groupItems.append(cube[0])
        cmds.move(0, 100, 0, cube[0])

        backLength = self._data.configs.get(SkeletonConfigEnum.FORE_OFFSET).z - \
                     self._data.configs.get(SkeletonConfigEnum.HIND_OFFSET).z

        cube2 = cmds.polyCube(name='pectoral_comparator', width=15, height=15, depth=15)
        cmds.move(0, 115, backLength, cube2[0])
        cmds.parent(cube2[0], cube[0], absolute=True)

        cmds.expression(
            string="%s.translateZ = 0.5*abs(%s.translateZ - %s.translateZ) + min(%s.translateZ, %s.translateZ)" %
            (cube[0], hinds[0], hinds[1], hinds[0], hinds[1])
        )

        cube = cmds.polyCube(name='pectoral_reference', width=15, height=15, depth=15)
        self._pecs = cube[0]
        groupItems.append(cube[0])
        cmds.move(0, 100, 0, cube[0])
        cmds.expression(
            string="%s.translateZ = 0.5*abs(%s.translateZ - %s.translateZ) + min(%s.translateZ, %s.translateZ)" %
            (cube[0], fores[0], fores[1], fores[0], fores[1])
        )

        self._group = cmds.group(*groupItems, world=True, name=name)

        cfg = self._data.configs
        info = 'Gait Phase: ' + \
                str(cfg.get(GaitConfigEnum.PHASE)) + \
                '\nGleno-Acetabular Distance (GAD): ' + \
                str(cfg.get(SkeletonConfigEnum.FORE_OFFSET).z) + \
                '\nStep Length: ' + \
                str(cfg.get(SkeletonConfigEnum.STRIDE_LENGTH)) + \
                '\nHind Duty Factor: ' + \
                str(cfg.get(GaitConfigEnum.DUTY_FACTOR_HIND)) + \
                '\nFore Duty Factor: ' + \
                str(cfg.get(GaitConfigEnum.DUTY_FACTOR_FORE)) + \
                '\nCycles: ' + \
                str(cfg.get(GaitConfigEnum.CYCLES))

        cmds.select(self._group)
        if not cmds.attributeQuery('notes', node=self._group, exists=True):
            cmds.addAttr(longName='notes', dataType='string')
            cmds.setAttr(self._group + '.notes', info, type='string')

        self.createShaders()
        self.createRenderEnvironment()

        minTime = min(0, int(cmds.playbackOptions(query=True, minTime=True)))

        deltaTime = cfg.get(GeneralConfigEnum.STOP_TIME) - cfg.get(GeneralConfigEnum.START_TIME)
        maxTime = max(
            int(float(cfg.get(GaitConfigEnum.CYCLES))*float(deltaTime)),
            int(cmds.playbackOptions(query=True, maxTime=True))
        )

        cmds.playbackOptions(
            minTime=minTime, animationStartTime=minTime, maxTime= maxTime, animationEndTime=maxTime
        )

        cmds.currentTime(0, update=True)

        cmds.select(self._group)

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ createShaders
    def createShaders(self):
        shader, shaderEngine = self.createShader('HindPrint_Blinn')
        cmds.setAttr(shader + '.color', 0.618, 0.551421, 0.368328, type='double3')
        cmds.select(
            cmds.ls(self.group + '|left_hind_*', objectsOnly=True, exactType='transform', long=True)
        )
        cmds.sets(forceElement=shaderEngine)

        cmds.select(
            cmds.ls(self.group + '|right_hind_*', objectsOnly=True, exactType='transform', long=True)
        )
        cmds.sets(forceElement=shaderEngine)

        shader, shaderEngine = self.createShader('ForePrint_Blinn')
        cmds.setAttr(shader + '.color', 0.309, 0.8618, 1.0, type='double3')
        cmds.select(
            cmds.ls(self.group + '|left_fore_*', objectsOnly=True, exactType='transform', long=True)
        )
        cmds.sets(forceElement=shaderEngine)

        cmds.select(
            cmds.ls(self.group + '|right_fore_*', objectsOnly=True, exactType='transform', long=True)
        )
        cmds.sets(forceElement=shaderEngine)

        shader, shaderEngine = self.createShader('HindFoot_Blinn')
        cmds.setAttr(shader + '.color', 0.792, 0.383566, 0.338184, type='double3')
        cmds.select([self.leftHind, self.rightHind])
        cmds.sets(forceElement=shaderEngine)

        shader, shaderEngine = self.createShader('ForeFoot_Blinn')
        cmds.setAttr(shader + '.color', 0.287, 0.762333, 1.0, type='double3')
        cmds.select([self.leftFore, self.rightFore])
        cmds.sets(forceElement=shaderEngine)

        shader, shaderEngine = self.createShader('Hips_Blinn')
        cmds.setAttr(shader + '.color', 1.0, 0.376, 0.376, type='double3')
        cmds.select([self.hips])
        cmds.sets(forceElement=shaderEngine)

        shader, shaderEngine = self.createShader('Pecs_Blinn')
        cmds.setAttr(shader + '.color', 0.629483, 1.0, 0.483, type='double3')
        cmds.select([self.pecs])
        cmds.sets(forceElement=shaderEngine)

#___________________________________________________________________________________________________ createShader
    def createShader(self, shaderName, shaderType ='blinn'):
        shaderEngine = None
        if not cmds.objExists(shaderName):
            shader       = cmds.shadingNode(shaderType, asShader=True)
            shader       = cmds.rename(shader, shaderName)
            shaderEngine = cmds.sets(renderable=True, empty=True, noSurfaceShader=True, name=shader + '_SG')
            cmds.connectAttr(shader + '.outColor', shaderEngine + '.surfaceShader')
        else:
            shader  = shaderName
            engines = cmds.listConnections(shader + '.outColor')
            if engines:
                shaderEngine = engines[0]

        return shader, shaderEngine

    def createRenderEnvironment(self):
        lightName = 'scenic_light1'
        if not cmds.objExists(lightName):
            lightName = cmds.directionalLight(name=lightName, intensity=0.5)
            cmds.move(0, 2500, 0, lightName)
            cmds.rotate('-45deg', '-45deg', 0, lightName)

        lightName = 'scenic_light2'
        if not cmds.objExists(lightName):
            lightName = cmds.directionalLight(name=lightName, intensity=0.5)
            cmds.move(0, 2500, 0, lightName)
            cmds.rotate('-45deg', '135deg', 0, lightName)

        floorName = 'floor'
        if not cmds.objExists(floorName):
            floorName = cmds.polyPlane(width=10000, height=10000, name=floorName)[0]
        shader, shaderEngine = self.createShader('Whiteout_Surface', 'surfaceShader')
        cmds.setAttr(shader + '.outColor', 1.0, 1.0, 1.0, type='double3')
        cmds.select([floorName])
        cmds.sets(forceElement=shaderEngine)

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
