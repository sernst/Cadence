# TrackSceneUtils.py
# (C)2014
# Scott Ernst

from nimble import cmds

from pyaid.reflection.Reflection import Reflection

from cadence.CadenceEnvironment import CadenceEnvironment
from cadence.enum.TrackPropEnum import TrackPropEnum

#___________________________________________________________________________________________________ TrackSceneUtils
class TrackSceneUtils(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ getTrackNode
    @classmethod
    def getTrackNode(cls, uid, trackSetNode =None):
        trackSetNode = TrackSceneUtils.getTrackSetNode() if not trackSetNode else trackSetNode
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

#___________________________________________________________________________________________________ checkNodeUidMatch
    @classmethod
    def checkNodeUidMatch(cls, uid, node):
        try:
            return uid == cmds.getAttr(node + '.' + TrackPropEnum.UID.maya)
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
        """ Returns the name of the track manager node for the current Cadence scene.

            trackSetNode: The track set node on which to find the track manager node. If no node
                    is specified the method will look it up internally.

            createIfMissing: If true and no track manager node is found one will be created and
                    connected to the track set node, which will also be created if one does
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
