.. _version_3.0:
version 3.0 changes
*******************

Change code to use Python 3 and cf-python 3.

0. Change code to use Python 3 and cf-python 3
==============================================

cf-plot code was changed to use Python 3 and cf-python 3.  Support for Python 2.7 and cf-python2.x was dropped. 


::

    Done


1. Port to Mac OSX
==================

The cf-python and cf-plot code base was ported to Mac OSX.


::

    Done



2. Separate out the colour bar routine
======================================

In the original cf-plot code base the Matplotlib colorbar routine was called individually in many places.  This has now been separated out into the cfp.cbar routine which is callable from anywhere in the cf-plot code or in user code.



::

    Done





3. cf_var_name - missing initial definition of ncvar
====================================================

A missing initial definition of ncvar in the cf_var_name routine was fixed.


::

    Fixed



4. Grid drawing options changed
===============================

The grid_lons and grid_lats options used in cfp.setvars have been removed.  The grid drawing options for
UKCP grids are now controlled by xticks, yticks and xaxis, yaxis as in other plots.

The polar stereographic grid now takes the line colour, line width and line style from grid_colour, grid_linestyle and grid_thickness 
that are set in cfp.setvars.

::

    Changed



5. con - blockfill plots - bug in blockfill code
================================================

A bug in the blockfill code logic meant that some data couldn't be plotted in blockfill mode.


::

    Fixed



6. con - automatic levels sometimes have too many decimal places
================================================================

The automatic contour level generation in con sometimes has too many decimal places.  


::

    Fixed



7. setup.py missing dependencies
================================

Missing dependencies for cf-python, scipy and cartopy were added to setup.py


::

    Fixed



8. Plot viewing with the Matplotlib interface
=============================================

Matplotlib can now be configured to allow non-blocking of the command prompt when a plot is 
active.  The cf-plot code has been changed allow the default plot viewer to be the Matplotlib 
interface.  Users can still use the previous Imagemagick display command by typing

cfp.setvars(viewer='matplotlib')

or add the below line to ~/.cfplotrc

viewer matplotlib


::

    Changed



9. mapset - aspect ratio in cylindrical projection plots
========================================================

The default setting for cylindrical plots is for one degree of longitude to be the same size 
as one degree of latitude.  This can now be changed with the aspect option to mapset:

|    aspect = 'equal' - the default, 1 degree longitude is the same size as one degree of latitude
|    aspect = 'auto'  - map fills the plot area
|    aspect = number  - a circle will be stretched such that the height is number times the width. 
|                       aspect = 1 is the same as aspect='equal'.


::

    Added



10. con - Hovmuller plot with short time axis
=============================================

An issue with a short time axis on a Hovmuller plot was found and fixed.



::

    Fixed



11. con - multiple plot spacing incorrect
=========================================

Fixed a variety of issues when using cfp.con and mutiple plots using the rows and columns 
spacing options to cfp.gopen.


::

    Fixed



12. con and vect - adding cyclic data issue
===========================================

When adding an extra cyclic point in longitude and the data the cartopy_util.add_cyclic_point
routine sometimes fails when the data isn't quite regularly spaced.  Generally this happends 
when the numpy value for the data has a lot of decimal points.  A numeric fix for this 
incorrect spacing was put in place.


::

    Fixed



13. con and lineplot - long floating point numbers
==================================================

In cfp.con and cfp.lineplot large floating point numbers sometimes occurred on the axes and in the contour
labels.  A new internal routine called cfp.fix_floats addresses these issues.  For example a numpy arange array
from 0 to 5 in steps of 0.1 sometimes produced an axis of
0, 0.1, 0.2, 0.3, 0.3999999999999999, 0.5
which produced a badly fored axis.
 

::

    Fixed



14. con - blockfill plot with a time mean can sometimes produce unexpected results
==================================================================================

When plotting a blockfill contour plot of data with a time mean the plot can sometimes produce unexpected results.
For example the following data has monthly data points but bounds of ten years for each point.  


