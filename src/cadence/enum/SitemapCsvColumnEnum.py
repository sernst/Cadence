# SitemapCsvColumnEnum.py
# (C)2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from collections import namedtuple

#___________________________________________________________________________________________________ TRACK_PROP_NT
# A custom data type for sitemap csv column enumerations that contain the following information:
#   * index     | Index of the column within the source spreadsheet
#   * name      | Key for the column. Used by the importer and stored by the database
SITEMAP_PROP_NT = namedtuple('SITEMAP_PROP_NT', ['index', 'name'])

#___________________________________________________________________________________________________ SitemapCsvColumnEnum
class SitemapCsvColumnEnum(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    """ A unique decimal index that identifies the sitemap when referenced within the database. """
    INDEX = SITEMAP_PROP_NT(0, 'index')

    """ The name of the Adobe Illustrator file represented by the siteMap. """
    FILENAME = SITEMAP_PROP_NT(1, 'filename')

    FEDERAL_EAST = SITEMAP_PROP_NT(2, 'federal_east')

    FEDERAL_NORTH = SITEMAP_PROP_NT(3, 'federal_north')

    LEFT = SITEMAP_PROP_NT(4, 'left')

    TOP = SITEMAP_PROP_NT(5, 'top')

    WIDTH = SITEMAP_PROP_NT(6, 'width')

    HEIGHT = SITEMAP_PROP_NT(7, 'height')

    FEDERAL_X = SITEMAP_PROP_NT(8, 'federal_x')

    FEDERAL_Y = SITEMAP_PROP_NT(9, 'federal_y')

    TRANSLATE_X = SITEMAP_PROP_NT(10, 'translate_x')

    TRANSLATE_Z = SITEMAP_PROP_NT(11, 'translate_z')

    ROTATE_X = SITEMAP_PROP_NT(12, 'rotate_x')

    ROTATE_Y = SITEMAP_PROP_NT(13, 'rotate_y')

    ROTATE_Z = SITEMAP_PROP_NT(14, 'rotate_z')

    SCALE = SITEMAP_PROP_NT(15, 'scale')
