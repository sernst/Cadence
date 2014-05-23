# TrackSceneUtils.py
# (C)2014
# Scott Ernst

import math

from nimble import cmds

from pyaid.reflection.Reflection import Reflection

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enum.TrackPropEnum import TrackPropEnum

#___________________________________________________________________________________________________ TrackSceneUtils
class TrackSceneUtils(object):
    """ A class for supporting Maya-side operations such as creating visual representations of Track
        nodes (createTrackNode), and getting and setting those values.  Used by remote scripts that
        extend NimbleScriptBase. """

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ createTrackNode
    @classmethod
    def createTrackNode(cls, uid, trackSetNode =None, props =None):
        """ The node consists of a (polyCylinder) center marker (only allowing rotateY, translateX,
            and translateZ).  It has a (polyCube) ruler child, 1 cm on a side, so that its
            scale directly relates to measured length (in centimeters).  The ruler cannot
            be scaled in Maya (only through the UI); it can be translated in Z to offset it relative
            to the center marker.  There are also two additional length bars that can rotate about
            the pivot to represent thetaMin (clockwise) and thetaMax (counterclockwise) estimates
            of rotation uncertainty. The offset of the ruler is represented as pointerSideLength
            lengthRatio, and defaults to 0.5 (half-way along the longitudinal axis of the track).
            Initially, the length derives from the measured value in the catalog (which, if 0.0,
            signifies that the length was indeterminate, such as when the track perimeter is
            incomplete).  Uncertainty in length is represented by two elongate polyCubes, one placed
            at each end of the ruler, with their scaleZ values adjusted to represent uncertainty
            in cm.  These markers are labeled padN and padS, and modified only in the UI.  As
            with the length attribute, the width is initially displayed according to the measured
            value in the catalog, and corresponds to the separation between two small unit polyCubes
            (padW and padE).  Length and width can only be adjusted in the UI.  Likwise the
            uncertainties in width and length are only adjusted in the UI. """

        if not trackSetNode:
            trackSetNode = TrackSceneUtils.getTrackSetNode()
        if not trackSetNode:
            return None

        node = cls.getTrackNode(uid, trackSetNode=trackSetNode)
        if node:
            return node

        cylinderRadius    = 10.0
        cylinderThickness = 1.0
        pointerThickness  = 0.5
        padBreadth        = 10.0
        padThickness      = 0.25
        rulerBreadth      = 1.0
        rulerThickness    = 0.25
        epsilon           = 0.25

        node = cmds.polyCylinder(
            radius=cylinderRadius,
            height=cylinderThickness,
            subdivisionsX=20,
            subdivisionsY=1,
            subdivisionsZ=1,
            axis=(0,1,0),
            createUVs=2,
            constructionHistory=1,
            name='Track0')[0]
        cmds.move(0.0, -(pointerThickness + cylinderThickness/2.0), 0.0)

        cmds.addAttr(
             longName='cadence_width',
             shortName=TrackPropEnum.WIDTH.maya,
             niceName='Width')
        cmds.addAttr(
             longName='cadence_widthUncertainty',
             shortName=TrackPropEnum.WIDTH_UNCERTAINTY.maya,
             niceName='Width Uncertainty')
        cmds.addAttr(
             longName='cadence_length',
             shortName=TrackPropEnum.LENGTH.maya,
             niceName='Length')
        cmds.addAttr(
             longName='cadence_lengthUncertainty',
             shortName=TrackPropEnum.LENGTH_UNCERTAINTY.maya,
             niceName='Length Uncertainty')
        cmds.addAttr(
             longName='cadence_lengthRatio',
             shortName=TrackPropEnum.LENGTH_RATIO.maya,
             niceName='Length Ratio')
        cmds.addAttr(
             longName='cadence_uniqueId',
             shortName=TrackPropEnum.UID.maya,
             dataType='string',
             niceName='Unique ID')

        pointerSideLength = 2.0*cylinderRadius
        pointer = cmds.polyPrism(
             length=pointerThickness,
             sideLength=pointerSideLength,
             numberOfSides=3,
             subdivisionsHeight=1,
             subdivisionsCaps=0,
             axis=(0,1,0),
             createUVs=3,
             constructionHistory=1,
             name='Pointer')[0]

        cmds.rotate(0.0, -90.0, 0.0)
        cmds.move(0, -pointerThickness/2.0, pointerSideLength/(2.0*math.sqrt(3.0)))
        cmds.move(0, 0, 0, pointer + ".scalePivot", pointer + ".rotatePivot", absolute=True)
        cmds.makeIdentity(
             apply=True,
             translate=True,
             rotate=True,
             scale=True,
             normal=False)
        cmds.scale(1.0, 1.0, 1.0/math.sqrt(3.0))
        cmds.setAttr(pointer + '.overrideEnabled', 1)
        cmds.setAttr(pointer + '.overrideDisplayType', 2)
        cmds.parent(pointer, node)

        padN = cmds.polyCube(
            axis=(0,1,0),
            width=padBreadth,
            height=padThickness,
            depth=100.0,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=3,
            constructionHistory=1,
            name='PadN')[0]
        cmds.move(0.0, -padThickness/2.0, 0.0)

        padS = cmds.polyCube(
            axis=(0,1,0),
            width=padBreadth,
            height=padThickness,
            depth=100.0,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=3,
            constructionHistory=1,
            name='PadS')[0]
        cmds.move(0.0, -padThickness/2.0, 0.0)

        padW = cmds.polyCube(
            axis=(0,1,0),
            width=100.0,
            height=padThickness,
            depth=padBreadth,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=3,
            constructionHistory=1,
            name='PadW')[0]
        cmds.move(0.0, -padThickness/2.0, 0.0)

        padE = cmds.polyCube(
            axis=(0,1,0),
            width=100.0,
            height=padThickness,
            depth=padBreadth,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=3,
            constructionHistory=1,
            name='PadE')[0]
        cmds.move(0.0, -padThickness/2.0, 0.0)

        ruler = cmds.polyCube(
            axis=(0,1,0),
            width=rulerBreadth,
            height=rulerThickness,
            depth=100.0,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=3,
            constructionHistory=1,
            name='Ruler')[0]
        cmds.move(0.0, -(padThickness + rulerThickness/2.0), 0.0)

        cmds.setAttr(ruler + '.overrideEnabled', 1)
        cmds.setAttr(ruler + '.overrideDisplayType', 2)
        cmds.setAttr(padN  + '.overrideEnabled', 1)
        cmds.setAttr(padN  + '.overrideDisplayType', 2)
        cmds.setAttr(padS  + '.overrideEnabled', 1)
        cmds.setAttr(padS  + '.overrideDisplayType', 2)
        cmds.setAttr(padW  + '.overrideEnabled', 1)
        cmds.setAttr(padW  + '.overrideDisplayType', 2)
        cmds.setAttr(padE  + '.overrideEnabled', 1)
        cmds.setAttr(padE  + '.overrideDisplayType', 2)

        cmds.setAttr(node + '.rotateX',    lock=True)
        cmds.setAttr(node + '.rotateZ',    lock=True)
        cmds.setAttr(node + '.scaleX',     lock=True)
        cmds.setAttr(node + '.scaleY',     lock=True)
        cmds.setAttr(node + '.scaleZ',     lock=True)
        cmds.setAttr(node + '.translateY', lock=True)

        # scale markers to display the width and length uncertainties
        cmds.connectAttr(node + "." + TrackPropEnum.WIDTH_UNCERTAINTY.maya,  padW + '.scaleX')
        cmds.connectAttr(node + "." + TrackPropEnum.WIDTH_UNCERTAINTY.maya,  padE + '.scaleX')
        cmds.connectAttr(node + "." + TrackPropEnum.LENGTH_UNCERTAINTY.maya, padN + '.scaleZ')
        cmds.connectAttr(node + "." + TrackPropEnum.LENGTH_UNCERTAINTY.maya, padS + '.scaleZ')

        # convert the node.width attribute in meters (as it comes from the database) to centimeters
        width = cmds.createNode('multiplyDivide', name='width')
        cmds.setAttr(width + '.operation', 1)
        cmds.setAttr(width + '.input1X', 100.0)
        cmds.connectAttr(node + '.' + TrackPropEnum.WIDTH.maya, width + '.input2X')

        # convert the node.length attribute in meters (as it comes from the database) to centimeters
        length = cmds.createNode('multiplyDivide', name='length')
        cmds.setAttr(length + '.operation', 1)
        cmds.setAttr(length + '.input1X', 100.0)
        cmds.connectAttr(node + '.' + TrackPropEnum.LENGTH.maya, length + '.input2X')

        # compute the half length hl = length/2.0) (now in centimeters)
        hl = cmds.createNode('multiplyDivide', name='hl')
        cmds.setAttr(hl + '.operation', 2)
        cmds.connectAttr(length + '.outputX', hl + '.input1X')
        cmds.setAttr(hl + '.input2X', 2.0)

        # translate padN in z by zN = lengthRatio*length (in centimeters)
        zN = cmds.createNode('multiplyDivide', name='zN')
        cmds.setAttr(zN + '.operation', 1)
        cmds.connectAttr(node + '.' + TrackPropEnum.LENGTH_RATIO.maya, zN + '.input1X')
        cmds.connectAttr(length + '.outputX',  zN + '.input2X')
        cmds.connectAttr(zN + '.outputX', padN + '.translateZ')

        # translate the ruler in z by zL = (zN - hl) (both in centimeters)
        zL = cmds.createNode('plusMinusAverage', name='zL')
        cmds.setAttr(zL + '.operation', 2)
        cmds.connectAttr(zN + '.outputX',  zL + '.input1D[0]')
        cmds.connectAttr(hl + '.outputX',  zL + '.input1D[1]')
        cmds.connectAttr(zL + '.output1D', ruler + '.translateZ')

        # scale the ruler (which is 100 cm long) by the length attribute (which is in meters)
        cmds.connectAttr(node + '.length', ruler + '.scaleZ')

        # translate padS in z by (zN - length); output is in zS.output1D
        zS = cmds.createNode('plusMinusAverage', name='sZ')
        cmds.setAttr(zS + '.operation', 2)
        cmds.connectAttr(zN + '.outputX',     zS + '.input1D[0]')
        cmds.connectAttr(length + '.outputX', zS + '.input1D[1]')
        cmds.connectAttr(zS + '.output1D',    padS + '.translateZ')

        # offset padW in x by width/2.0; output is in xW.outputX
        xW = cmds.createNode('multiplyDivide', name = 'xW')
        cmds.setAttr(xW + '.operation', 2)
        cmds.connectAttr(width + '.outputX', xW + '.input1X')
        cmds.setAttr(xW + '.input2X', 2.0)
        cmds.connectAttr(xW + '.outputX', padW + '.translateX')

        # offset padE in x by -width/2.0; output is in xE.outputX
        xE = cmds.createNode('multiplyDivide', name = 'xE')
        cmds.setAttr(xE + '.operation', 2) # division operation
        cmds.connectAttr(width + '.outputX', xE + '.input1X')
        cmds.setAttr(xE + '.input2X', -2.0)
        cmds.connectAttr(xE + '.outputX', padE + '.translateX')

        cmds.parent(ruler, node)
        cmds.parent(padN,   node)
        cmds.parent(padS,   node)
        cmds.parent(padW,   node)
        cmds.parent(padE,   node)

        cmds.select(node)
        cmds.move(0, -epsilon, 0)

        if props:
            cls.setTrackProps(node, props)
        else:
            print 'Trying to create pointerSideLength node without props?  But we neeeeds them!'
            return

        # Add the new nodeName to the Cadence track scene set
        cmds.sets(node, add=trackSetNode)

        return node

