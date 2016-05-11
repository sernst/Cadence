# TrackSceneUtils.py
# (C)2014-2016
# Scott Ernst and Kent A. Stevens

from __future__ import\
    print_function, absolute_import, unicode_literals, division

import math

from nimble import cmds
from pyaid.reflection.Reflection import Reflection

from cadence.config import CadenceConfigs
from cadence.enums.TrackPropEnum import TrackPropEnum
from cadence.util.maya.MayaUtils import MayaUtils
from cadence.config.TrackwayShaderConfig import TrackwayShaderConfig
from cadence.util.shading.ShadingUtils import ShadingUtils

#_______________________________________________________________________________
class TrackSceneUtils(object):
    """ A class for supporting Maya-side operations such as creating visual
        representations of Track nodes (createTrackNode), and getting/setting
        those values.  Used by remote scripts that extend NimbleScriptBase.

        While originally designed for track nodes, a simplified token has been
        introduced, and while it uses the uid and trackSetNode, the attributes
        are different. """

#===============================================================================
#                                             T R A C K  N O D E  S U P P O R T
#
#_______________________________________________________________________________
    @classmethod
    def createTrackNode(cls, uid, trackSetNode =None, props =None):
        """ A track node consists of a triangular pointer (left = red, right =
            green) which is selectable but only allows rotateY, translateX, and
            translateZ. The node has a child, a transform called inverter, which
            serves to counteract the scaling in x and z that is applied to the
            triangular node.  There are two orthogonal rulers (width and
            length).  Width and length uncertainty is represented by rectangular
            bars at the ends of the rulers.  In Maya one can directly adjust
            track position (translateX and translateZ) and orientation
            (rotationY); other attributes are adjusted only through the UI. """

        if not trackSetNode:
            trackSetNode = TrackSceneUtils.getTrackSetNode()

        if not trackSetNode:
            return None

        node = cls.getTrackNode(uid, trackSetNode=trackSetNode)
        if node:
            return node

        # Set up dimensional constants for the track node
        nodeThickness  = 1.0
        thetaBreadth   = 0.1
        thetaThickness = 0.5
        barBreadth     = 2.0
        barThickness   = 0.5
        rulerBreadth   = 1.0
        rulerThickness = 0.25
        epsilon        = 1.0

        # Create an isoceles triangle pointer, with base aligned with X, and
        # scaled by node.width.  The midpoint of the base is centered on the
        # 'track center' and the altitude extends from that center of the track
        # 'anteriorly' to the perimeter of the track's profile (if present, else
        # estimated).  The node is scaled longitudinally (in z) based on the
        # distance zN (the 'anterior' length of the track, in cm).  The triangle
        # is initially 1 cm on a side.
        sideLength = 1.0
        node = cmds.polyPrism(
            length=nodeThickness,
            sideLength=sideLength,
            numberOfSides=3,
            subdivisionsHeight=1,
            subdivisionsCaps=0,
            axis=(0, 1, 0),
            createUVs=0,
            constructionHistory=0,
            name='Track0')[0]

        # Point the triangle down the +Z axis
        cmds.rotate(0.0, -90.0, 0.0)

        # push it down below ground level so that the two rulers are just
        # submerged, and scale the triangle in Z to match its width (1 cm) so it
        # is ready to be scaled
        cmds.move(0, -(nodeThickness/2.0 + rulerThickness), math.sqrt(3.0)/6.0)

        # move the node's pivot to the 'base' of the triangle so it scales
        # outward from that point
        cmds.move(
            0, 0, 0, node + ".scalePivot", node + ".rotatePivot", absolute=True)
        cmds.scale(2.0/math.sqrt(3.0), 1.0, 100.0)
        cmds.makeIdentity(
            apply=True,
            translate=True,
            rotate=True,
            scale=True,
            normal=False)

        # Set up the cadence attributes
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
             longName='cadence_rotationUncertainty',
             shortName=TrackPropEnum.ROTATION_UNCERTAINTY.maya,
             niceName='Rotation Uncertainty')
        cmds.addAttr(
             longName='cadence_uniqueId',
             shortName=TrackPropEnum.UID.maya,
             dataType='string',
             niceName='Unique ID')

        # Construct a ruler representing track width, then push it down just
        # below ground level, and ake it non-selectable.  Drive its scale by the
        # node's width attribute.
        widthRuler = cmds.polyCube(
            axis=(0, 1, 0),
            width=100.0,
            height=rulerThickness,
            depth=rulerBreadth,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=0,
            constructionHistory=0,
            name='WidthRuler')[0]

        # Push it down to just rest on the triangular node (which is already
        # submerged by the thickness of the ruler and half the node thickness.
        cmds.move(0.0, -rulerThickness/2.0, 0.0)
        cmds.setAttr(widthRuler + '.overrideEnabled', 1)
        cmds.setAttr(widthRuler + '.overrideDisplayType', 2)

        # Construct a ruler representing track length and push it down the same
        # as the width ruler, and make it non-selectable.  Its length will be
        # driven by the node's length attribute.
        lengthRuler = cmds.polyCube(
            axis=(0, 1, 0),
            width=rulerBreadth,
            height=rulerThickness,
            depth=100.0,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=0,
            constructionHistory=0,
            name='LengthRuler')[0]
        cmds.move(0.0, -rulerThickness/2.0, 0.0)
        cmds.setAttr(lengthRuler + '.overrideEnabled', 1)
        cmds.setAttr(lengthRuler + '.overrideDisplayType', 2)

        # Now construct 'error bars' to the North, South, West, and East of the
        # node, to visualize uncertainty in width (West and East bars) and
        # length (North and South bars), and push them just below ground level,
        # and make them non-selectable.
        barN = cmds.polyCube(
            axis=(0,1,0),
            width=barBreadth,
            height=barThickness,
            depth=100.0,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=0,
            constructionHistory=0,
            name='BarN')[0]
        cmds.move(0, -(barThickness/2 + rulerThickness), 0)
        cmds.setAttr(barN + '.overrideEnabled', 1)
        cmds.setAttr(barN + '.overrideDisplayType', 2)

        barS = cmds.polyCube(
            axis=(0, 1, 0),
            width=barBreadth,
            height=barThickness,
            depth=100.0,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=0,
            constructionHistory=0,
            name='BarS')[0]
        cmds.move(0, -(barThickness/2 + rulerThickness), 0)
        cmds.setAttr(barS + '.overrideEnabled', 1)
        cmds.setAttr(barS + '.overrideDisplayType', 2)

        barW = cmds.polyCube(
            axis=(0, 1, 0),
            width=100.0,
            height=barThickness,
            depth=barBreadth,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=0,
            constructionHistory=0,
            name='BarW')[0]
        cmds.move(0, -(barThickness/2 + rulerThickness), 0)
        cmds.setAttr(barW + '.overrideEnabled', 1)
        cmds.setAttr(barW + '.overrideDisplayType', 2)

        barE = cmds.polyCube(
            axis=(0, 1, 0),
            width=100.0,
            height=barThickness,
            depth=barBreadth,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=0,
            constructionHistory=0,
            name='BarE')[0]
        cmds.move(0, -(barThickness/2 + rulerThickness), 0)
        cmds.setAttr(barE + '.overrideEnabled', 1)
        cmds.setAttr(barE + '.overrideDisplayType', 2)

        # Create two diverging lines that indicate rotation uncertainty (plus
        # and minus), with their pivots placed so they extend from the node
        # center, and each is made non-selectable.  First make the indicator of
        # maximum (counterclockwise) estimated track rotation
        thetaPlus = cmds.polyCube(
            axis=(0, 1, 0),
            width=thetaBreadth,
            height=thetaThickness,
            depth=1.0,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=0,
            constructionHistory=0,
            name='ThetaPlus')[0]
        cmds.setAttr(thetaPlus + '.overrideEnabled',     1)
        cmds.setAttr(thetaPlus + '.overrideDisplayType', 2)

        # Next, construct the indicator of the minimum (clockwise) estimate of
        # track rotation
        thetaMinus = cmds.polyCube(
            axis=(0, 1, 0),
            width=thetaBreadth,
            height=thetaThickness,
            depth=1.0,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=0,
            constructionHistory=0,
            name='ThetaMinus')[0]
        cmds.setAttr(thetaMinus + '.overrideEnabled',     1)
        cmds.setAttr(thetaMinus + '.overrideDisplayType', 2)

        # The two width 'error bars' will be translated outward from the node
        # center.  First, the width attribute is converted from meters (as it
        # comes from the database) to centimeters; the computation is available
        # in the output of the node 'width'.
        width = cmds.createNode('multiplyDivide', name='width')
        cmds.setAttr(width + '.operation', 1)
        cmds.setAttr(width + '.input1X', 100.0)
        cmds.connectAttr(
            node + '.' + TrackPropEnum.WIDTH.maya, width + '.input2X')

        # Translate barW in x by width/2.0; output is in xW.outputX
        xW = cmds.createNode('multiplyDivide', name = 'xW')
        cmds.setAttr(xW + '.operation', 2)
        cmds.connectAttr(width + '.outputX', xW + '.input1X')
        cmds.setAttr(xW + '.input2X', 2.0)
        cmds.connectAttr(xW + '.outputX', barW + '.translateX')

        # Translate barE in x by -width/2.0; output is in xE.outputX
        xE = cmds.createNode('multiplyDivide', name = 'xE')
        cmds.setAttr(xE + '.operation', 2) # division operation
        cmds.connectAttr(width + '.outputX', xE + '.input1X')
        cmds.setAttr(xE + '.input2X', -2.0)
        cmds.connectAttr(xE + '.outputX', barE + '.translateX')

        # Now regarding length, first convert the node.length attribute from
        # meters to centimeters. This computation is available in the output of
        # the node 'length'
        length = cmds.createNode('multiplyDivide', name='length')
        cmds.setAttr(length + '.operation', 1)
        cmds.setAttr(length + '.input1X', 100.0)
        cmds.connectAttr(
            node + '.' + TrackPropEnum.LENGTH.maya, length + '.input2X')

        # scale thetaPlus and thetaMinus by length (since they are 1 cm,
        # multiply by length in cm)
        cmds.connectAttr(length + '.outputX', thetaPlus  + '.scaleZ')
        cmds.connectAttr(length + '.outputX', thetaMinus + '.scaleZ')

        # Then barN is translated forward in z by zN = lengthRatio*length
        # (centimeters)
        zN = cmds.createNode('multiplyDivide', name='zN')
        cmds.setAttr(zN + '.operation', 1)
        cmds.connectAttr(
            node + '.' + TrackPropEnum.LENGTH_RATIO.maya, zN + '.input1X')
        cmds.connectAttr(length + '.outputX',  zN + '.input2X')
        cmds.connectAttr(zN + '.outputX', barN + '.translateZ')

        # Next, translate barS backward in z by (zN - length); output is in
        # zS.output1D
        zS = cmds.createNode('plusMinusAverage', name='sZ')
        cmds.setAttr(zS + '.operation', 2)
        cmds.connectAttr(zN + '.outputX',     zS + '.input1D[0]')
        cmds.connectAttr(length + '.outputX', zS + '.input1D[1]')
        cmds.connectAttr(zS + '.output1D',    barS + '.translateZ')

        # Next, compute the half length, hl = length/2.0 (centimeters)
        hl = cmds.createNode('multiplyDivide', name='hl')
        cmds.setAttr(hl + '.operation', 2)
        cmds.connectAttr(length + '.outputX', hl + '.input1X')
        cmds.setAttr(hl + '.input2X', 2.0)

        # Translate lengthRuler along z by zL = (zN - hl) (centimeters)
        zL = cmds.createNode('plusMinusAverage', name='zL')
        cmds.setAttr(zL + '.operation', 2)
        cmds.connectAttr(zN + '.outputX',  zL + '.input1D[0]')
        cmds.connectAttr(hl + '.outputX',  zL + '.input1D[1]')
        cmds.connectAttr(zL + '.output1D', lengthRuler + '.translateZ')

        # Scale the four 'error bars' to represent the width and length
        # uncertainties (centimeters)
        cmds.connectAttr(
            node + "." + TrackPropEnum.WIDTH_UNCERTAINTY.maya,
            barW + '.scaleX')
        cmds.connectAttr(
            node + "." + TrackPropEnum.WIDTH_UNCERTAINTY.maya,
            barE + '.scaleX')
        cmds.connectAttr(
            node + "." + TrackPropEnum.LENGTH_UNCERTAINTY.maya,
            barN + '.scaleZ')
        cmds.connectAttr(
            node + "." + TrackPropEnum.LENGTH_UNCERTAINTY.maya,
            barS + '.scaleZ')

        # Create an 'inverter' transform under which all the other parts are
        # hung as children, which counteracts scaling applied to its parent
        # triangular node.
        inverter = cmds.createNode('transform', name='inverter')

        # drive the inverter's .scaleX and .scaleZ as the inverse of the parent
        # node's scale values
        sx = cmds.createNode('multiplyDivide', name='sx')
        cmds.setAttr(sx + '.operation', 2)
        cmds.setAttr(sx + '.input1X', 1.0)
        cmds.connectAttr(node + '.scaleX', sx + '.input2X')
        cmds.connectAttr(sx + '.outputX', inverter + '.scaleX')

        sz = cmds.createNode('multiplyDivide', name='sz')
        cmds.setAttr(sz + '.operation', 2)
        cmds.setAttr(sz + '.input1X', 1.0)
        cmds.connectAttr(node + '.scaleZ', sz + '.input2X')
        cmds.connectAttr(sz + '.outputX', inverter + '.scaleZ')

        # Assemble the parts as children under the scale inverter node
        cmds.parent(lengthRuler, inverter)
        cmds.parent(widthRuler,  inverter)
        cmds.parent(barN,        inverter)
        cmds.parent(barS,        inverter)
        cmds.parent(barW,        inverter)
        cmds.parent(barE,        inverter)
        cmds.parent(thetaPlus,   inverter)
        cmds.parent(thetaMinus,  inverter)
        cmds.parent(inverter,    node)

        # Rotate thetaPlus and thetaMinus about the Y axis to indicate
        # rotational uncertainty
        cmds.connectAttr(
            node + '.' + TrackPropEnum.ROTATION_UNCERTAINTY.maya,
            node + '|' + inverter + '|' + thetaPlus + '.rotateY')

        neg = cmds.createNode('multiplyDivide', name='negative')
        cmds.setAttr(neg + '.operation', 1)
        cmds.setAttr(neg + '.input1X',  -1.0)
        cmds.connectAttr(
            node + '.' + TrackPropEnum.ROTATION_UNCERTAINTY.maya,
            neg + '.input2X')
        cmds.connectAttr(
            neg + '.outputX',
            node + '|' + inverter + '|' + thetaMinus + '.rotateY')

        # Disable some transforms of the node
        cmds.setAttr(node + '.rotateX',    lock=True)
        cmds.setAttr(node + '.rotateZ',    lock=True)
        cmds.setAttr(node + '.scaleY',     lock=True)
        cmds.setAttr(node + '.translateY', lock=True)

        # Now, the width of the triangle will be driven by its width attribute
        # (driving .scaleX)
        cmds.connectAttr(node + '.width',  node + '.scaleX')

        # The quantity zN is used to scale length of the triangle
        cmds.connectAttr(zN + '.outputX',  node + '.scaleZ')

        # Scale the 'length' (in x) of the width ruler
        cmds.connectAttr(
            node + '.width',  node + '|' + inverter + '|WidthRuler.scaleX')

        # Scale the length of the length ruler
        cmds.connectAttr(
            node + '.length', node + '|' + inverter + '|LengthRuler.scaleZ')

        # Translate the track node epsilon below ground level (to reveal the
        # overlaid track siteMap)
        cmds.move(0, -epsilon, 0, node)

        # Initialize all the properties from the dictionary
        if props:
            cls.setTrackProps(node, props)
        else:
            print('in createTrackNode:  properties not provided')
            return node

        # Add the new nodeName to the Cadence track scene set, color it, and
        # we're done
        cmds.sets(node, add=trackSetNode)
        cls.colorTrackNode(node, props)
        return node

