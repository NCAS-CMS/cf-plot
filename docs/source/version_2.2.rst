.. _version_2.2:
version 2.2 changes
*******************

Change from BaseMap to Cartopy mapping.

0. Base code change from BaseMap to Cartopy mapping
===================================================

Support for Basemap will be finish at the same time as Python 2.7 at the end of 2020.   Cartopy is now quite mature and the change of use from Basemap to Cartopy should present only a few changes to cf-plot users while offering some useful enhancements.


::

    Done



1.  mapset - change of resolution parameters
============================================

resolution=resolution - the map resolution - can be one of '110m',
'50m' or '10m'.  '50m' means 1:50,000,000 and not 50 metre.


::

    Done



2. setvars - continent linestyle
================================

The setvars routine can now be used to set the continent linestyle

cfp.setvars(continent_linestyle='dashed') for instance


::

    Done



3. vect - vector plots now respect reduced map grids
=====================================================


When plotting vectors onto a map previous versions used a whole globe cylindrical projection.  This has now
changed and will plot the map to match the input vector area unless any map settings have been changed by the user.


::

    Fixed



4. lineplot - turning off the legend frame
==========================================

To turn off the legend frame use
cfp.setvars(legend_frame=False)


::

    Done


5. con - colorbar font properties
=================================


colorbar font properties can now be set using the setvars routine:
cfp.setvars(colorbar_fontsize=11) 
cfp.setvars(colorbar_fontweight='normal')


::

    Done



6. lineplot - marker edge options added
=======================================

Two new marker properties have been introduced to the lineplot routine.

|   markeredgecolor = 'k' - colour of edge around the marker
|   markeredgewidth = 0.5 - width of edge around the marker


::

    Done



7. lineplot - legend frame options added
========================================

The default of having a frame around the legend can now be turned off with:

cfp.setvars(legend_frame=False) 


Legend frame face and edge colors can be set with:

cfp.setvars(legend_frame_face_color='pink')
cfp.setvars(legend_frame_edge_color='blue')



::

    Done




8. axes - degree symbol option for longitude and latitude labelling
===================================================================

The default labelling for longitude and latitude axes is 90E, 30N etc.  
If a degree symbol is required this can be made the default for all subsequent 
plots with:

cfp.setvars(degsym=True)

Users can also add this option to the ~/.cfplot_defaults file as

degsym True

 
The degree symbol is '$\degree$' as a string for any further plot customisation.

::

    Done



9. rgrot, rgunrot - removed rotated axis routines
=================================================

The rgrot and rgunrot routines are no longer needed and have been replaced 
by using the Cartopy ccrs.RotatedPole transform.


::

    Done



10. con - incorrect cropping of polar stereographic and lcc projections
=======================================================================


The crop limits used in Cartopy / Matplotlib for polarstereographic and lcc
projections are slightly wrong.  These were fixed by recalculating the limits 
and setting them with set_xlim and set_ylim within the plot_map_axes routine.


::

    Done



11. stipple - Add ylog parameter
================================

Stipple now works with log pressure plots by adding the ylog=True parameter.


::

    Done




12. gvals  - very small values bug
==================================

cfp.gvals(1.90028259794e-09, 1.05456045674e-07)

produced an array error.



::

    Corrected



13. lineplot - y-axis labels fontsize and fontweight
====================================================

lineplot y-axis labels fontsize and fontweight were unaffected by

|    cfp.setvars(axis_label_fontsize=20)
|    cfp.setvars(axis_label_fontweight='bold')



::

    Corrected




14. setvars - axis_width keyword added
======================================

The axis_width keyword was added to the setvars routine.  This controls the width
of the drawn axes around the plot.





15. cf-data-assign - rotated pole axis specification bug
========================================================

A bug appears in the internal routine cf-data_assign for rotated pole plots when both 
the X and Y axes have the same number of points.  The cf_data_assign routine was modified to 
properly assign grid_longitude and grid_latitude.



::

    Fixed


16. graphs
==========

Documentation updated on line labelling for legends in example 28.  In addition it is also shown how to access a plot legend directly using Matplotlib commands to create a custom legend.


::

    Updated



17. stipple
===========

Incorrect stippling for longitudes < 0 in polar stereographic plots


::

    Fixed


18. lineplot - incorrect axis labelling
=======================================

In lineplot if no axis labels are provided then the axis labels were copied from the tick values.  In the case of floating point numbers these can sometimes give large numbers of decimal places due to numeric rounding.  A fix has been put in place to use the format specifier '{}'.format(val) so 13.899999999999997 becomes the more reasonable string value of '13.9'.


::

    Fixed





