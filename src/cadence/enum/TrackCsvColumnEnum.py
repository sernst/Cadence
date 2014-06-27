# TrackCsvColumnEnum.py
# (C)2013-2014
# Scott Ernst

from collections import namedtuple

#___________________________________________________________________________________________________ TRACK_PROP_NT
# A custom data type for track csv column enumerations that contain the following information:
#   * index     | Index of the column within the source spreadsheet
#   * name      | Key for the column. Used by the importer and stored by the database
CSV_COLUMN_NT = namedtuple('TRACK_PROP_NT', ['index', 'name' ])

#___________________________________________________________________________________________________ TrackCsvColumnEnum
class TrackCsvColumnEnum(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

    INDEX                               = CSV_COLUMN_NT(0,  'index')
    TRACKSITE                           = CSV_COLUMN_NT(1,  'tracksite')
    LEVEL                               = CSV_COLUMN_NT(2,  'level')
    TRACKWAY                            = CSV_COLUMN_NT(3,  'trackway')
    SECTOR                              = CSV_COLUMN_NT(4,  'sector')
    ENTRY_AZIMUTH                       = CSV_COLUMN_NT(5,  'entry_azimuth')
    EXIT_AZIMUTH                        = CSV_COLUMN_NT(6,  'exit_azimuth')
    TOTAL_AZIMUTH                       = CSV_COLUMN_NT(7,  'direct_azimuth')
    TRACKWAY_LENGTH                     = CSV_COLUMN_NT(8,  'trackway_length')
    COMMENT                             = CSV_COLUMN_NT(9,  'comment')
    AZIMUTH_DEVIATION                   = CSV_COLUMN_NT(10, 'azimuth_deviation')
    AZIMUTH_MEAN                        = CSV_COLUMN_NT(11, 'azimuth_mean')
    AZIMUTH_MEAN_DEVIATION              = CSV_COLUMN_NT(12, 'azimuth_mean_deviation')
    ORIENTATIONS                        = CSV_COLUMN_NT(13, 'orientations')
    OUTLINE_DRAWING                     = CSV_COLUMN_NT(14, 'outline_drawing')
    SAMPLE                              = CSV_COLUMN_NT(15, 'sample')
    CAST                                = CSV_COLUMN_NT(16, 'cast')
    CAST_NAME                           = CSV_COLUMN_NT(17, 'cast_name')
    CAST_DATE                           = CSV_COLUMN_NT(18, 'cast_date')
    DATA_NAME                           = CSV_COLUMN_NT(19, 'data_name')
    DATA_DATE                           = CSV_COLUMN_NT(20, 'data_date')
    TRACK_NAME                          = CSV_COLUMN_NT(21, 'track_name')
    MISSING                             = CSV_COLUMN_NT(22, 'missing')
    PES_LENGTH                          = CSV_COLUMN_NT(23, 'pes_length')
    PES_LENGTH_GUESS                    = CSV_COLUMN_NT(24, 'pes_length_guess')
    PES_WIDTH                           = CSV_COLUMN_NT(25, 'pes_width')
    PES_WIDTH_GUESS                     = CSV_COLUMN_NT(26, 'pes_width_guess')
    PES_DEPTH                           = CSV_COLUMN_NT(27, 'pes_depth')
    PES_DEPTH_GUESS                     = CSV_COLUMN_NT(28, 'pes_depth_guess')
    LEFT_PES_ROTATION                   = CSV_COLUMN_NT(29, 'left_pes_rotation')
    LEFT_PES_ROTATION_GUESS             = CSV_COLUMN_NT(30, 'left_pes_rotation_guess')
    RIGHT_PES_ROTATION                  = CSV_COLUMN_NT(31, 'right_pes_rotation')
    RIGHT_PES_ROTATION_GUESS            = CSV_COLUMN_NT(32, 'right_pes_rotation_guess')
    MANUS_LENGTH                        = CSV_COLUMN_NT(33, 'manus_length')
    MANUS_LENGTH_GUESS                  = CSV_COLUMN_NT(34, 'manus_length_guess')
    MANUS_WIDTH                         = CSV_COLUMN_NT(35, 'manus_width')
    MANUS_WIDTH_GUESS                   = CSV_COLUMN_NT(36, 'manus_width_guess')
    MANUS_DEPTH                         = CSV_COLUMN_NT(37, 'manus_depth')
    MANUS_DEPTH_GUESS                   = CSV_COLUMN_NT(38, 'manus_depth_guess')
    LEFT_MANUS_ROTATION                 = CSV_COLUMN_NT(39, 'left_manus_rotation')
    LEFT_MANUS_ROTATION_GUESS           = CSV_COLUMN_NT(40, 'left_manus_rotation_guess')
    RIGHT_MANUS_ROTATION                = CSV_COLUMN_NT(41, 'right_manus_rotation')
    RIGHT_MANUS_ROTATION_GUESS          = CSV_COLUMN_NT(42, 'right_manus_rotation_guess')
    PES_STRIDE                          = CSV_COLUMN_NT(43, 'pes_stride')
    PES_STRIDE_GUESS                    = CSV_COLUMN_NT(44, 'pes_stride_guess')
    PES_STRIDE_FACTOR                   = CSV_COLUMN_NT(45, 'pes_stride_factor')
    WIDTH_PES_ANGULATION_PATTERN        = CSV_COLUMN_NT(46, 'width_pes_angulation_pattern')
    WIDTH_PES_ANGULATION_PATTERN_GUESS  = CSV_COLUMN_NT(47, 'width_pes_angulation_pattern_guess')
    LEFT_PES_PACE                       = CSV_COLUMN_NT(48, 'left_pes_pace')
    LEFT_PES_PACE_GUESS                 = CSV_COLUMN_NT(49, 'left_pes_pace_guess')
    LEFT_PES_PROGRESSION                = CSV_COLUMN_NT(50, 'left_pes_progression')
    LEFT_PES_PROGRESSION_GUESS          = CSV_COLUMN_NT(51, 'left_pes_progression_guess')
    RIGHT_PES_PACE                      = CSV_COLUMN_NT(52, 'right_pes_pace')
    RIGHT_PES_PACE_GUESS                = CSV_COLUMN_NT(53, 'right_pes_pace_guess')
    PES_PACE_ANGULATION                 = CSV_COLUMN_NT(54, 'pes_pace_angulation')
    PES_PACE_ANGULATION_GUESS           = CSV_COLUMN_NT(55, 'pes_pace_angulation')
    MANUS_STRIDE                        = CSV_COLUMN_NT(56, 'manus_stride')
    MANUS_STRIDE_GUESS                  = CSV_COLUMN_NT(57, 'manus_stride_guess')
    MANUS_STRIDE_FACTOR                 = CSV_COLUMN_NT(58, 'manus_stride_factor')
    WIDTH_MANUS_ANGULATION_PATTERN      = CSV_COLUMN_NT(59, 'width_manus_angulation_pattern')
    WIDTH_MANUS_ANGULATION_PATTERN_GUESS= CSV_COLUMN_NT(60, 'width_manus_angulation_pattern_guess')
    LEFT_MANUS_PACE                     = CSV_COLUMN_NT(61, 'left_manus_pace')
    LEFT_MANUS_PACE_GUESS               = CSV_COLUMN_NT(62, 'left_manus_pace_guess')
    LEFT_MANUS_PROGRESSION              = CSV_COLUMN_NT(63, 'left_manus_progression')
    LEFT_MANUS_PROGRESSION_GUESS        = CSV_COLUMN_NT(64, 'left_manus_progression_guess')
    RIGHT_MANUS_PACE                    = CSV_COLUMN_NT(65, 'right_manus_pace')
    RIGHT_MANUS_PACE_GUESS              = CSV_COLUMN_NT(66, 'right_manus_pace_guess')
    RIGHT_MANUS_PROGRESSION             = CSV_COLUMN_NT(67, 'right_manus_progression')
    RIGHT_MANUS_PROGRESSION_GUESS       = CSV_COLUMN_NT(68, 'right_manus_progression_guess')
    MANUS_PACE_ANGULATION               = CSV_COLUMN_NT(69, 'manus_pace_angulation')
    MANUS_PACE_ANGULATION_GUESS         = CSV_COLUMN_NT(70, 'manus_pace_angulation_guess')
    GLENO_ACETABULAR_DISTANCE           = CSV_COLUMN_NT(71, 'gleno_acetabular_distance')
    GLENO_ACETABULAR_DISTANCE_GUESS     = CSV_COLUMN_NT(72, 'gleno_acetabykar_distance_guess')
    ANATOMICAL_DETAILS                  = CSV_COLUMN_NT(73, 'anatomical_details')
