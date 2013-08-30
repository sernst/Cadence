# TrackController.py
# (C)2013
# Scott Ernst

from ziggurat.view.api.ApiController import ApiController

#___________________________________________________________________________________________________ TrackController
class TrackController(ApiController):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, router):
        """Creates a new instance of TrackController."""
        super(TrackController, self).__init__(router)

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ get
    def get(self):
        trackIds = self._router.getArg('ids')
        self._router.logger.write('GET TRACKS: ' + str(trackIds))

        return dict(
            tracks=[]
        )

#___________________________________________________________________________________________________ put
    def put(self):
        tracks = self._router.getArg('tracks')
        self._router.logger.write('PUT TRACKS: ' + str(tracks))

        return dict(
            success=True
        )