|   **f.coord('T').dtarray**
|   array([cftime.Datetime360Day(1983-08-16 00:00:00),
|          cftime.Datetime360Day(1983-09-16 00:00:00),
|          cftime.Datetime360Day(1983-10-16 00:00:00)], dtype=object)

|   **f.coord('T').bounds.dtarray**
|   array([[cftime.Datetime360Day(1979-02-01 00:00:00),
|           cftime.Datetime360Day(1988-03-01 00:00:00)],
|          [cftime.Datetime360Day(1979-03-01 00:00:00),
|           cftime.Datetime360Day(1988-04-01 00:00:00)],
|          [cftime.Datetime360Day(1979-04-01 00:00:00),
|           cftime.Datetime360Day(1988-05-01 00:00:00)]], dtype=object)


To reset the bounds for this data to be relevant for blockfill plotting use

|   **T=f.coord('T')**
|   **T.del_bounds()**
|   **new_bounds=T.create_bounds()**
|   **T.set_bounds(new_bounds)**

The new time data bounds are now monthly which is what is expected:

|   **f.coord('T').bounds.dtarray**
|   array([[cftime.Datetime360Day(1983-08-01 00:00:00),
|           cftime.Datetime360Day(1983-09-01 00:00:00)],
|          [cftime.Datetime360Day(1983-09-01 00:00:00),
|           cftime.Datetime360Day(1983-10-01 00:00:00)],
|          [cftime.Datetime360Day(1983-10-01 00:00:00),
|           cftime.Datetime360Day(1983-11-01 00:00:00)]], dtype=object)


::
    Information added to user guide
    


15. con, vect and lineplot - input data checking
================================================


Basic data size and shape checking is now done for the inputs of CF data to con, vect and lineplot.


::

    Done



16. lineplot - multiple lines on a single graph can have incorrect axis limits
==============================================================================

When making muliple lines on a single graph it can have incorrect axis limits as by
default the axis limits and labelling were chosen from the last made line.  This was changed so
that the the min and max of X and Y for the lines in accumulated and applied to the graph.


::

    Fixed



17. mapset - Lambert Conformal projection - lcc now works in the southern hemisphere
====================================================================================

Selecting the Lambert Conformal 'lcc' projection now works in the southern hemisphere.



**cfp.mapset(proj='lcc', lonmin=-50, lonmax=50, latmin=-80, latmax=-10)**



::

    Fixed



18. setup.py changes
====================

Some minor changes to the requirements were made to the setup.py file


::

    Fixed



19. __init__.py change
======================

Put in missing quote in __date__ string.


::

    Fixed



20. lineplot - check for axis missing
=====================================


In lineplot there was no check to see if the Z or T axis existed bufore trying to extract information from them.  A check is now made so that this doesn;t give an error when making a lineplot using data without these axes.



::

    Fixed



21. cf-plot install notes changed
=================================

The cf-plot install notes have been changed to include information on how to use pip to upgrade an existing version of cf-plot.



::

    Fixed


22. gvals routine rewritten - internal contour and axis label generator
=======================================================================

The gvals internal routine has been rewritten to be shorter and more logical.  This routine is used in the automatic selection of contour and axis labels.
The new routine should produce better formatted and spaced labels.



::

    Fixed



23. cfp.con - plot type=0 rewrite
=================================

The cfp.con section for plot_type=0 has been rewritten.  plot_type=0 is where only one or less
if X, Y, Z, T are being plotted.  i.e. time vs station index.



::

    Changed



24. Boolean data
================

CF fields that are passed for plotting are changed to 0 or 1 values.


::

    Fixed



25. cfp.lineplot - default line colours now taken from Matplotlib
=================================================================

The default cfp.lineplot colours are taken from Matplotlib unless specified by the user with 
the color keyword.  The previous default was for black which made lineplots more difficult to 
interpret.


::

    Changed




26. cfp.stream - streamplots added
==================================

Streamplots are now available in cf-plot.  Examples are in the user guide under vectors and also in the vector section of example plots.


