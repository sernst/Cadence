library(stringr)
library(RSQLite)

generateFingerprints <- function(tracks) {
  return(paste(
    tracks$site, tracks$level, tracks$year, tracks$sector, 
    tracks$trackwayType, tracks$trackwayNumber,
    ifelse(tracks$left, 'L', 'R'),
    ifelse(tracks$pes, 'P', 'M'),
    stringr::str_replace_all(tracks$number, '-', 'N'), sep='-'))
}

getTracksData <- function() {
  # Create a connection to the tracks database and load the tracks database table
  conn <- RSQLite::dbConnect(RSQLite::SQLite(), dbname="input/tracks.vdb")
  tracks <- RSQLite::dbReadTable(conn, "tracks")
  tracks$fingerprint <- generateFingerprints(tracks)
  RSQLite::dbDisconnect(conn)
  return(tracks)
}

getSitemapsData <- function() {
  conn <- RSQLite::dbConnect(RSQLite::SQLite(), dbname="input/tracks.vdb")
  sitemaps <- RSQLite::dbReadTable(conn, "sitemaps")
  RSQLite::dbDisconnect(conn)
  return(sitemaps)
}

getAnalysisTracksData <- function() {
  conn <- RSQLite::dbConnect(RSQLite::SQLite(), dbname="input/analysis.vdb")
  analysisTracks <- RSQLite::dbReadTable(conn, "tracks")
  RSQLite::dbDisconnect(conn)
  return(analysisTracks)
}