#___________________________________________________________________________________________________ getTrackNode
    @classmethod
    def getTrackNode(cls, uid, trackSetNode =None):
        trackSetNode = cls.getTrackSetNode() if not trackSetNode else trackSetNode
        if not trackSetNode:
            return None

        nodes = cmds.sets(trackSetNode, query=True)
        if not nodes:
            return None

        for node in nodes:
            if not cmds.hasAttr(node + '.' + TrackPropEnum.UID.maya):
                continue
            if uid == cmds.getAttr(node + '.' + TrackPropEnum.UID.maya):
                return node

        return None

#___________________________________________________________________________________________________ getUid
    @classmethod
    def getUid(cls, node):
        """ This returns the UID (or None if the nodeName is not a track nodeName). """
        trackSetNode = cls.getTrackSetNode()
        if not trackSetNode:
            return None
        if not cmds.sets(node, isMember=trackSetNode):
            return None
        try:
            return cmds.getAttr(node + '.' + TrackPropEnum.UID.maya)
        except Exception, err:
            return None

#___________________________________________________________________________________________________ checkNodeUidMatch
    @classmethod
    def checkNodeUidMatch(cls, uid, node):
        try:
            return uid == cls.getUid(node)
        except Exception, err:
            return False

#___________________________________________________________________________________________________ getTrackProps
    @classmethod
    def getTrackProps(cls, node):
        out = dict()
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.maya is None:
                continue
            out[enum.name] = cmds.getAttr(node + '.' + enum.maya)
        return out

