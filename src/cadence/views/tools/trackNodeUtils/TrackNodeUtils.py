# TrackNodeUtils.py
# (C)2015
# Kent A. Stevens


from nimble import cmds

from cadence.config import CadenceConfigs
from cadence.enums.TrackPropEnum import TrackPropEnum


#_______________________________________________________________________________
class TrackNodeUtils(object):
    """ A class for operating directly upon the track nodes in a Maya scene,
        without dependence upon a database session. """

#_______________________________________________________________________________
    @classmethod
    def getTrackSetNode(cls):
        """ Get the TrackSet from the Maya scene so we can map from UID to track
            nodes """

        for node in cmds.ls(exactType='objectSet'):
            if node == CadenceConfigs.TRACKWAY_SET_NODE_NAME:
                return node
        return None

#_______________________________________________________________________________
    @classmethod
    def getTrackNode(cls, uid):
        """ This returns the (string) name of the track node for a given UID,
            else None. """

        trackSetNode = cls.getTrackSetNode()

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
    def setNodeDatum(cls, node, value):
        """ Sets the numeric datum value, creating the attribute if not already
            defined. """

        if not cmds.attributeQuery('datum', node=node, exists=True):
            cmds.addAttr(
                node,
                longName='cadence_datum',
                shortName='datum',
                niceName='Datum')

        cmds.setAttr(node + '.datum', value)

#_______________________________________________________________________________
    @classmethod
    def getNodeDatum(cls, node):
        """ Returns the numeric datum value, else None. """

        if not cmds.attributeQuery('datum', node=node, exists=True):
            return None

        return cmds.getAttr(node + '.datum')

#_______________________________________________________________________________
    @classmethod
    def setNodeLinks(cls, node, prev, next):
        """ Sets up two attributes, prev and next, that directly link the given
            node to its previous and next nodes. """

        if not cmds.attributeQuery('prevNode', node=node, exists=True):
            cmds.addAttr(
                node,
                longName='cadence_prevNode',
                shortName='prevNode',
                dataType='string',
                niceName='PrevNode')

        if not cmds.attributeQuery('nextNode', node=node, exists=True):
            cmds.addAttr(
                node,
                longName='cadence_nextNode',
                shortName='nextNode',
                dataType='string',
                niceName='NextNode')

        if prev:
            cmds.setAttr(node + '.prevNode', prev, type='string')
        if next:
            cmds.setAttr(node + '.nextNode', next, type='string')

#_______________________________________________________________________________
    @classmethod
    def getLength(cls, node):
        """ Returns the length value directly from the node. """

        return cmds.getAttr(node + '.length')

#_______________________________________________________________________________
    @classmethod
    def getLengthUncertainty(cls, node):
        """ Returns the length uncertainty value directly from the node. """

        return cmds.getAttr(node + '.lengthUncertainty')


#_______________________________________________________________________________
    @classmethod
    def getNextNode(cls, node):
        """ Returns the next track node to a given node else None. """

        if not cmds.attributeQuery('next', node=node, exists=True):
            return None

        return cmds.getAttr(node + '.next')

#_______________________________________________________________________________
    @classmethod
    def getPosition(cls, node):
        """ Returns the pair of coordiantes for this track node directly from the node. """

        return (cmds.getAttr(node + '.translateX'), cmds.getAttr(node + '.translateZ'))

#_______________________________________________________________________________
    @classmethod
    def getPrevNode(cls, node):
        """ Returns the previous track node to a given node else None. """

        if not cmds.attributeQuery('prev', node=node, exists=True):
            return None

        return cmds.getAttr(node + '.prev')

 #_______________________________________________________________________________
    @classmethod
    def getRotation(cls, node):
        """ Returns the rotationvalue directly from the node. """

        return cmds.getAttr(node + '.rotateY')
#_______________________________________________________________________________
    @classmethod
    def getRotationUncertainty(cls, node):
        """ Returns the rotation uncertainty value directly from the node. """

        return cmds.getAttr(node + '.rotationUncertainty')

#_______________________________________________________________________________
    @classmethod
    def getWidth(cls, node):
        """ Returns the width value directly from the node. """

        return cmds.getAttr(node + '.width')

#_______________________________________________________________________________
    @classmethod
    def getWidthUncertainty(cls, node):
        """ Returns the width uncertainty value directly from the node. """

        return cmds.getAttr(node + '.widthUncertainty')
