library(dplyr)
library(magrittr)
library(ggplot2)

source('src/support/TrackUtils.r')
tracks <- getTracksData() 

widthTracks <- tracks %>% 
  dplyr::filter(widthMeasured > 0) %>%
  dplyr::filter(width > 0) %>%
  dplyr::filter(bitwAnd(importFlags, bitwShiftL(1, 2)) == 0)

lengthTracks <- tracks %>%
  dplyr::filter(lengthMeasured > 0) %>%
  dplyr::filter(length > 0) %>%
  dplyr::filter(bitwAnd(importFlags, bitwShiftL(1, 3)) == 0)

#--------------------------------------------------------------------------------------------------
# WIDTH CALCULATIONS

wMean <- mean(widthTracks$widthMeasured)
wN <- count(widthTracks)$n
wNZero <- count(dplyr::filter(widthTracks, widthTracks$deltaWidth == 0))$n
wNZeroPercent <- 100.0*wNZero/wN

widthTracks$deltaWidth <- (
  widthTracks$width - widthTracks$widthMeasured)/widthTracks$widthMeasured
widthTracks$deltaWidth <- 100.0*widthTracks$deltaWidth
dwMean <- mean(widthTracks$deltaWidth)
dwDev <- sd(widthTracks$deltaWidth)

ggplot2::ggplot(widthTracks, aes(deltaWidth)) + 
  ggplot2::geom_histogram(binwidth=4) + 
  ggplot2::ggtitle('Track Width Measurment Discrepancies') +
  ggplot2::xlab('Fractional Field & Digital Measurement Difference (%)') +
  ggplot2::ylab('Count (#)') +
  ggplot2::xlim(c(-50, 50))

#--------------------------------------------------------------------------------------------------
# LENGTH CALCULATIONS

lMean <- mean(lengthTracks$lengthMeasured)
lN <- count(lengthTracks)$n
lNZero <- count(dplyr::filter(lengthTracks, lengthTracks$deltaLength == 0))$n
lNZeroPercent <- 100.0*lNZero/lN

lengthTracks$deltaLength <- 
  (lengthTracks$length - lengthTracks$lengthMeasured)/lengthTracks$lengthMeasured
lengthTracks$deltaLength <- 100.0*lengthTracks$deltaLength
dlMean <- mean(lengthTracks$deltaLength)
dlDev <- sd(lengthTracks$deltaLength)

ggplot2::ggplot(lengthTracks, aes(deltaLength)) + 
  ggplot2::geom_histogram(binwidth=4) + 
  ggplot2::ggtitle('Track Length Measurment Discrepancies') +
  ggplot2::xlab('Fractional Field & Digital Measurement Difference (%)') +
  ggplot2::ylab('Count (#)') +
  ggplot2::xlim(c(-50, 50))
