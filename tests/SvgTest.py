# SvgTest.py
# (C)2012-2014
# Kent A. Stevens and Scott Ernst
# test of SvgWriter and Tracks_SiteMap

# from cadence.models.tracks.Tracks_Track import Tracks_Track
# from cadence.models.tracks.Tracks_SiteMap import Tracks_SiteMap
from cadence.svg.SvgWriter import SvgWriter

# model   = Tracks_SiteMap.MASTER
# session = Tracks_Track.MASTER.createSession()
# map     = session.query(model).filter(model.index == 1).first()

# print "map.index = %s and map.name = %s" % (map.index, map.name)

map = None

writer = SvgWriter('test.svg', map)

writer.rect(10, 10, 4, 4)
writer.circle(20, 10, 4)
writer.ellipse(40, 10, 2, 4)
writer.text("test", 60, 10)
writer.save()