| stream - plot a streamplot
|
| u=None - u wind
| v=None - v wind
| x=None - x locations of u and v
| y=None - y locations of u and v
| density=None - controls the closeness of streamlines. When density = 1, 
|                the domain is divided into a 30x30 grid
| linewidth=None - the width of the stream lines. With a 2D array the line width 
|                  can be varied across the grid. The array must have the same shape as u and v
| color=None - the streamline color 
| arrowsize=None - scaling factor for the arrow size
| arrowstyle=None - arrow style specification
| minlength=None - minimum length of streamline in axes coordinates
| maxlength=None - maximum length of streamline in axes coordinates






27. cfp.levs - step option bugfix
=================================

cfp.levs(step=20) sets the step to 20 for contour level generation.  This was inadvertenty cleared
inbetween plots and also generated a step of a float of 20.0 rather than the integer 20.


::

    Fixed



28. Code change to adhere to PEP8
=================================

The cf-plot code base was changed to adhere to PEP8 with a 100 column line length.  


::

    Changed




29. Changed default zorder from None to 1
=========================================

The default zorder of None caused issues with the latest versions of Matplotlib so this was changed to 1.

::

    Changed


30. savefig option of papertype removed
=======================================


The savefig option of papertype was removed as this is being dropped from later versions of matplotlib.

::

    Changed


31. con - polar plots colorbar size changed
===========================================

The default size of colorbar_shrink for contour plots was changed from 1.0 to 0.8 to match the size of the plot.  Setting it to 1 made it larger than the plot.


::

    Changed



32. setvars - remove white space around plots
=============================================

To remove white space from around plots you can use the ImageMagick convert command convert -trim fig1.png fig1_trimmed.png or use
the setvars command:  **cfp.setvars(tight=True)**

::

    Changed



33. lineplot - passing two CF fields for plotting doesn't plot the second line
==============================================================================

Passing two CF fields for plotting to lineplot only plotted the first line.  This was intentional behaviour and now doing this causes an 
error.  The way to plot two lines is to open a graphics plot with cfp.gopen(), make two separate calls to cfp.lineplot and then close the graphics plot with cfp.gclose().  This is consistent with making multiple contour plots or a contour plot with overlaid vectors or stipples.

::

    Changed


34. lineplot - change automatic y axis values for a constant value line plot
============================================================================

When using lineplot with a constant value graph the automatic y-axis limits were set from -0.001 to +0.001 of the constant value.  This has been changed to -1.0 to 1.0 of the constant value.

::

    Changed



35. traj - spurious data points plotted
=======================================

When using masked trajectory data and the latest version of numpy spurious data points were sometimes plotted.  


::

    Fixed



36. con and setvars - changing contour level selection from linear to log, loglike or outlier
=============================================================================================

A new routine **cfp.calculate_levels** has been added to the cf-plot code to allow different 
schemes for contour level selection.  The default in cf-plot is that when the user hasn't made a 
specific level selection the contour levels will be spaced linearly between the minimum and maximum
of the input data.

| An additional option to **cfp.con** is **calculate_levels** which takes:
| 'linear' - a linear set of levels between the minimum and maximum of the field
| 'log' - log levels - -1e6, -1e5 ,-1e4 etc
| 'loglike' - log like levels -5.e-05, -2.e-05, -1.e-05, -5.e-06, -2.e-06, -1.e-06 etc
| 'outlier' - removes outlier data before generating a linear set of levels.  The outlier must have less than
|             1% of the data values.
| 'inspect' - inspect and choose the most appropriate of the above values

**cfp.setvars** also has a new **calculate_levels** option which is persistent between **cfp.con** calls.

::

    Done



37. Fix incorrect version number in setup.py
============================================


An incorrect version number was set in setup.py.


::

    Fixed



38. con - No contour levels data throws an error in Matplotlib line labelling
=============================================================================

The default behaviour of Matplotlib has changed such that if the data is all the same the contour labelling scheme in Matplotlib throws an error.  This is in Matplotlib 3.3.2 and may well have been in previous versions. cf-plot was changed so that in thie case of min(data) == max(data) the contour labels are turned off so a plot can be made.


::

    Fixed



39. con - 2D data fails to plot in polar stereographic projection
=================================================================

Data associated with 2D longitude and 2D latitude arrays fails to plot in the polar stereographic projection. 


::

    Fixed











