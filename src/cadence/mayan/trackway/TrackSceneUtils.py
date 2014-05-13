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

    DISK_RADIUS = 10

#___________________________________________________________________________________________________ createTrackNode
    @classmethod
    def createTrackNode(cls, uid, trackSetNode =None, props =None):
        if not trackSetNode:
            trackSetNode = TrackSceneUtils.getTrackSetNode()
        if not trackSetNode:
            return None

        node = cls.getTrackNode(uid, trackSetNode=trackSetNode)
        if node:
            return node

        a = 100
        node = cmds.polyPrism(
            length=0.5,
            sideLength=a,
            numberOfSides=3,
            subdivisionsHeight=1,
            subdivisionsCaps=0,
            axis=(0,1,0),
            createUVs=3,
            constructionHistory=1,
            name='Track0')[0]
        cmds.scale(2.0/math.sqrt(3.0), 1.0, 1.0)
        cmds.rotate(0.0, -90.0, 0.0)

        cmds.move(0, 0, a/3.0)
        cmds.move(0, 0, 0, node + ".scalePivot", node + ".rotatePivot", absolute=True)
        cmds.makeIdentity(
            apply=True,
            translate=True,
            rotate=True,
            scale=True,
            normal=False)
        cmds.move(0, -1.0, 0)

# set up additional attributes to map from track data to node attributes
        cmds.addAttr(
            longName='cadence_length',
#            shortName=TrackPropEnum.LENGTH,
            shortName='length',
            niceName='Length')
        cmds.addAttr(
            longName='cadence_width',
#            shortName=TrackPropEnum.WIDTH,
            shortName='width',
            niceName='Width')
        cmds.addAttr(
            longName='cadence_widthUncertainty',
#           shortName=TrackPropEnum.WIDTH_UNCERTAINTY,
            shortName='widthUncertainty',
            niceName='WidthUncertainty')
        cmds.addAttr(
            longName='cadence_lengthUncertainty',
#           shortName=TrackPropEnum.LENGTH_UNCERTAINTY,
            shortName='lengthUncertainty',
            niceName='LengthUncertainty')

        tail = cmds.polyCube(
            axis=(0,1,0),
            width=10.0,
            height=0.5,
            depth=100.0,
            subdivisionsX=1,
            subdivisionsY=1,
            createUVs=3,
            constructionHistory=1,
            name='Tail')[0]
        cmds.move(0, 0, -50)
        cmds.move(0, 0, 0, tail + ".scalePivot", tail + ".rotatePivot", absolute=True)
        cmds.makeIdentity(
            apply=True,
            translate=True,
            rotate=True,
            scale=True,
            normal=False)
        cmds.move(0, -1.0, 0)
        cmds.setAttr(tail + '.overrideEnabled', 1)
        cmds.setAttr(tail + '.overrideDisplayType', 2)

        # the tail length is the track length (node.length) minus the head length (node.scaleZ)
        tailLength = cmds.createNode('plusMinusAverage', name='tailLength')
        cmds.setAttr(tailLength + '.operation', 2)
        cmds.connectAttr(node + '.length', tailLength + '.input1D[0]')
        cmds.connectAttr(node + '.sz', tailLength + '.input1D[1]')
        normalizeScale = cmds.createNode('multiplyDivide', name='normalizeScale')
        cmds.setAttr(normalizeScale + '.operation', 2)
        cmds.connectAttr(tailLength + '.output1D', normalizeScale + '.input1X')
        cmds.connectAttr(node + '.sz', normalizeScale + '.input2X')
        cmds.connectAttr(normalizeScale + '.outputX', tail + '.sz')

        cmds.parent(tail, node)

        cmds.select(node)
        cmds.setAttr(node + '.rotateX', lock=True)
        cmds.setAttr(node + '.rotateZ', lock=True)
        cmds.setAttr(node + '.scaleY', lock=True)
        cmds.setAttr(node + '.translateY', lock=True)
        cmds.addAttr(
            longName='cadence_uniqueId',
            shortName=TrackPropEnum.UID.maya,
            dataType='string',
            niceName='Unique ID')

# initialize the values of the attributes (this is for testing only)
        cmds.setAttr(node + '.width', .3)
        cmds.setAttr(node + '.length', .5)
#       cmds.setAttr(node + '.widthUncertainty', 0.01)
#       cmds.setAttr(node + '.lengthUncertainty', 0.01)

        # Add the new nodeName to the Cadence track scene set
        cmds.sets(node, add=trackSetNode)

        if props:
            cls.setTrackProps(node, props)

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

            trackSetNode: The track set nodeName on which to find the track manager nodeName. If no nodeName
                    is specified the method will look it up internally.

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
