Constructs and manages transform node based trackway representations in Maya.

Building Trackways
------------------
When starting a new trackway series:

1) Fill out the trackway data (Community, Site, Year, Sector, Level, and Trackway).

2) Push Set Select

2) Add any notes that will associated by default with the series. Note that the notes for
any specific track can be overwritten to annotate any particlar track.

3) push INITIALIZE, and eight initial tracks will be generated (ML1, ML2, PL1, PL2, etc.).  These
constitute the first two for each foot.  Scale, rotate and move them to the first two track
locations for each foot, for the given trackway.

4) select the last track of a track series you wish to extend. Push NEW to create new tracks, one
per button press (e.g., selecting ML2 and clicking the NEW button will create ML3 placing it as
a linear extrapolation based on the displacement of ML2 from ML1.  ML3 will have the rotation
copied from ML2).  Each press of NEW will extend the series.

---

Removing Prints
---------------
A print or prints can be removed from a trackway at any time by selecting the print(s) and clicking
the

 * *Trackway Modifier* -> *Remove*

 button.

---

Navigation
----------
The trackway navigation section allows for easy browsing of trackways using forward and back
navigation as well as footprint information section that shows the relationships for the current
trackway.