#_______________________________________________________________________________
    @classmethod
    def getTrackNode(cls, uid, trackSetNode =None):
        trackSetNode = cls.getTrackSetNode() if not trackSetNode\
            else trackSetNode
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

#_______________________________________________________________________________
    @classmethod
    def getUid(cls, node, trackSetNode =None):
        """ This returns the UID (or None if nodeName not a track nodeName). """

        if not trackSetNode:
            trackSetNode = cls.getTrackSetNode()

        if not trackSetNode:
            return None

        if not cmds.sets(node, isMember=trackSetNode):
            return None

        try:
            return cmds.getAttr(node + '.' + TrackPropEnum.UID.maya)
        except Exception as err:
            return None

#_______________________________________________________________________________
    @classmethod
    def checkNodeUidMatch(cls, uid, node):
        try:
            return uid == cls.getUid(node)
        except Exception as err:
            return False

#_______________________________________________________________________________
    @classmethod
    def getTrackProps(cls, node):
        out = dict()

        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.maya is None:
                continue
            out[enum.name] = cmds.getAttr(node + '.' + enum.maya)
        return out

#_______________________________________________________________________________
    @classmethod
    def setTrackProps(cls, node, props):
        for enum in Reflection.getReflectionList(TrackPropEnum):
            if enum.maya and enum.maya in props:
                if enum.type == 'string':
                    cmds.setAttr(
                        node + '.' + enum.maya, props[enum.maya],
                        type=enum.type)
                else:
                    cmds.setAttr(node + '.' + enum.maya, props[enum.maya])

