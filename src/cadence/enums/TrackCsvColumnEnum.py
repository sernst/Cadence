# TrackCsvColumnEnum.py
# (C)2013-2014
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from collections import namedtuple

#_______________________________________________________________________________
# A custom data type for track csv column enumerations that contain the following information:
#   * index     | Index of the column within the source spreadsheet
#   * name      | Key for the column. Used by the importer and stored by the database
CSV_COLUMN_NT = namedtuple('TRACK_PROP_NT', ['index', 'name', 'snapshot' ])

#_______________________________________________________________________________
class TrackCsvColumnEnum(object):
    """A class for..."""

#===============================================================================
#                                                                                       C L A S S

    """ Row index within the spreadsheet file where the entry is found. This value can change any
        time a new import process occurs and represents the location in the most recent spreadsheet
        file. It should only be used for reference given that the value can arbitrarily change. """
    INDEX = CSV_COLUMN_NT(0, 'index', False)

    """ The short name of the track site where the print resides, e.g. BEB.
        Always 3 upper case letters"""
    TRACKSITE = CSV_COLUMN_NT(1, 'tracksite', False)

    """ The level within the track site specifying the excavation depth where the track resided.
        Lower numbers are deeper in the excavation and are therefore older. """
    LEVEL = CSV_COLUMN_NT(2, 'level', False)

    """ Represents the trackway type, e.g. S for Sauropod, and the trackway number within the
        tracksite and level. Suffices can include 'bis' for a trackway that was broken but could
        be a continuation of the previous version. """
    TRACKWAY = CSV_COLUMN_NT(3, 'trackway', False)

    """ The excavation area within the tracksite where the track was found. """
    SECTOR = CSV_COLUMN_NT(4, 'sector', False)

    """ CATALOG ONLY: Entry angle for the trackway as measured by the Illustrator file. """
    ENTRY_AZIMUTH = CSV_COLUMN_NT(5, 'entry_azimuth', False)

    """ CATALOG ONLY: Exit angle for the trackway as measured by the Illustrator file. """
    EXIT_AZIMUTH = CSV_COLUMN_NT(6, 'exit_azimuth', False)

    """ CATALOG ONLY: Information that specifies the total orientation """
    TOTAL_AZIMUTH = CSV_COLUMN_NT(7, 'direct_azimuth', False)

    """ CATALOG ONLY: Trackway length as measured by the illustrator file. """
    TRACKWAY_LENGTH = CSV_COLUMN_NT(8, 'trackway_length', False)

    """ CATALOG ONLY: Illustrator file measurement. """
    COMMENT = CSV_COLUMN_NT(9, 'comment', False)

    """ CATALOG ONLY: Illustrator file measurement. """
    AZIMUTH_DEVIATION = CSV_COLUMN_NT(10, 'azimuth_deviation', False)

    """ CATALOG ONLY: Illustrator file measurement. """
    AZIMUTH_MEAN = CSV_COLUMN_NT(11, 'azimuth_mean', False)

    """ CATALOG ONLY: Illustrator file measurement. """
    AZIMUTH_MEAN_DEVIATION = CSV_COLUMN_NT(12, 'azimuth_mean_deviation', False)

    """ CATALOG ONLY: Categorical reference for track types, such as straight, curved, etc. """
    ORIENTATIONS = CSV_COLUMN_NT(13, 'orientations', False)

    """ Reference material exists for a plastic sheet drawing at 1:1 for the track. """
    OUTLINE_DRAWING = CSV_COLUMN_NT(14, 'outline_drawing', True)

    """ Reference material of the original print exists in the collection. """
    PRESERVED = CSV_COLUMN_NT(15, 'preserved', True)

    """ Reference material exist as a cast in the collection. """
    CAST = CSV_COLUMN_NT(16, 'cast', True)

    """ Initials of the person or people who took the data. """
    MEASURED_BY = CSV_COLUMN_NT(17, 'measured_by', True)

    """ The date when the print was measured in the field. """
    MEASURED_DATE = CSV_COLUMN_NT(18, 'measured_date', True)

    """ Name of person in the office that took the measured data and entered. """
    DATA_ENTERED_BY = CSV_COLUMN_NT(19, 'data_entered_by', False)

    """ The date the measured data was entered in the computer. """
    DATA_ENTRY_DATE = CSV_COLUMN_NT(20, 'data_entry_date', False)

    """ The name of the track within. """
    TRACK_NAME = CSV_COLUMN_NT(21, 'track_name', False)

    """ A fictional possible track to explain missing. """
    MISSING = CSV_COLUMN_NT(22, 'missing', False)

    """ Fundamental track measurements made in the field """
    PES_LENGTH = CSV_COLUMN_NT(23, 'pes_length', False)
    PES_LENGTH_GUESS = CSV_COLUMN_NT(24, 'pes_length_guess', False)

    PES_WIDTH = CSV_COLUMN_NT(25, 'pes_width', False)
    PES_WIDTH_GUESS = CSV_COLUMN_NT(26, 'pes_width_guess', False)

    PES_DEPTH = CSV_COLUMN_NT(27, 'pes_depth', False)
    PES_DEPTH_GUESS = CSV_COLUMN_NT(28, 'pes_depth_guess', False)

    MANUS_LENGTH = CSV_COLUMN_NT(33, 'manus_length', False)
    MANUS_LENGTH_GUESS = CSV_COLUMN_NT(34, 'manus_length_guess', False)

    MANUS_WIDTH = CSV_COLUMN_NT(35, 'manus_width', False)
    MANUS_WIDTH_GUESS = CSV_COLUMN_NT(36, 'manus_width_guess', False)

    MANUS_DEPTH = CSV_COLUMN_NT(37, 'manus_depth', False)
    MANUS_DEPTH_GUESS = CSV_COLUMN_NT(38, 'manus_depth_guess', False)

    """ Rotation (in degrees) measured locally using center-to-center track segments as the 0 line.
        Positive values indicate outward rotation and negative values inward relative the body. """
    LEFT_PES_ROTATION = CSV_COLUMN_NT(29, 'left_pes_rotation', False)
    LEFT_PES_ROTATION_GUESS = CSV_COLUMN_NT(30, 'left_pes_rotation_guess', False)

    RIGHT_PES_ROTATION = CSV_COLUMN_NT(31, 'right_pes_rotation', False)
    RIGHT_PES_ROTATION_GUESS = CSV_COLUMN_NT(32, 'right_pes_rotation_guess', False)

    LEFT_MANUS_ROTATION = CSV_COLUMN_NT(39, 'left_manus_rotation', False)
    LEFT_MANUS_ROTATION_GUESS = CSV_COLUMN_NT(40, 'left_manus_rotation_guess', False)

    RIGHT_MANUS_ROTATION = CSV_COLUMN_NT(41, 'right_manus_rotation', False)
    RIGHT_MANUS_ROTATION_GUESS = CSV_COLUMN_NT(42, 'right_manus_rotation_guess', False)

    """ Center-to-center measurement between successive prints. If a track or more were missing the
        measurement was made to the next available track and then divided by the interpretation of
        the number of missing tracks as defined by the stride factor. """
    PES_STRIDE = CSV_COLUMN_NT(43, 'pes_stride', False)
    PES_STRIDE_GUESS = CSV_COLUMN_NT(44, 'pes_stride_guess', False)
    PES_STRIDE_FACTOR = CSV_COLUMN_NT(45, 'pes_stride_factor', False)

    MANUS_STRIDE = CSV_COLUMN_NT(58, 'manus_stride', False)
    MANUS_STRIDE_GUESS = CSV_COLUMN_NT(59, 'manus_stride_guess', False)
    MANUS_STRIDE_FACTOR = CSV_COLUMN_NT(60, 'manus_stride_factor', False)

    """ WAP & WAM as measured in the field according to Daniel's thesis in Figure 2.11. """
    WIDTH_PES_ANGULATION_PATTERN = CSV_COLUMN_NT(46, 'width_pes_angulation_pattern', False)
    WIDTH_PES_ANGULATION_PATTERN_GUESS = CSV_COLUMN_NT(47, 'width_pes_angulation_pattern_guess', False)

    WIDTH_MANUS_ANGULATION_PATTERN = CSV_COLUMN_NT(61, 'width_manus_angulation_pattern', False)
    WIDTH_MANUS_ANGULATION_PATTERN_GUESS = CSV_COLUMN_NT(62, 'width_manus_angulation_pattern_guess', False)

    """ Diagonal distance between the track and the corresponding next track on the opposite side
        of the body/trackway."""
    LEFT_PES_PACE = CSV_COLUMN_NT(48, 'left_pes_pace', False)
    LEFT_PES_PACE_GUESS = CSV_COLUMN_NT(49, 'left_pes_pace_guess', False)

    RIGHT_PES_PACE = CSV_COLUMN_NT(52, 'right_pes_pace', False)
    RIGHT_PES_PACE_GUESS = CSV_COLUMN_NT(53, 'right_pes_pace_guess', False)

    LEFT_MANUS_PACE = CSV_COLUMN_NT(63, 'left_manus_pace', False)
    LEFT_MANUS_PACE_GUESS = CSV_COLUMN_NT(64, 'left_manus_pace_guess', False)

    RIGHT_MANUS_PACE = CSV_COLUMN_NT(67, 'right_manus_pace', False)
    RIGHT_MANUS_PACE_GUESS = CSV_COLUMN_NT(68, 'right_manus_pace_guess', False)

    """ Angle in degrees of successive pace measurements between tracks. """
    PES_PACE_ANGULATION = CSV_COLUMN_NT(56, 'pes_pace_angulation', False)
    PES_PACE_ANGULATION_GUESS = CSV_COLUMN_NT(57, 'pes_pace_angulation_guess', False)

    MANUS_PACE_ANGULATION = CSV_COLUMN_NT(71, 'manus_pace_angulation', False)
    MANUS_PACE_ANGULATION_GUESS = CSV_COLUMN_NT(72, 'manus_pace_angulation_guess', False)

    """ A calculated measurement """
    LEFT_PES_PROGRESSION = CSV_COLUMN_NT(50, 'left_pes_progression', False)
    LEFT_PES_PROGRESSION_GUESS = CSV_COLUMN_NT(51, 'left_pes_progression_guess', False)

    RIGHT_PES_PROGRESSION = CSV_COLUMN_NT(54, 'right_pes_progression', False)
    RIGHT_PES_PROGRESSION_GUESS = CSV_COLUMN_NT(55, 'right_pes_progression_guess', False)

    LEFT_MANUS_PROGRESSION = CSV_COLUMN_NT(65, 'left_manus_progression', False)
    LEFT_MANUS_PROGRESSION_GUESS = CSV_COLUMN_NT(66, 'left_manus_progression_guess', False)

    RIGHT_MANUS_PROGRESSION = CSV_COLUMN_NT(69, 'right_manus_progression', False)
    RIGHT_MANUS_PROGRESSION_GUESS = CSV_COLUMN_NT(70, 'right_manus_progression_guess', False)

    """ Measurement as described in Daniel's thesis in figure 2.13. """
    GLENO_ACETABULAR_DISTANCE = CSV_COLUMN_NT(73, 'gleno_acetabular_distance', False)
    GLENO_ACETABULAR_DISTANCE_GUESS = CSV_COLUMN_NT(74, 'gleno_acetabular_distance_guess', False)

    """ CATALOG ONLY: Comments about toe, claw, etc. impressions in the print. """
    ANATOMICAL_DETAILS = CSV_COLUMN_NT(75, 'anatomical_details', False)
