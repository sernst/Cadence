# Tracks_SiteMap.py
# (C)2014-2015
# Scott Ernst and Kent A. Stevens

from __future__ import print_function, absolute_import, unicode_literals, division

from pyaid.config.ConfigsDict import ConfigsDict
from pyaid.radix.Base36 import Base36
import sqlalchemy as sqla

from cadence.models.tracks.TracksDefault import TracksDefault



# AS NEEDED: from cadence.models.tracks.Tracks_Track import Tracks_Track
# AS NEEDED: from cadence.models.tracks.Tracks_Trackway import Tracks_Trackway

#___________________________________________________________________________________________________ Tracks_SiteMap
class Tracks_SiteMap(TracksDefault):
    """ A database model class containing coordinate information for trackway excavation site maps.
        The following public methods assist in mapping from scene coordinates to siteMap coordinates,
        and vice versa, and  Federal coordinates:

            projectToMap(sceneX, sceneZ)    returns the corresponding site map point [mapX, mapY]
            projectToScene(mapX, mapY) 	    returns the corresponding scene point [sceneX, sceneZ]
            getFederalCoordinates()         returns the federal coordinates [east, north]

        The federal coordinates marker is translated to the origin of the scene by xTranslate and
        yTranslate, rotated by xRotate, yRotate, and zRotate and scaled.  The siteMap is bounded by
        the upper left corner (left, top) and the lower right corner (left + width, top + height).
        All site maps are drawn in millimeter units, with a scale of 50:1.  That is, 1 mm in the
        siteMap = 50 mm in the real world.  The Maya scene is defined with centimeter units, hence
        one unit in the siteMap equals 5 cm in the scene. While the scale has been uniformly 50:1,
        this value is not hard-coded, but rather regarded a parameter, scale.  The site map has a
        federal coordinates marker, the location of which is given by xFederal and yFederal."""

#===================================================================================================
#                                                                                       C L A S S

    __tablename__ = u'sitemaps'

    _index               = sqla.Column(sqla.Integer,     default=0)
    _name                = sqla.Column(sqla.Unicode,     default=u'')
    _level               = sqla.Column(sqla.Unicode,     default=u'')
    _filename            = sqla.Column(sqla.Unicode,     default=u'')
    _federalEast         = sqla.Column(sqla.Integer,     default=0)
    _federalNorth        = sqla.Column(sqla.Integer,     default=0)
    _left                = sqla.Column(sqla.Float,       default=0.0)
    _top                 = sqla.Column(sqla.Float,       default=0.0)
    _width               = sqla.Column(sqla.Float,       default=0.0)
    _height              = sqla.Column(sqla.Float,       default=0.0)
    _xFederal            = sqla.Column(sqla.Float,       default=0.0)
    _yFederal            = sqla.Column(sqla.Float,       default=0.0)
    _xTranslate          = sqla.Column(sqla.Float,       default=0.0)
    _zTranslate          = sqla.Column(sqla.Float,       default=0.0)
    _xRotate             = sqla.Column(sqla.Float,       default=0.0)
    _yRotate             = sqla.Column(sqla.Float,       default=0.0)
    _zRotate             = sqla.Column(sqla.Float,       default=0.0)
    _scale               = sqla.Column(sqla.Float,       default=1.0)

    _flags               = sqla.Column(sqla.Integer,     default=0)
    _sourceFlags         = sqla.Column(sqla.Integer,     default=0)
    _displayFlags        = sqla.Column(sqla.Integer,     default=0)
    _importFlags         = sqla.Column(sqla.Integer,     default=0)
    _analysisFlags       = sqla.Column(sqla.Integer,     default=0)

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        super(Tracks_SiteMap, self).__init__(**kwargs)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: isReady
    @property
    def isReady(self):
        return False if self.scale == 0.0 else True

#___________________________________________________________________________________________________ GS: uid
    @property
    def uid(self):
        return Base36.to36(self.index)

#___________________________________________________________________________________________________ GS: cache
    @property
    def cache(self):
        """ Caching object used during analysis to store transient data related to this sitemap """
        out = self.fetchTransient('cache')
        if not out:
            out = ConfigsDict()
            self.putTransient('cache', out)
        return out

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getFederalCoordinates
    def getFederalCoordinates(self):
        """ The Swiss federal coordinates associated with the siteMap is returned.  The coordinates
            are in meters relative to a geographical reference point in SE France.  The values of
            the first coordinate ('east') are on the order of 600,000 m and those of the second
            coordinate ('north') are roughly 200,000 m. Note that coordinate values extracted from
            the scene are in centimeters, while these coordinates are in meters. """

        return [self.federalEast, self.federalNorth]

#___________________________________________________________________________________________________ getTracksQuery
    def getTracksQuery(self, session =None):
        """ This method returns an SQLAlchemy query object within the specified session, or a new
            session if none is specified, that can be used to retrieve all tracks within this
            sitemap. """

        from cadence.models.tracks.Tracks_Track import Tracks_Track
        model = Tracks_Track.MASTER

        if not self.filename:
            print('getAllTracks: filename invalid')
            return

        site  = self.name
        level = self.level

        if session is None:
            session = self.mySession

        return session.query(model).filter(model.site == site).filter(model.level == level)

#___________________________________________________________________________________________________ getAllTracks
    def getAllTracks(self, session =None):
        """ This operates on the current siteMap, which is populated with the specifics for a given
            track site.  The three-letter site abbreviation (e.g., BSY, TCH) and the level can be
            parsed the filename, based on the (informal-but-thus-far-valid) naming convention for
            the sitemap file. """

        return self.getTracksQuery(session=session).all()

#___________________________________________________________________________________________________ getTrackways
    def getTrackways(self):
        """getTrackways doc..."""

        from cadence.models.tracks.Tracks_Trackway import Tracks_Trackway
        model = Tracks_Trackway.MASTER
        trackways = self.mySession.query(model).filter(model.siteMapIndex == self.index).all()
        for tw in trackways:
            tw.sitemap = self
        return trackways

#___________________________________________________________________________________________________ GS: getNameFromFilename
    @classmethod
    def getNameFromFilename(cls, filename):
        """ Name of the sitemap as determined by its filename """
        return filename[0:3]

#___________________________________________________________________________________________________ GS: getLevelFromFilename
    @classmethod
    def getLevelFromFilename(cls, filename):
        return filename.partition('_')[-1].rpartition(' ')[0]

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _getAnalysisPair
    def _getAnalysisPair(self, session, createIfMissing):
        """_getAnalysisPair doc..."""

        from cadence.models.analysis.Analysis_Sitemap import Analysis_Sitemap
        model = Analysis_Sitemap.MASTER

        result = session.query(model).filter(model.index == self.index).first()

        if createIfMissing and not result:
            result = model()
            result.index = self.index
            session.add(result)
            session.flush()

        return result

#===================================================================================================
#                                                                               I N T R I N S I C

#___________________________________________________________________________________________________ __str__
    def __str__(self):
        """__str__ doc..."""
        return '<Sitemap[%s | %s] "%s">' % (self.i, self.index, self.filename)