#_______________________________________________________________________________
    @classmethod
    def colorTrackNode(cls, node, props):
        # Save state of selected nodes to restore at end of this function
        priorSelection = MayaUtils.getSelectedTransforms()

        # Use red for left, green for right, in accordance with international
        # maritime convention
        left = props[TrackPropEnum.LEFT.name]
        pes  = props[TrackPropEnum.PES.name]

        if left:
            ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR,   node)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, node)

        # Next, get a shortcut to the components of the track node
        root = node + '|inverter'

        # Make the width and length rulers either light gray (for manus) or
        # dark gray (for pes) and the 'error bars' white.
        c = TrackwayShaderConfig.DARK_GRAY_COLOR if pes else \
            TrackwayShaderConfig.LIGHT_GRAY_COLOR

        ShadingUtils.applyShader(c, root + '|WidthRuler')
        ShadingUtils.applyShader(c, root + '|LengthRuler')

        ShadingUtils.applyShader(
            TrackwayShaderConfig.WHITE_COLOR, root + '|BarN')
        ShadingUtils.applyShader(
            TrackwayShaderConfig.WHITE_COLOR, root + '|BarS')
        ShadingUtils.applyShader(
            TrackwayShaderConfig.WHITE_COLOR, root + '|BarW')
        ShadingUtils.applyShader(
            TrackwayShaderConfig.WHITE_COLOR, root + '|BarE')

        # And finish up with other details
        ShadingUtils.applyShader(
            TrackwayShaderConfig.YELLOW_COLOR, root + '|ThetaPlus')
        ShadingUtils.applyShader(
            TrackwayShaderConfig.YELLOW_COLOR, root + '|ThetaMinus')

        MayaUtils.setSelection(priorSelection)

