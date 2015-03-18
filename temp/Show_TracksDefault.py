from __future__ import print_function, absolute_import, unicode_literals, division

import sqlalchemy as sqla

class Track(ModelsBase):

    __tablename__  = 'tracks'

    i                   = sqla.Column(sqla.Integer,     primary_key=True)
    uid                 = sqla.Column(sqla.Unicode,     default='')
    site                = sqla.Column(sqla.Unicode,     default='')
    year                = sqla.Column(sqla.Unicode,     default='')
    level               = sqla.Column(sqla.Unicode,     default='')
    sector              = sqla.Column(sqla.Unicode,     default='')
    trackwayType        = sqla.Column(sqla.Unicode,     default='')
    trackwayNumber      = sqla.Column(sqla.Unicode,     default='')
    number              = sqla.Column(sqla.Unicode,     default='')

    next                = sqla.Column(sqla.Unicode,     default='')
    left                = sqla.Column(sqla.Boolean,     default=True)
    pes                 = sqla.Column(sqla.Boolean,     default=True)

    width               = sqla.Column(sqla.Float,       default=0.0)
    widthUncertainty    = sqla.Column(sqla.Float,       default=3.0)
    length              = sqla.Column(sqla.Float,       default=0.0)
    lengthUncertainty   = sqla.Column(sqla.Float,       default=3.0)
    rotation            = sqla.Column(sqla.Float,       default=0.0)
    rotationUncertainty = sqla.Column(sqla.Float,       default=5.0)
    x                   = sqla.Column(sqla.Float,       default=0.0)
    z                   = sqla.Column(sqla.Float,       default=0.0)

    fieldWidth          = sqla.Column(sqla.Float,       default=0.0)
    fieldLength         = sqla.Column(sqla.Float,       default=0.0)
    fieldRotation       = sqla.Column(sqla.Float,       default=0.0)

    def getPreviousTrack(self):
        model = self.__class__

        return self.mySession.query(model).filter(model.next == self.uid).first()

    def getNextTrack(self):
        model = self.__class__
        return self.mySession.query(self).filter(model.uid == self.next).first()
