from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

from cadence.analysis.shared import DataLoadUtils

#_______________________________________________________________________________
def plot():
    pass

################################################################################

#_______________________________________________________________________________ _main_
def _main_(args):
    trackways = DataLoadUtils.getTrackwaysWithAnalysis()
    tracks = DataLoadUtils.getTrackWithAnalysis()


#_______________________________________________________________________________ RUN MAIN
if __name__ == '__main__':
    import argparse
    import textwrap
    dedent = textwrap.dedent
    parser = argparse.ArgumentParser()

    parser.description = dedent("""
        Plots trackway statistics figures for SVP talk.""")
    _main_(parser.parse_args())
