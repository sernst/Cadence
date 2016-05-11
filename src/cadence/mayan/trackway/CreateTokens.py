# CreateTokens.py
# (C)2016
# Kent A. Stevens

from __future__ import\
    print_function, absolute_import, unicode_literals, division

from nimble import NimbleScriptBase

from cadence.mayan.trackway.TrackSceneUtils import TrackSceneUtils

#_______________________________________________________________________________
class CreateTokens(NimbleScriptBase):
    """ This is creates the tokens from a passed list of dictionaries. """

#===============================================================================
#                                                                      C L A S S

    NO_PROPSLIST = u'noPropsList'

#===============================================================================
#                                                                    P U B L I C

#_______________________________________________________________________________
    def run(self, *args, **kwargs):
        """ This fetches the list of props (each a dictionary specifying a
            token) and creates the corresponding tokens in Maya. """

        propsList = self.fetch('propsList', None)
        if not propsList:
            self.putErrorResult(
                u'No list of props specified. Unable to create tokens.',
                code=self.NO_PROPSLIST)
            return

        for props in propsList:
            TrackSceneUtils.createToken(props['uid'], props)

