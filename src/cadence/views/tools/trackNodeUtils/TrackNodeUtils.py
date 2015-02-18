# TrackNodeUtils.py
# (C)2015
# Kent A. Stevens


from nimble import cmds

from cadence.enums.TrackPropEnum import TrackPropEnum
from cadence.CadenceEnvironment import CadenceEnvironment

#___________________________________________________________________________________________________ TrackNodeUtils
class TrackNodeUtils(object):
    """ A class for operating directly upon the track nodes in a Maya scene, without dependence
        upon a database session. """

#___________________________________________________________________________________________________ getTrackSetNode
    @classmethod
    def getTrackSetNode(cls):
        """ Get the TrackSet from the Maya scene so we can map from UID to track nodes """

        for node in cmds.ls(exactType='objectSet'):
            if node == CadenceEnvironment.TRACKWAY_SET_NODE_NAME:
                return node
        return None

#___________________________________________________________________________________________________ getTrackNode
    @classmethod
    def getTrackNode(cls, uid):
        """ This returns the (string) name of the track node for a given UID, else None. """

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

#___________________________________________________________________________________________________ setDatum
    @classmethod
    def setDatum(cls, node, value):
        """ Sets the numeric datum value, creating the attribute if not already defined. """

        if not cmds.attributeQuery('datum', node=node, exists=True):
            cmds.addAttr(node, longName='cadence_datum', shortName='datum', niceName='Datum')

        cmds.setAttr(node + '.datum', value)

#___________________________________________________________________________________________________ setDatum
    @classmethod
    def getDatum(cls, node):
        """ Returns the numeric datum value, else None. """

        if not cmds.attributeQuery('datum', node=node, exists=True):
            return None

        return cmds.getAttr(node + '.datum')

#___________________________________________________________________________________________________ setNodeLinks
    @classmethod
    def setNodeLinks(cls, node, prev, next):
        """ Sets up two attributes, prev and next, that directly link the given node to its
            previous and next nodes. """

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

#___________________________________________________________________________________________________ getLength
    @classmethod
    def getLength(cls, node):
        """ Returns the length value directly from the node. """

        return cmds.getAttr(node + '.length')

#___________________________________________________________________________________________________ getLengthUncertainty
    @classmethod
    def getLengthUncertainty(cls, node):
        """ Returns the length uncertainty value directly from the node. """

        return cmds.getAttr(node + '.lengthUncertainty')


#___________________________________________________________________________________________________ getNextNode
    @classmethod
    def getNextNode(cls, node):
        """ Returns the next track node to a given node else None. """

        if not cmds.attributeQuery('next', node=node, exists=True):
            return None

        return cmds.getAttr(node + '.next')

#___________________________________________________________________________________________________ getPosition
    @classmethod
    def getPosition(cls, node):
        """ Returns the pair of coordiantes for this track node directly from the node. """

        return (cmds.getAttr(node + '.translateX'), cmds.getAttr(node + '.translateZ'))

#___________________________________________________________________________________________________ getPrevNode
    @classmethod
    def getPrevNode(cls, node):
        """ Returns the previous track node to a given node else None. """

        if not cmds.attributeQuery('prev', node=node, exists=True):
            return None

        return cmds.getAttr(node + '.prev')

 #___________________________________________________________________________________________________ getRotation
    @classmethod
    def getRotation(cls, node):
        """ Returns the rotationvalue directly from the node. """

        return cmds.getAttr(node + '.rotateY')
#___________________________________________________________________________________________________ getRotationUncertainty
    @classmethod
    def getRotationUncertainty(cls, node):
        """ Returns the rotation uncertainty value directly from the node. """

        return cmds.getAttr(node + '.rotationUncertainty')

#___________________________________________________________________________________________________ getWidth
    @classmethod
    def getWidth(cls, node):
        """ Returns the width value directly from the node. """

        return cmds.getAttr(node + '.width')

#___________________________________________________________________________________________________ getWidthUncertainty
    @classmethod
    def getWidthUncertainty(cls, node):
        """ Returns the width uncertainty value directly from the node. """

        return cmds.getAttr(node + '.widthUncertainty')
