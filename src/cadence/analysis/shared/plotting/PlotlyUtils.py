# PlotlyUtils.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

import re

PLOTLY_PLOT_NUMBER_REGEX = re.compile('[0-9]+')
PLOTLY_EMBED_URL_PATTERN = 'https://plot.ly/~teradjunct/###.embed'

#_______________________________________________________________________________ __init__
def getPlotlyFilename(filename, folder =None, root ='A16'):
    root = root.strip('/')
    filename = filename.strip('/')
    if folder:
        return '%s/%s/%s' % (root, folder.strip('/'), filename)
    return '%s/%s' % (root, filename)

#_______________________________________________________________________________ toEmbedUrl
def toEmbedUrl(url):
    # https://plot.ly/~teradjunct/759/pes-width-distributions-by-tracksite/

    parts = url.replace('https://plot.ly/', '').strip('/').split('/')
    for p in parts:
        if PLOTLY_PLOT_NUMBER_REGEX.match(p):
            return PLOTLY_EMBED_URL_PATTERN.replace('###', p)
    return url

