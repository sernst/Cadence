# StatusAnalyzer.py
# (C)2014-2015
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

from cadence.analysis.AnalyzerBase import AnalyzerBase
from cadence.analysis.status.OriginCheckStage import OriginCheckStage
from cadence.analysis.status.RotationalUncertaintyStage import RotationalUncertaintyStage
from cadence.analysis.status.SpatialUncertaintyStage import SpatialUncertaintyStage
from cadence.analysis.status.TrackwayLoadStage import TrackwayLoadStage

#*************************************************************************************************** StatusAnalyzer
class StatusAnalyzer(AnalyzerBase):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, **kwargs):
        """Creates a new instance of StatusAnalyzer."""
        super(StatusAnalyzer, self).__init__(**kwargs)
        self.addStage(TrackwayLoadStage('load', self))
        self.addStage(OriginCheckStage('origin', self))
        self.addStage(SpatialUncertaintyStage('spatial-unc', self))
        self.addStage(RotationalUncertaintyStage('rotation-unc', self))

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    StatusAnalyzer().run()