#_______________________________________________________________________________
    @classmethod
    def getTrackManagerNode(cls, trackSetNode =None, createIfMissing =False):
        """ Returns the name of the track manager nodeName for the current
            Cadence scene.

            trackSetNode: The track set nodeName on which to find the track
            manager nodeName.  If no nodeName is specified the method will look
            it up internally.

            createIfMissing: If true and no track manager nodeName is found one
            will be created and connected to the track set nodeName, which will
            also be created if one does not exist. """

        if not trackSetNode:
            trackSetNode = cls.getTrackSetNode(createIfMissing=createIfMissing)

        connects = cmds.listConnections(
                trackSetNode + '.usedBy',
                source=True,
                destination=False)
        if connects:
            for node in connects:
                if cmds.nodeType(node) == 'trackManager':
                    return node

        if createIfMissing:
            node = cmds.createNode('trackManager')
            cmds.connectAttr(
                node + '.trackSet', trackSetNode + '.usedBy', force=True)
            return node

        return None

#_______________________________________________________________________________
    @classmethod
    def getTrackSetNode(cls, createIfMissing =False):
        for node in cmds.ls(exactType='objectSet'):
            if node == CadenceConfigs.TRACKWAY_SET_NODE_NAME:
                return node

        if createIfMissing:
            return cmds.sets(
                name=CadenceConfigs.TRACKWAY_SET_NODE_NAME, empty=True)

        return None


