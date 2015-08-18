library(dplyr)
library(ggplot2)

PATH <- "/Users/scott/Dropbox/a16/Analysis/StatisticsAnalyzer/Trackway-Stats.csv"
df <- read.csv(PATH)

ggplot(df, aes(Index, Normalize.Density)) + geom_point()