
from __future__ import print_function, absolute_import, unicode_literals, division

from maya import cmds

def createTrackwayVisualization(trackway):

    references = []

    for foot in trackway:
        references.extend(createMarchingSphere(foot))

    references.append(createHipsIndicator(trackway))
    references.append(createShoulderIndicator(trackway))

    group = cmds.group(*references, world=True, name=name)
    cmds.select(group)

    applyShaders(trackway)
    createRenderEnvironment()

    minTime = min(0, int(cmds.playbackOptions(query=True, minTime=True)))
    maxTime = trackway.duration

    cmds.playbackOptions(
        minTime=minTime, animationStartTime=minTime,
        maxTime= maxTime, animationEndTime=maxTime)

    cmds.currentTime(0, update=True)
    cmds.select(group)

def createMarchingSphere(foot):
    sphereName, sphereShape = cmds.polySphere(radius=foot.radius, name=foot.name)
    reference = [sphereName]

    for keyFrame in foot.keys:
        for keyable in keyFrame.attributes:
            cmds.setKeyframe(
                sphereName,
                attribute=keyable.name,
                time=keyFrame.time,
                value=keyable.value)

        if keyFrame.isLandEvent:
            trackName, trackShape = cmds.polyCylinder(
                name=foot.label + '_print_1', # Maya numbers automatically
                radius=foot.radius,
                height=1.0 if foot.isPes else 5.0)

            cmds.move(keyFrame.value.x, keyFrame.value.y, keyFrame.value.z, trackName)
            reference.append(trackName)

    return reference

def createHipsIndicator(trackway):
    hips, shape = cmds.polyCube(name='hips', width=20, height=20, depth=20)
    cmds.move(0, 100, 0, hips)
    references.append(hips)

    shoulders, shape = cmds.polyCube(name='shoulders_locked', width=15, height=15, depth=15)
    cmds.move(0, 115, trackway.spineLength, shoulders)
    cmds.parent(shoulders, hips, absolute=True)

    pes = trackway.pes
    cmds.expression("%s.z = 0.5*abs(%s.z - %s.z) + min(%s.z, %s.z)" % (
        hips, pes.left, pes.right, pes.left, pes.right))

    return hips

def createShoulderIndicator(trackway):
    shoulders, shape = cmds.polyCube(name='shoulders', width=15, height=15, depth=15)
    groupItems.append(shoulders)
    cmds.move(0, 100, 0, shoulders)

    manus = trackway.manus
    cmds.expression("%s.z = 0.5*abs(%s.z - %s.z) + min(%s.z, %s.z)" % (
        shoulders, manus.left, manus.right, manus.left, manus.right))

    return shoulders

def createShader(name, shaderType, color):
    shader = cmds.shadingNode(shaderType, asShader=True, name=name)
    cmds.setAttr(shader + '.color', color[0], color[1], color[2], type='double3')
    shaderEngine = cmds.sets(renderable=True, empty=True, noSurfaceShader=True)
    return shader, shaderEngine

def applyShaders(trackway):
    shader, shaderEngine = createShader('Pes_Shader', 'blinn', (0.79, 0.38, 0.34))
    cmds.select(trackway.pes.left.name, trackway.pes.right.name)
    cmds.sets(forceElement=shaderEngine)

def createRenderEnvironment():
    lightName = cmds.directionalLight(name='scenic_light1', intensity=0.5)
    cmds.move(0, 2500, 0, lightName)
    cmds.rotate('-45deg', '-45deg', 0, lightName)

    lightName = cmds.directionalLight(name='scenic_light2', intensity=0.5)
    cmds.move(0, 2500, 0, lightName)
    cmds.rotate('-45deg', '135deg', 0, lightName)

    floorName, shape = cmds.polyPlane(width=10000, height=10000, name='floor')
    shader, shaderEngine = createShader('Floor_Surface', 'surfaceShader', (1.0, 1.0, 1.0))
    cmds.select(floorName)
    cmds.sets(forceElement=shaderEngine)

