Constructs and manages transform node based trackway representations in Maya.

The basic unit is a Track, which is visualized as an oriented disk, colored to indicate manus/pes
(light/dark gray disk color) and left/right (red/green triangular orientation indicator), as
inferred from its name (e.g., LM2).  Change the name and the colors will change accordingly.

A 'trackway' is comprised of four 'track series', each of which is a sequential ordering of tracks
typically starting with '1', e.g., 'LP1".  Note that the A16 catalog does not necessarily start with
'1' for all track series.  The catalog has entries for obviously missing tracks, which are not
visualized in Maya.  Missing tracks are reflected in gaps in the numbering as entered from the
catalog or .ai files.

Select a track marker in the Maya scene and push 'Refresh' to update the UI.  Select any number of
track markers for a given trackway, then change any property.

Uncertainty is associated with the width, length and rotation of each track.  This uncertainty
also accounts for positional uncertainty as the placement of the foot is increasingly uncertain
as the width, length, or orientation uncertainty increases (due to slippage either lateral or
along the length of the trackway or by rotation).  Given a nominal size for the foot (either manus
or pes) the positional uncertainty is bounded by the dimensions of the ellipse of the given track
relative to the center of the ellipse.


Building Trackways
------------------
When starting a new trackway series:

1) Push 'Initialize Trackway'. This will create the first two tracks for each of the four feet
(LP1, RP1, LP2, RP2 for the pes and LM1, RM1, LM2, and RM2 for the manus).  They are then selected
and ready to use.

2) Fill out the trackway properties (Community, Site, Year, Sector, Level, and Trackway) and push
'Set Selected Tracks' to apply those properties to the inital eight tracks. They are given initial
values of width, length and rotation. Note that any text notes to be associated with the trackway
the series will be applied to all subsequent tracks for that series.

3) Next, select on of the track pairs for a given foot (e.g., (ML1 and ML2) and place them on the
corresponding first two track locations.  Scale and rotate using Maya, then press 'Add Track' to
continue with that series.  Each additional track is numbered sequentially, but the numbering may
have to be modified to match the trackway (where gaps have occurred due to missing tracks).


Selecting Tracks
----------------

If a track marker is selected in Maya, it is necessary to press 'Refresh' to update the UI.  Once
a track is selected, one can then navigate forward and backwards (and jump to the first and last
tracks of a given series) by buttons 'First Track', 'Prev Track', 'Next Track', and 'Last Track'.
Note that the UI is updated with each next track.

Relative to a given track one can select all tracks up to but not including that track by 'Select
Prior Tracks' or from next to the end of the series by 'Select Later Tracks' or the entire series
by 'Select Track Series'. Finally, "Select All Tracks" selects all tracks in the Maya scene, as
useful for exporting.


Modifying Track Series
----------------------
A track or tracks can be removed from a trackway at any time by selecting those track(s) in Maya
and pushing 'Delete Selected Tracks'.  The order of tracks within a series can be modified by first
selecting those to be reordered, pressing 'Unlink Selected Tracks' then selecting one just before,
then the tracks in the new order of placement, and follow by one just after, then push 'Link
Selected Tracks'.  Confirm by then navigating to previous and next tracks.

A number of tracks can be selected and renamed consecutively by selecting them in the desired order
then entering the new track name for the first track in the sequence and pressing 'Rename Selected
Tracks'.


