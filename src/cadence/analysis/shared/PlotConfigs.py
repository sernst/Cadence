# configs.py
# (C)2015
# Scott Ernst

from __future__ import \
    print_function, absolute_import, \
    unicode_literals, division

COLORS = [
    'rgb(141,211,199)',
    'rgb(188,128,189)',
    'rgb(190,186,218)',
    'rgb(251,128,114)',
    'rgb(128,177,211)',
    'rgb(253,180,98)',
    'rgb(179,222,105)',
    'rgb(252,205,229)',
    'rgb(217,217,217)' ]

SIZE_CLASSES = [
    dict(
        id='t',
        index=0,
        range=(0, 0.25),
        name='Tiny',
        color=COLORS[0]),
    dict(
        id='s',
        index=1,
        range=(0.25, 0.50),
        name='Small',
        color=COLORS[1]),
    dict(
        id='m',
        index=2,
        range=(0.5, 0.75),
        name='Medium',
        color=COLORS[2]),
    dict(
        id='l',
        index=3,
        range=(0.75, 100.0),
        name='Large',
        color=COLORS[3]) ]

SITE_SPECS = dict(
    CRO=dict(
        color=COLORS[0]),
    CRT=dict(
        color=COLORS[1]),
    BEB=dict(
        color=COLORS[2]),
    BSY=dict(
        color=COLORS[3]),
    PMM=dict(
        color=COLORS[4]),
    SCR=dict(
        color=COLORS[5]),
    TCH=dict(
        color=COLORS[6]),
    CPP=dict(
        color=COLORS[7]),
    OFF=dict(
        color=COLORS[8]))
