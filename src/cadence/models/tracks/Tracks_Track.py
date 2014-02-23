# Tracks_Track.py
# (C)2013-2014
# Scott Ernst

import nimble
from nimble import cmds

from cadence.config.TrackwayShaderConfig import TrackwayShaderConfig

from cadence.mayan.trackway import GetTrackNodeData
from cadence.mayan.trackway import UpdateTrackNode
from cadence.mayan.trackway import CreateTrackNode
from cadence.models.tracks.TracksDefault import TracksDefault
from cadence.util.shading.ShadingUtils import ShadingUtils

#___________________________________________________________________________________________________ Tracks_Track
class Tracks_Track(TracksDefault):
    """ Database model representation of a track with all the attributes and information for a
        specific track as well as a connectivity information for the track within its series. """

#===================================================================================================
#                                                                                       C L A S S

    __tablename__  = u'tracks'

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: nodeName
    @property
    def nodeName(self):
        """ A cached value for the name of the Maya node representing this track if one exists,
            which is updated each time a create/update operation on the node occurs. Can be
            incorrect if the node was renamed between such operations. """
        return self.fetchTransient('nodeName')
    @nodeName.setter
    def nodeName(self, value):
        self.putTransient('nodeName', value)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ createNode
    def createNode(self):
        """ Create an elliptical cylinder (disk) plus a superimposed triangular pointer to signify
            the position, dimensions, and rotation of a manus or pes print.  The cylinder has a
            diameter of one meter so that the scale in x and z equates to the width and length of
            the manus or pes in fractional meters (e.g., 0.5 = 50 cm).  The pointer is locked to
            not be non-selectable (reference) and the marker is prohibited from changing y
            (elevation) or rotation about either x or z.  The color of the cylinder indicates manus
            versus pes, and the color of the pointer on top of the cylinder indicates left versus
            right."""

        conn = nimble.getConnection()
        out  = conn.runPythonModule(CreateTrackNode, uid=self.uid, props=self.toMayaNodeDict())
        if not out.success:
            print 'CREATE NODE ERROR:', out.error
            return None

        self.nodeName = out.payload['node']

        return self.nodeName

#___________________________________________________________________________________________________ updateNode
    def updateNode(self):
        """ Sends values to Maya node representation of the track to synchronize the values in the
            model and the node. """
        conn = nimble.getConnection()
        result = conn.runPythonModule(UpdateTrackNode, uid=self.uid, props=self.toMayaNodeDict())
        if not result.success:
            return False

        self.nodeName = result.payload.get('node')
        return True

#___________________________________________________________________________________________________ updateFromNode
    def updateFromNode(self):
        """ Retrieves Maya values from the node representation of the track and updates this
            model instance with those values. """

        conn = nimble.getConnection()
        result = conn.runPythonModule(GetTrackNodeData, uid=self.uid, node=self.nodeName)
        if result.payload.get('error'):
            print 'NODE ERROR:', result.payload.get('message')
            return False

        self.nodeName = result.payload.get('node')

        if self.nodeName:
            self.fromDict(result.payload.get('props'))
            return True

        return False

#___________________________________________________________________________________________________ colorTrack
    def colorTrack(self):
        """ TODO: Kent... """
        if not self.nodeName:
            return False

        if self.pes:
            ShadingUtils.applyShader(TrackwayShaderConfig.DARK_GRAY_COLOR, self.nodeName)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.LIGHT_GRAY_COLOR, self.nodeName)

        if self.left:
            ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR, self.nodeName + '|pointer')
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, self.nodeName + '|pointer')

        return True

#___________________________________________________________________________________________________ setCadenceCamFocus
    def setCadenceCamFocus(self):
        """ TODO: Kent... """
        if self.nodeName is None:
            return

        if not cmds.objExists('CadenceCam'):
            self.initializeCadenceCam()
        height = cmds.xform('CadenceCam', query=True, translation=True)[1]
        cmds.move(self.x, height, self.z, 'CadenceCam', absolute=True)

#___________________________________________________________________________________________________ incrementName
    @classmethod
    def incrementName(cls, name):
        """ TODO: Kent... """
        prefix = name[:2]
        number = int(name[2:])
        return prefix + str(number + 1)

#___________________________________________________________________________________________________ initializeCadenceCam
    @classmethod
    def initializeCadenceCam(cls):
        """ TODO: Kent... """
        c = cmds.camera(
            orthographic=True,
            nearClipPlane=1,
            farClipPlane=100000,
            orthographicWidth=500)
        cmds.rename(c[0], 'CadenceCam')
        cmds.rotate(-90, 180, 0)
        cmds.move(0, 100, 0, 'CadenceCam', absolute=True)
