.. _version_1.5:
version 1.5 changes
*******************

This is a rolling bug/feature fix version.


1. Fix colour bar mislabelling
==============================

The colorbar can sometimes be mislabelled when using unusual manual labels.

cfp.levs(manual=[-1, 1, 10000, 20000, 30000, 40000, 50000, 60000]) 
will give the correct contour lines and labels but incorrect colorbar labels.  The color bar labels will
be 0, 2, 10001, 20001, 30001, 40001, 50001, 60001 and a +1 will appear next to the color bar label. 

It looks like this is an intentional behaviour of the code for colorbar and is correct but not what is required. The cf-plot code was changed to substitute the correct colorbar labels for the ones that colorbar thinks it should use.

 ::

   Fixed


2. Incorrect plot limits for multiple plots
===========================================

A longitude-latitude plot followed by a latitude-pressure plot on the same page gives incorrect plot limits for the second plot.

 ::

   Fixed



3. Bug in longitude wrapping
============================

Non global data in longitude-latitude causes a crash in the longitude wrapping section

 ::

   Fixed


4. Non-global longitude/latitude data is plotted on a global grid
=================================================================

The default cylindirical projection limits of -180 to 180 in longitude and -90 to 90 in latitude are used for all map plots.  This needs changing to be the limits of the data in these cases.

  ::

    Fixed



5. Automatic colour scales bug
==============================

Automatic colour scales are broken.  Remove call to cscale() in gpos. 

 ::

   Fixed



6. Colorbar labels overwrite each other
=======================================

Colour bar labels overwite each other when large number of contour levels are used or when more plot columns are used.   Include code to take account of these based on the total number of characters in the contour labels and the number of 
columns.  If the user hasn't supplied a value for colorbar_label_skip to the con routine then the calculated value is
used.  The labels used will start at the lowest for a continuous data set and from zero for a diverging one.


 ::

   Fixed


7. Latitude vs log pressure plot axes cause an abort
====================================================

Latitude vs log pressure plot axes cause an abort due to zero being used for the top of the atmosphere.  Line of code inadvertently deleted but this is now back in place.


 ::

   Fixed



8. A CF field list with one field is rejected by cf-plot before plotting
========================================================================

Code changed to check and pass the field for plotting.

 ::

   Fixed



9. Added longitude height plots
===============================

Longitude-height plots were missing from cf_data_assign and from the contouring routine.
These have now been added.

 ::

   Fixed



10. Documentation change
========================

The web and user guide documentation has chaged so that the examples reference data in cfplot_data.  This is so the gallery examples work as written and to prevent multiple copies of the example data being on local disks.

 ::

   Fixed



11. Reset command
=================

A reset command was added to the code to reset all the graphics options in one step.  Use cfp.reset().


 ::

   Added to code



12: Internal work on axes command
=================================

A lot of internal work was done on the axes command to make it write the passed data into the plotvars array.
The data from here then superceeds any automatically generated axis labels.

 ::

   Added to code



13. Setvars command added
=========================

A new command called setvars was added to the code.  This is used to set various common plotting options.
Options are:

    | file=None - output file name
    | text_fontsize=None - text fontsize, default=11
    | title_fontsize=None - title fontsize, default=15
    | axis_label_fontsize=None - default=11
    | text_fontweight='normal' - text fontweight
    | title_fontweight='normal' - title fontweight
    | axis_label_fontweight='normal' - axis fontweight
    | fontweight='normal' - all above fontweights
    | continent_thickness=None - default=1.5
    | continent_color=None - default='k' (black)


 ::

   Added to code




14. Reduced longitude grid not plotted correctly
================================================

A reduced longitude grid isn't plotted correctly due to a bug in 
the calculation of the lonrange variable.

 ::

   Fixed





