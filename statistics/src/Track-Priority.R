library(dplyr)

priorities <- read.csv("/Users/scott/Dropbox/a16/Analysis/StatisticsAnalyzer/Track-Priority.csv")
errors <- read.csv("/Users/scott/Dropbox/a16/Analysis/ComparisonAnalyzer/Error-Deviations.csv")
errors <- dplyr::select(errors, -Fingerprint)

# Create a connection to the tracks database and load the tracks database table
conn <- RSQLite::dbConnect(RSQLite::SQLite(), dbname="input/tracks.vdb")
sitemaps <- RSQLite::dbReadTable(conn, "sitemaps")
sourceTracks <- RSQLite::dbReadTable(conn, "tracks")
RSQLite::dbDisconnect(conn)

subsetTracks <- sourceTracks[c(
  'uid', 'pes',
  'width', 'widthMeasured',
  'length', 'lengthMeasured',
  'widthUncertainty', 'lengthUncertainty')]
subsetTracks <- dplyr::filter(subsetTracks, subsetTracks$width > 0 & subsetTracks$length > 0)

sameTracks <- dplyr::filter(subsetTracks, 
  subsetTracks$widthMeasured > 0 &
  subsetTracks$lengthMeasured > 0 &
  subsetTracks$widthMeasured == subsetTracks$lengthMeasured)
sameTracks <- dplyr::inner_join(sameTracks, priorities, by=c('uid' = 'UID'))
sameTracks$delta <- abs(sameTracks$width - sameTracks$length)
sameTracks <- dplyr::filter(sameTracks, sameTracks$delta > 0)

averageWidth <- mean(subsetTracks$width)
averageLength <- mean(subsetTracks$length)

manusTracks <- dplyr::filter(subsetTracks, subsetTracks$pes == 0)
manusTracks$widthDelta <- ifelse(
  manusTracks$widthMeasured == 0, 0,
  abs(manusTracks$width - averageWidth)/manusTracks$widthUncertainty)
manusTracks$widthDelta <- manusTracks$widthDelta/max(manusTracks$widthDelta)

manusTracks$lengthDelta <- ifelse(
  manusTracks$lengthMeasured == 0, 0,
  abs(manusTracks$length - averageLength)/manusTracks$lengthUncertainty)
manusTracks$lengthDelta <- manusTracks$lengthDelta/max(manusTracks$lengthDelta)

pesTracks <- dplyr::filter(subsetTracks, subsetTracks$pes == 1)
pesTracks$widthDelta <- ifelse(
  pesTracks$widthMeasured == 0, 0,
  abs(pesTracks$width - averageWidth)/pesTracks$widthUncertainty)
pesTracks$widthDelta <- 2.0*pesTracks$widthDelta/max(pesTracks$widthDelta)

pesTracks$lengthDelta <- ifelse(
  pesTracks$lengthMeasured == 0, 0,
  abs(pesTracks$length - averageLength)/pesTracks$lengthUncertainty)
pesTracks$lengthDelta <- pesTracks$lengthDelta/max(pesTracks$lengthDelta)

subsetTracks <- rbind(pesTracks, manusTracks)

TRACK_LENGTH_WEIGHT <- 1.0
WIDTH_WEIGHT <- 2.5
LENGTH_WEIGHT <- 2.0

targets <- dplyr::inner_join(priorities, errors, by=c('UID'))
#targets <- dplyr::filter(targets, targets$Preserved == 1 | targets$Cast == 1)
targets <- dplyr::inner_join(targets, subsetTracks, by=c('UID' = 'uid'))
targets$Priority <- targets$Priority/max(targets$Priority)
targets$Priority <- (targets$Width.Deviation + targets$Length.Deviation)*(
  TRACK_LENGTH_WEIGHT*targets$Priority +
  WIDTH_WEIGHT*targets$lengthDelta +
  LENGTH_WEIGHT*targets$widthDelta)
targets$Priority <- targets$Priority/max(targets$Priority)
targets <- dplyr::arrange(targets, dplyr::desc(targets$Priority))

write.csv(targets, 'output/Track_Priorities.csv')