#===============================================================================
#                                                      T O K E N  S U P P O R T
#
#_______________________________________________________________________________
    @classmethod
    def createToken(cls, uid, props, trackSetNode =None):
        """ A token is created, provided with some additional Maya attributes,
            and placed in the scene. Tokens are functtionally similar to
            TrackNodes, but with different shapes and attributes. """

        cylinderHeight = 5.0
        coneHeight     = 10.0

        if not trackSetNode:
            trackSetNode = TrackSceneUtils.getTrackSetNode()

        if not trackSetNode:
            return None

        node = cls.getTrackNode(uid, trackSetNode=trackSetNode)

        if node:
            return node

        # determine whether left or right, and manus or pes, from name
        name = props['name'] if props else None
        if not name:
            print('createToken:  No properties specified')
            return
        # remove '_proxy' or '_token' if present (as in S6_LP3_proxy)
        nameFields = cls.decomposeName(name.split('_')[0])
        isLeft     = nameFields['left']
        isPes      = nameFields['pes']

        # make a cone for the token of an proxy else a cylinder
        if uid.endswith('_proxy'):
            node = cmds.polyCone(
                radius=0.5,
                height=coneHeight,
                subdivisionsX=10,
                subdivisionsY=1,
                subdivisionsZ=1,
                axis=(0, 1, 0),
                createUVs=0,
                constructionHistory=0,
                name='Token_0')[0]
            cmds.move(0, 0.5 * coneHeight, 0)
        else:
            node = cmds.polyCylinder(
                radius=0.5,
                height=cylinderHeight,
                subdivisionsX=10,
                subdivisionsY=1,
                subdivisionsZ=1,
                subdivisionsCaps=0,
                axis=(0, 1, 0),
                createUVs=0,
                constructionHistory=0,
                name='Token_0')[0]
            cmds.move(0, 0.5 * cylinderHeight, 0)

        # Set up the basic cadence attributes
        cmds.addAttr(longName='cadence_dx', shortName='dx', niceName='DX')
        cmds.addAttr(longName='cadence_dy', shortName='dy', niceName='DY')

        cmds.addAttr(
             longName='cadence_uniqueId',
             shortName='track_uid',
             dataType='string',
             niceName='UID')

        cmds.addAttr(
             longName='cadence_name',
             shortName='token_name',
             dataType='string',
             niceName='Name')

        # Disable some transform attributes
        cmds.setAttr(node + '.rotateX',    lock=True)
        cmds.setAttr(node + '.rotateZ',    lock=True)
        cmds.setAttr(node + '.scaleY',     lock=True)
        cmds.setAttr(node + '.translateY', lock=True)

        # Scale the cylinder/cone in x and z to represent 'dy' and 'dx' in
        # centimeters. There is a change of coordinates between Maya (X, Z) and
        # the simulator (X, Y) space. For example, for the right manus:
        #    x = int(100*float(entry['rm_y']))
        #    z = int(100*float(entry['rm_x']))
        # and likewise for dx and dy.

        # the DX and DY attributes affect scaleZ and scaleX in the node
        cmds.connectAttr(node + '.dx', node + '.scaleZ')
        cmds.connectAttr(node + '.dy', node + '.scaleX')

        # add a short annotation based on the name
        annotation = cmds.annotate(node, text=cls.shortName(props['name']))
        cmds.select(annotation)
        aTransform = cmds.pickWalk(direction='up')[0]

        # control it's position by that of the node, so that it stays 15 cm
        # above the pes and 10 cm above the manus
        if isPes:
            cmds.move(0.0, 15.0, 0.0, aTransform)
        else:
            cmds.move(0.0, 10.0, 0.0, aTransform)

        cmds.connectAttr(node + '.translateX', aTransform + '.translateX')
        cmds.connectAttr(node + '.translateZ', aTransform + '.translateZ')

        # and make it non-selectable
        cmds.setAttr(aTransform + '.overrideEnabled', 1)
        cmds.setAttr(aTransform + '.overrideDisplayType', 2)
        cmds.rename(aTransform, "TokenAnnotation_0")

        if isPes:
            if isLeft:
                color = TrackwayShaderConfig.LEFT_PES_TOKEN_COLOR
            else:
                color = TrackwayShaderConfig.RIGHT_PES_TOKEN_COLOR
        else:
            if isLeft:
                color = TrackwayShaderConfig.LEFT_MANUS_TOKEN_COLOR
            else:
                color = TrackwayShaderConfig.RIGHT_MANUS_TOKEN_COLOR
        ShadingUtils.applyShader(color, node)

        cmds.select(node)
        # add the new node to the Cadence track set
        cmds.sets(node, add=trackSetNode)

        # finally, initialize all the properties from the dictionary props
        cls.setTokenProps(node, props)

        return node

