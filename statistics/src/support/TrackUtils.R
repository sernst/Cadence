library(stringr)

generateFingerprints <- function(tracks) {
  return(paste(
    tracks$site, tracks$level, tracks$year, tracks$sector, 
    tracks$trackwayType, tracks$trackwayNumber,
    ifelse(tracks$left, 'L', 'R'),
    ifelse(tracks$pes, 'P', 'M'),
    stringr::str_replace_all(tracks$number, '-', 'N'), sep='-'))
}