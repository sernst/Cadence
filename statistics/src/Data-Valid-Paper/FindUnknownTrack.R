library(dplyr)
library(magrittr)
library(ggplot2)

source('src/support/TrackUtils.r')
tracks <- getTracksData()

WIDTH_TARGET <- 0.37
LENGTH_TARGET <- 0.44

bebTracks <- dplyr::filter(tracks, tracks$site == 'BEB' & tracks$level == '515') %>%
  dplyr::filter(width > 0 & length > 0) %>%
  dplyr::filter(widthMeasured > 0 & lengthMeasured > 0)

bebTracks$ranking <- sqrt(
  (bebTracks$width - WIDTH_TARGET)^2 +
  (bebTracks$length - LENGTH_TARGET)^2 +
  (bebTracks$widthMeasured - WIDTH_TARGET)^2 +
  (bebTracks$lengthMeasured - LENGTH_TARGET)^2)

ggplot2::ggplot(bebTracks, aes(ranking)) + ggplot2::geom_histogram()

bebTracks <- dplyr::filter(bebTracks, bebTracks$ranking)
write.csv(result, 'output/Unknown-Track-Matches.csv')
