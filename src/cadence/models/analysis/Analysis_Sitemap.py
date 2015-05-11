# Analysis_Sitemap.py
# (C)2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import sqlalchemy as sqla

from cadence.models.analysis.AnalysisDefault import AnalysisDefault

#___________________________________________________________________________________________________ Analysis_Sitemap
class Analysis_Sitemap(AnalysisDefault):
    """ Doc... """

#===================================================================================================
#                                                                                       C L A S S

    __tablename__ = 'sitemap'

    _index = sqla.Column(sqla.Integer,     default=0)



