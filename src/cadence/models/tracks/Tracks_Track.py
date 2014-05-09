# Tracks_Track.py
# (C)2013-2014
# Scott Ernst

import nimble
from nimble import cmds
from pyaid.dict.DictUtils import DictUtils

from cadence.config.TrackwayShaderConfig import TrackwayShaderConfig

from cadence.mayan.trackway import GetTrackNodeData
from cadence.mayan.trackway import UpdateTrackNode
from cadence.mayan.trackway import CreateTrackNode
from cadence.models.tracks.TracksDefault import TracksDefault
from cadence.util.shading.ShadingUtils import ShadingUtils

#___________________________________________________________________________________________________ Tracks_Track
class Tracks_Track(TracksDefault):
    """ Database model representation of a track with all the attributes and information for a
        specific track as well connectivity information for the track within its series. """

#===================================================================================================
#                                                                                       C L A S S

    __tablename__  = u'tracks'

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: nodeName
    @property
    def nodeName(self):
        """ A cached value for the name of the Maya nodeName representing this track if one exists,
            which is updated each time a create/update operation on the nodeName occurs. Can be
            incorrect if the nodeName was renamed between such operations. """
        return self.fetchTransient('nodeName')
    @nodeName.setter
    def nodeName(self, value):
        self.putTransient('nodeName', value)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ createNode
    def createNode(self):
        """ Create a visual representation of a track, to signify the position, dimensions (length
            and width), and rotation of either a manus or pes print.  The representation has
            basic dimensions of one meter so that the scale in x and z equates to the width and
            length of the manus or pes in fractional meters (e.g., 0.5 = 50 cm).  Individual
            components within the track node are made non-selectable (reference) and the marker is
            prohibited from changing y (elevation) or to rotate about either x or z. """
        conn = nimble.getConnection()
        out  = conn.runPythonModule(
            CreateTrackNode,
            uid=self.uid,
            props=self.toMayaNodeDict(),
            runInMaya=False)
        if not out.success:
            print 'CREATE NODE ERROR:', out.error
            return None

        self.nodeName = out.payload.get('nodeName')

        return self.nodeName

#___________________________________________________________________________________________________ updateNode
    def updateNode(self):
        """ Sends values to Maya nodeName representation of the track to synchronize the values in
            the model and the nodeName. """
        conn = nimble.getConnection()
        result = conn.runPythonModule(UpdateTrackNode, uid=self.uid, props=self.toMayaNodeDict())
        if not result.success:
            return False

        self.nodeName = result.payload.get('nodeName')
        return True

#___________________________________________________________________________________________________ updateFromNode
    def updateFromNode(self):
        """ Retrieves Maya values from the nodeName representation of the track and updates this
            model instance with those values. """
        conn = nimble.getConnection()
        result = conn.runPythonModule(GetTrackNodeData, uid=self.uid, nodeName=self.nodeName)
        if result.payload.get('error'):
            print 'NODE ERROR:', result.payload.get('message')
            return False

        print 'UpdateFromNode:', DictUtils.prettyPrint(result.payload)
        self.nodeName = result.payload.get('nodeName')

        if self.nodeName:
            self.fromDict(result.payload.get('props'))
            return True

        return False

#___________________________________________________________________________________________________ colorTrack
    def colorTrack(self):
        """ THIS WILL BE REWORKED FOR MORE GENERALITY, TO BE PASSED IN SHADERS AS ARGS. """
        if not self.nodeName:
            return False

        if self.left:
            ShadingUtils.applyShader(TrackwayShaderConfig.RED_COLOR, self.nodeName)
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.GREEN_COLOR, self.nodeName)

        if self.pes:
            ShadingUtils.applyShader(TrackwayShaderConfig.DARK_GRAY_COLOR, self.nodeName + '|Tail')
        else:
            ShadingUtils.applyShader(TrackwayShaderConfig.LIGHT_GRAY_COLOR, self.nodeName + '|Tail')


        return True

#___________________________________________________________________________________________________ setCadenceCamFocus
    def setCadenceCamFocus(self):
        """ Positions the CadenceCam to be centered upon this track nodeName (and initializes the
            camera if no camera already exists with that name). Note that the camera is initially
            100 m above the plane, but that can be subsequently adjusted in Maya. """
        if self.nodeName is None:
            return

        if not cmds.objExists('CadenceCam'):
            print 'hmmm, no CadenceCam'
            self.initializeCadenceCam()
        height = cmds.xform('CadenceCam', query=True, translation=True)[1]
        cmds.move(self.x, height, self.z, 'CadenceCam', absolute=True)

#___________________________________________________________________________________________________ initializeCadenceCam
    @classmethod
    def initializeCadenceCam(cls):
        """ This creates an orthographic camera that looks down the Y axis onto the XZ plane,
            and rotated so that the AI file track labels are legible.  This camera will then be
            positioned so that the given track nodeName is centered in its field by
            setCadenceCamFocus. """
        c = cmds.camera(
            orthographic=True,
            nearClipPlane=1,
            farClipPlane=100000,
            orthographicWidth=500)
        cmds.rename(c[0], 'CadenceCam')
        cmds.rotate(-90, 180, 0)
        cmds.move(0, 100, 0, 'CadenceCam', absolute=True)
