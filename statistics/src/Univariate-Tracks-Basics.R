library(RSQLite)

# Create a connection to the tracks database and load the tracks database table
tracksConn <- RSQLite::dbConnect(RSQLite::SQLite(), dbname="input/tracks.vdb")
tracks <- RSQLite::dbReadTable(tracksConn, "tracks")
head(tracks)

manusTracks = tracks[which(tracks$pes == FALSE), ]
pesTracks = tracks[which(tracks$pes == TRUE), ]

# [PLOT]: Length vs Width
pdf("output/Length-by-Width.pdf", useDingbats=FALSE)
plot(pesTracks$length ~ pesTracks$width)
plot(manusTracks$length ~ manusTracks$width)

# Finalized PDF printing
dev.off()