# @classmethod
# def createToken(cls, uid, props, trackSetNode=None):
#     """ A token is created, provided with some additional Maya attributes,
#         and placed in the scene. Tokens are functtionally similar to
#         TrackNodes, but with different shapes and attributes. """
#
#     if not trackSetNode:
#         trackSetNode = TrackSceneUtils.getTrackSetNode()
#
#     if not trackSetNode:
#         return None
#
#     node = cls.getTrackNode(uid, trackSetNode=trackSetNode)
#
#     if node:
#         return node
#
#     cylinderHeight = 4.0
#     coneHeight = 8.0
#
#     # determine whether left or right, and manus or pes, from name
#     name = props['name'] if props else None
#     if not name:
#         print('createToken:  No properties specified')
#         return
#     # remove '_proxy' or '_token' if present (as in S6_LP3_proxy)
#     nameFields = cls.decomposeName(name.split('_')[0])
#     isLeft = nameFields['left']
#     isPes = nameFields['pes']
#
#     # make a cylinder for a pes token and a cone for a manus token
#     if isPes:
#         node = cmds.polyCylinder(
#             radius=0.5,
#             height=cylinderHeight,
#             subdivisionsX=10,
#             subdivisionsY=1,
#             subdivisionsZ=1,
#             subdivisionsCaps=0,
#             axis=(0, 1, 0),
#             createUVs=0,
#             constructionHistory=0,
#             name='Token_0')[0]
#         cmds.move(0, 0.5 * cylinderHeight, 0)
#     else:
#         node = cmds.polyCone(
#             radius=0.5,
#             height=coneHeight,
#             subdivisionsX=10,
#             subdivisionsY=1,
#             subdivisionsZ=1,
#             axis=(0, 1, 0),
#             createUVs=0,
#             constructionHistory=0,
#             name='Token_0')[0]
#         cmds.move(0, 0.5 * coneHeight, 0)
#
#     # Set up the basic cadence attributes
#     cmds.addAttr(longName='cadence_dx', shortName='dx', niceName='DX')
#     cmds.addAttr(longName='cadence_dy', shortName='dy', niceName='DY')
#
#     cmds.addAttr(
#         longName='cadence_uniqueId',
#         shortName='track_uid',
#         dataType='string',
#         niceName='UID')
#
#     cmds.addAttr(
#         longName='cadence_name',
#         shortName='token_name',
#         dataType='string',
#         niceName='Name')
#
#     # Disable some transform attributes
#     cmds.setAttr(node + '.rotateX', lock=True)
#     cmds.setAttr(node + '.rotateZ', lock=True)
#     cmds.setAttr(node + '.scaleY', lock=True)
#     cmds.setAttr(node + '.translateY', lock=True)
#
#     # Scale the cylinder/cone in x and z to represent 'dy' and 'dx' in
#     # centimeters. There is a change of coordinates between Maya (X, Z) and
#     # the simulator (X, Y) space. For example, for the right manus:
#     #    x = int(100*float(entry['rm_y']))
#     #    z = int(100*float(entry['rm_x']))
#     # and likewise for dx and dy.
#
#     # the DX and DY attributes affect scaleZ and scaleX in the node
#     cmds.connectAttr(node + '.dx', node + '.scaleZ')
#     cmds.connectAttr(node + '.dy', node + '.scaleX')
#
#     # add a short annotation based on the name
#     annotation = cmds.annotate(node, text=cls.shortName(props['name']))
#     cmds.select(annotation)
#     aTransform = cmds.pickWalk(direction='up')[0]
#
#     # control it's position by that of the node stays 15 cm above the pes
#     # and 10 cm above the manus
#     if isPes:
#         cmds.move(0.0, 15.0, 0.0, aTransform)
#     else:
#         cmds.move(0.0, 10.0, 0.0, aTransform)
#
#     cmds.connectAttr(node + '.translateX', aTransform + '.translateX')
#     cmds.connectAttr(node + '.translateZ', aTransform + '.translateZ')
#
#     # and make it non-selectable
#     cmds.setAttr(aTransform + '.overrideEnabled', 1)
#     cmds.setAttr(aTransform + '.overrideDisplayType', 2)
#     cmds.rename(aTransform, "TokenAnnotation_0")
#
#     # if a proxy, color it blue; if a token, color it red or green.
#     if uid.endswith('_proxy'):
#         ShadingUtils.applyShader(TrackwayShaderConfig.BLUE_COLOR, node)
#     else:
#         if isLeft:
#             ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR, node)
#         else:
#             ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, node)
#
#     cmds.select(node)
#     # add the new node to the Cadence track set
#     cmds.sets(node, add=trackSetNode)
#
#     # finally, initialize all the properties from the dictionary props
#     cls.setTokenProps(node, props)
#
#     return node

