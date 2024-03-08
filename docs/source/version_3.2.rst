.. _version_3.2:
version 3.2 changes
*******************



0. Initial rolling bugfix release
=================================

 Initial rolling bugfix release


::

    Done



1. cfp.bfill_ugrid - code not checking for no points returned from np.where
===========================================================================

Code didn't check for no points returned from a where statement causing a crash in certain circumstances.


::

   Fixed
   
   
   
2. cfp.bfill_ugrid - update for shapely 2.0
===========================================

Update shapely polygon coordinate extraction so code will work with shapely 2.0 +:
# Original method for shapely < 2.0
#coords = geom_cyl[0].exterior.coords[:]

# New method for shapely 2.0 +
poly_mapped = sgeom.mapping(geom_cyl.geoms[0])
coords = list(poly_mapped['coordinates'][0])
 

::

   Fixed  
   


3. cfp.con - line_labels not honoured
=====================================

cfp.con : line_labels were not honoured.


::

   Fixed



4. cfp.levs - need all of min, max and step to define a set of contour levels 
=============================================================================

cfp.levs - need all of min, max and step to define a set of contour levels 


::

   Fixed
   
   
   
5.  cfp.cbar : error when position is specified
===============================================

cfp.cbar : error when position is specified


::

   Fixed
   
  
  
6. cfp.dim_titles - titles and plot positioning issues fixed
============================================================

cfp.dim_titles - titles and plot positioning issues were fixed.


::

   Fixed



7. cfp.stipple - not working for Robinson projection
====================================================
   
cfp.stipple wasn't working for the Robinson projection.


::

   Fixed
   


8. cfp.titles - auxiliary axes sometimes caused an issue
========================================================

cfp-titles - auxiliary axes sometimes caused an issue.


::

   Fixed



9. cfp.mapset - when a cyl mapset is done the colour scale should be relevant for the area selected 
===================================================================================================

cfp.mapset - when a cyl mapset is done the colour scale should be relevant for the area selected.
 
 
::

  Changed
   
   
   
10. cfp.levs - need all of min, max and step to define a set of contour levels
==============================================================================

A new check was put into cfp.levs requiring all of min, max and step to define a set of contour levels.


::

   Changed


11. cfp.titles - plot labelling too far to the right for contour and vector plots
=================================================================================

cfp.titles - plot labelling too far to the right for contour and vector plots


::

   Fixed


12. cfp.mapset - robinson projection changes
============================================

Robinson projection changes:

add titles code, add stipples, colorbar fails, colorbar in incorrect place


::

   Changed



13. cfp.generate_titles - error if cell_method has no associated axis
=====================================================================

An error occured if a cell_method had no associated axis.  A check was put in place to detect this.


::

   Changed



14. cfp.con - ugrid keyword changed to irregular
===============================================

In cfp.con the ugrid keyword was changed to irregular as this is more appropriate.


::

   Changed


15. cfp.bfill - map transform now passed through to blockfill_fast code
=======================================================================

In cfp.bfill the map transform wasn;t passed through to the blockfill_fast code and this has now been corrected.


::

   Fixed
   
   
16. cfp.con - new test for spatially irregular data points    
==========================================================

A new test was introduced to cfp.con to check whether the data points are spatially irregular.  This is done with the 
x points comparing the size of x to the size of the unique x points.  User specified values of True or False override 
the new internal test.


::

   Changed


17. cfp.levs - np.int depreciated change
========================================

np.int has been depreciated in newer versions of numpy and was just an alias for int.  In cfp.levs the np.int was changed to np.int64 to match the surrounding code.


::

   Changed


18. cfp.bfill - change of level inclusion
=========================================

cfp.bfill has been changed in the blockfill=True section.  The code now matches blockfill=fast in that the fill is between matching the first level and below the second level.


::

   Changed


19. cfp.lineplot - error in calculating user time limits for the x-axis
=======================================================================

cfp.lineplot - an error in calculating user time limits for the x-axis has been fixed.


::

   Fixed


20. cfp.setvars - grid=True didn't work on a cylindrical map
============================================================

cfp.setvars - grid=True doesn't work on a cylindrical projection map.  The grid keyword was moved into the cfp.con code as this was more appropriate.  The grid_zorder parameter controls the plotting order of the grid and has a default value of 100.  A calling sequence to draw dashed grey lines of thickness every 10 degrees in longitude and latitude would be:

::

   import cf
   import cfplot as cfp
   f = cf.read('cfplot_data/tas_A1.nc')[0]
   cfp.setvars(grid_x_spacing=10, grid_y_spacing=10, grid_colour='grey', grid_thickness=0.5, grid_linestyle='--' )
   cfp.con(f.subspace(time=15), lines=False, grid=True)


::

   Fixed
   
   
21. cfp.setvars - feature_zorder parameter added
================================================

In cfp.setvars the feature_zorder parameter was added.  This controls the plotting order of the features and has a default value of 99.


::

   Changed
   
   
22. cfp.con - blockfill and blockfill_fast for 2D data added
============================================================

cfp.con - blockfill and blockfill_fast for 2D data added.


::

   Added
   
   
23. cfp.con - code to subspace field to user defined map removed 
================================================================

cfp-con - code to subspace field to user defined map removed as this was causing issues with blank plots.


::

   Removed
   
   
   
   



