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
pdf("output/Track-Basics.pdf", useDingbats=FALSE)
ggplot(pesTracks, aes(width, length)) + geom_point()
ggplot(manusTracks, aes(width, length)) + geom_point()
ggplot(tracks, aes(strideLength, paceLength)) + geom_point()
ggplot(tracks, aes(strideLength, simpleGauge)) + geom_point()
ggplot(tracks, aes(width, strideLength)) + geom_point()
ggplot(tracks, aes(width, simpleGauge)) + geom_point()
ggplot(tracks, aes(width)) + geom_histogram()

# Finalized PDF printing
dev.off()

columnsToKeep <- c('width', 'rotation', 'strideLength', 'paceLength', 'headingAngle', 'simpleGauge')
subsetTracks <- tracks[c('uid', columnsToKeep)]
subsetTracks <- na.omit(subsetTracks)
clusterTracks <- scale(subsetTracks[columnsToKeep])

wss <- (nrow(clusterTracks)-1)*sum(apply(clusterTracks,2,var))
for (i in 2:15) wss[i] <- sum(kmeans(clusterTracks, centers=i)$withinss)
plot.new()
plot(1:15, wss, type="b", xlab="Number of Clusters", ylab="Within groups sum of squares")

fit <- kmeans(clusterTracks, 5)
aggregate(clusterTracks,by=list(fit$cluster),FUN=mean)
subsetTracks <- data.frame(subsetTracks, fit$cluster)

plot.new()
plot(fit[c("strideLength", "simpleGauge")], col=fit$cluster)
points(fit$centers[,c("strideLength", "simpleGauge")], col=1:5, pch=8, cex=2)

result <- subsetTracks[c('uid', 'fit.cluster')]
result <- dplyr::select(result, uid, cluster = fit.cluster)
write.csv(result, 'output/Clustered-Tracks.csv')

