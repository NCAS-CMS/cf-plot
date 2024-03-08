.. _version_1.7:
version 1.7 changes
*******************

Rolling update of features.


1. Irregular grid plotting
==========================

 ::

   Introduced


2. Zonal vector plots
=====================

 ::

   Introduced


3. Bug in cf_data_assign for user defined plots
===============================================

 ::

   Fixed


4. Bug in vect for multiple plots
=================================

 ::

   Fixed


5. Code change for cf-python major release
==========================================

Change .transform for .ref to work with new naming scheme in cf-python 1.0.0

 ::

   Implemented

6. Minor bug fix in manual contour level specification
======================================================

In the bfill routine levs=clevs.astype(float) was changed to levs=np.array(clevs).astype(float)

 ::

    Fixed
   

7. No change
============

An error was made in changing to version 1.7.7 and was reverted in 1.7.8.

 ::

    Fixed


8. Check cf-python is able to be imported and is greater or equal to version 1.0.1
==================================================================================


Change import section at start of cf-plot code so that version 1.0.1 or greater of cf is present.

 ::

   Fixed



9. Add reverse keyword to cscale routine
========================================

Added the reverse keyword to the cscale routine to rever the colour scale

 ::

   Done


10. Add new perceptually uniform sequential colour scales
=========================================================


Added viridis, magma, inferno, plasma, parula and gray uniform sequential colour scales.  These scales
are colour blind friendly and also perceptually uniform.

 ::

   Done


11. Make viridis the default sequential colour scale
====================================================


Make viridis the default sequential colour scale.

 ::

   Done


12. Bug in mapset - coastline resolution cannot be changed
==========================================================

 ::

   Fixed




13. con update - allow default expansion of colour scales to fit the contour levels 
===================================================================================


When setting a different colour scale cf-plot now automatically matches colour table to 
the contour levels.


 ::

   Done



14. con update - numpy warning when having a zero contour  
=========================================================


Having a zero contour in the levels caused a numpy warning when doing a contour map.  The 
numpy warning level was reduced in the con routine so this warning isn't shown.  This may
be removed in a future version of cf-plot as it looks like the numpy warning isn't there in
later versions of numpy. 


 ::

   Done


15. Update cf-plot documentation to reflect new colour maps
===========================================================


The cf-plot documentation was chaged to reflect the adoption of viridis as the new sequential 
data colour map.  Other examples were also changed to show the new magma, inferno, plasma, 
parula and gray colour scales.


 ::

   Done



16. Missing field name on PP data 
=================================


With PP data that has no standard_name, long_name or short_name the field name is blank.  The field naming scheme was changed to use the cf-python method field.name('No Name') setting the field name to 'No Name' as a catch all. 


 ::

   Done




17.  Vector key location
========================

vect now takes key_location=[xloc, yloc] to change the position of the vector key.  The xloc, yloc are in normalized coordinates with the default being [0.9, -0.06]

 ::

   Done


18. Single colorbar for multiple plots
======================================

con now takes colorbar_position= [xmin, ymin, x_extent, y_extent] option.  These values are in normalised coordinates. For use when a common colorbar is required for a set of plots. A typical set of values would be [0.1, 0.05, 0.8, 0.02]

 ::

   Done


19. Plot size and offsets introduced
====================================

gopen now takes additional parameters to alter the figure size and margins:

figsize=[11.7, 8.3]  - figure size in inches
left=0.12 - left margin in normalised coordinates
right=0.92 - right margin in normalised coordinates
top=0.92 - top margin in normalised coordinates
bottom=0.08 - bottom margin in normalised coordinates

::

   Done


20. - 26. Mods to __init__.py and setup.py
==========================================

Mods to setup files to point to correct documentation website and to properly reference colourmaps directory.




27. EP flux vectors
===================

vect to be modified to take addition values so that EP flux vector etc plots are possible.


::

   Done - see example 15









