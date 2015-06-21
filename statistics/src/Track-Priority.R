library(dplyr)

priorities <- read.csv("/Users/scott/Dropbox/a16/Analysis/StatisticsAnalyzer/Track-Priority.csv")
errors <- read.csv("/Users/scott/Dropbox/a16/Analysis/ComparisonAnalyzer/Error-Deviations.csv")

targets <- dplyr::inner_join(priorities, errors, by=c('UID'))
targets <- dplyr::filter(targets, targets$Preserved == 1 | targets$Cast == 1)

write.csv(targets, 'output/Track_Priorities.csv', sep=",")
