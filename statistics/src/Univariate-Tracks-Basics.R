library(RSQLite)
library(dplyr)
library(ggplot2)

# Create a connection to the tracks database and load the tracks database table
tracksConn <- RSQLite::dbConnect(RSQLite::SQLite(), dbname="input/tracks.vdb")
allTracks <- RSQLite::dbReadTable(tracksConn, "tracks")
RSQLite::dbDisconnect(tracksConn)
tracksConn <- NULL

# Add the fingerprint to the columns of data
allTracks$fingerprint <- paste(
  allTracks$site, allTracks$level, allTracks$year, allTracks$sector, 
  allTracks$trackwayType, allTracks$trackwayNumber,
  ifelse(allTracks$left, 'L', 'R'),
  ifelse(allTracks$pes, 'P', 'M'),
  allTracks$number, sep='-')

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

# Finalized PDF printing
dev.off()