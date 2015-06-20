library(RSQLite)
library(dplyr)
library(ggplot2)

source('src/support/TrackUtils.R')

# Create a connection to the tracks database and load the tracks database table
conn <- RSQLite::dbConnect(RSQLite::SQLite(), dbname="input/tracks.vdb")
sitemaps <- RSQLite::dbReadTable(conn, "sitemaps")
sourceTracks <- RSQLite::dbReadTable(conn, "tracks")
RSQLite::dbDisconnect(conn)

conn <- RSQLite::dbConnect(RSQLite::SQLite(), dbname="input/analysis.vdb")
analysisTracks <- RSQLite::dbReadTable(conn, "tracks")
RSQLite::dbDisconnect(conn)
conn <- NULL

allTracks <- dplyr::inner_join(sourceTracks, analysisTracks, by=c('uid'))

# Add the fingerprint to the columns of data
allTracks$fingerprint <- generateFingerprints(allTracks)

# Modify the tracks table for analysis
hidden <- dplyr::filter(allTracks, allTracks$hidden == 1)
incomplete <- dplyr::filter(allTracks, bitwAnd(allTracks$sourceFlags, 1) == 0)
tracks <- dplyr::setdiff(allTracks, hidden)

# Grab non-hidden tracks that 
zeroTracks <- dplyr::filter(allTracks, allTracks$width == 0.0 | allTracks$length == 0.0)

tracks <- dplyr::setdiff(tracks, zeroTracks)

manusTracks <- tracks[which(tracks$pes == FALSE), ]
pesTracks <- tracks[which(tracks$pes == TRUE), ]

# [PLOT]: Length vs Width
pdf("output/Length-by-Width.pdf", useDingbats=FALSE)
ggplot(pesTracks, aes(width, length)) + geom_point()
ggplot(manusTracks, aes(width, length)) + geom_point()
ggplot(allTracks, aes(strideLength, paceLength)) + geom_point()
ggplot(allTracks, aes(strideLength, simpleGauge)) + geom_point()

# Finalized PDF printing
dev.off()