#___________________________________________________________________________________________________ setTrackProps
    @classmethod
    def setTrackProps(cls, node, props):
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.maya and enum.maya in props:
                if enum.type == 'string':
                    cmds.setAttr(node + '.' + enum.maya, props[enum.maya], type=enum.type)
                else:
                    cmds.setAttr(node + '.' + enum.maya, props[enum.maya])

#___________________________________________________________________________________________________ getTrackManagerNode
    @classmethod
    def getTrackManagerNode(cls, trackSetNode =None, createIfMissing =False):
        """ Returns the name of the track manager nodeName for the current Cadence scene.

            trackSetNode: The track set nodeName on which to find the track manager nodeName.
                    If no nodeName is specified the method will look it up internally.

            createIfMissing: If true and no track manager nodeName is found one will be created and
                    connected to the track set nodeName, which will also be created if one does
                    not exist. """

        if not trackSetNode:
            trackSetNode = cls.getTrackSetNode(createIfMissing=createIfMissing)

        connects = cmds.listConnections(trackSetNode + '.usedBy', source=True, destination=False)
        if connects:
            for node in connects:
                if cmds.nodeType(node) == 'trackManager':
                    return node

        if createIfMissing:
            node = cmds.createNode('trackManager')
            cmds.connectAttr(node + '.trackSet', trackSetNode + '.usedBy', force=True)
            return node

        return None

#___________________________________________________________________________________________________ getTrackSetNode
    @classmethod
    def getTrackSetNode(cls, createIfMissing =False):
        for node in cmds.ls(exactType='objectSet'):
            if node == CadenceEnvironment.TRACKWAY_SET_NODE_NAME:
                return node

        if createIfMissing:
            return cmds.sets(name=CadenceEnvironment.TRACKWAY_SET_NODE_NAME, empty=True)

        return None