#_______________________________________________________________________________
    @classmethod
    def getTokenProps(cls, node):
        """ This returns the attributes uid, x, dx, y, dy.  Values in Maya are
            in centimeters, hence the conversion to meters. """

        out = dict()
        out['name'] = cmds.getAttr(node + '.token_name')
        out['uid']  = cmds.getAttr(node + '.track_uid')
        out['x']    = cmds.getAttr(node + '.translateZ')/100.0
        out['dx']   = cmds.getAttr(node + '.dx')/100.0
        out['y']    = cmds.getAttr(node + '.translateX')/100.0
        out['dy']   = cmds.getAttr(node + '.dy')/100.0
        return out

#_______________________________________________________________________________
    @classmethod
    def setTokenProps(cls, node, props):
        """ This sets the attributes of a token:  uid, x, dx, y, dy.  It
            accounts for the change of coordinates right inside Maya."""

        cmds.setAttr(node + '.token_name',  props['name'], type='string')
        cmds.setAttr(node + '.track_uid',   props['uid'], type='string')
        cmds.setAttr(node + '.translateZ',  100.0*props['x'])
        cmds.setAttr(node + '.dx',          100.0*props['dx'])
        cmds.setAttr(node + '.translateX',  100.0*props['y'])
        cmds.setAttr(node + '.dy',          100.0*props['dy'])

#_______________________________________________________________________________
    @classmethod
    def getTokenNode(cls, uid, trackSetNode =None):
        """ This returns the name (string) of the node in the trackSet
            for the object with matching UID attribute. """

        if not trackSetNode:
            trackSetNode = cls.getTrackSetNode()
        if not trackSetNode:
            return None

        nodes = cmds.sets(trackSetNode, query=True)
        if not nodes:
            return None

        for node in nodes:
            if not cmds.hasAttr(node + '.' + 'track_uid'):
                continue
            if uid == cmds.getAttr(node + '.' + 'track_uid'):
                return node

        return None

#_______________________________________________________________________________
    @classmethod
    def shortName(cls, name):
        """ Given, e.g., 'CRO-500-2004-1-S-6-L-P-2', returns the string LP2. """

        parts = name.split('-')
        if len(parts) == 9:
            side   = parts[6]
            limb   = parts[7]
            number = parts[8]
            return side + limb + number
        elif len(parts) == 3:
            side    = parts[0]
            limb    = parts[1]
            number  = parts[2]
            return side + limb + number
        else:
            print('shortName:  unrecognized format for name string')
            return None

#_______________________________________________________________________________
    @classmethod
    def decomposeName(cls, name):
        """ Given, for example, 'CRO-500-2004-1-S-6-L-P-2', this returns a
            dictionary with the keys: pes, left, number, and trackway. In this
            example, trackway = CRO-500-2004-1-S-6, left = True, Pes = T, and
            number is the string '2'. """

        out = { 'number':None, 'pes':None, 'left':None, 'trackway':None }
        parts = name.split('-')
        if len(parts) == 9:
            out['trackway'] = format('%s-%s-%s-%s-%s-%s' % tuple(parts[0:6]))
            out['left']     = True if parts[6] == 'L' else False
            out['pes']      = True if parts[7] == 'P' else False
            out['number']   = parts[8].split('_')[0]
            return out
        elif len(parts) == 3:
            out['left']     = True if parts[0] == 'L' else False
            out['pes']      = True if parts[1] == 'P' else False
            out['number']   = parts[2].split('_')[0]
            return out
        else:
            print('decomposeName:  unrecognized format for name string')
            return None