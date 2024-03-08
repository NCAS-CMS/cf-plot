.. _version_1.9:
version 1.9 changes
*******************

Rolling update of features / bug fixes


1. Vector polar plots
=====================

Vector polar plots introduced.  Use the pts option to vect when doing a stereographic polar vector plot to interpolate
the grid to be uniformly spaced when viewed.

 ::

   Done


2. Change documentation web page location
=========================================

| Was:
| http://climate.ncas.ac.uk/~andy/cfplot_sphinx/_build/html/#
| changed to:
| http://ajheaps.github.io/cf-plot/#

 ::

   Done


3. Add orography / bathymetry colour scales
===========================================

 ::

   Done


4. Change cfplot to cf-plot
===========================

Package renamed to cf-plot to fit in with cf-python and cf-view.


 ::

   Done

5. Change web docs to github
============================

Web documents location changed to http://ajheaps.github.io/cf-plot.  setup.py etc references changed accordingly. 

::

   Done


6. Add plot spacing options to gopen
====================================

Add hspace and wspace plot spacing options to gopen.

 ::

   Done


7. lineplot - -assing non-CF data
=================================

Add options so that passing of non-CF data to lineplot works.

::

    Done


8. vect - turn off vector key 
=============================

Add show_key option to vect to allow turning off of vector key.

 ::

    Done


9. cscale - colour maps not referenced correctly when doing a local install
===========================================================================

pip install --user cf-plot

Doesn't allow changing of colour maps.

::

    Done


10. lineplot - add axis labelling that overrides any CF information
===================================================================

Add axis labelling that overrides any CF information in lineplot.


 ::

    Done



11. gclose - plots not closed properly
======================================

Add plot.close() to gclose routine to properly close each plot when it is finished.


::

    Done


12. levs - change in floating point levels calculation
======================================================

Floating point levels were calculated using numpy.arange and this can sometimes give stange contour levels. 
For example, 

|
|    np.arange(-0.2,0.2,0.04)
|    array([ -2.00000000e-01,  -1.60000000e-01,  -1.20000000e-01,
|        -8.00000000e-02,  -4.00000000e-02,   2.77555756e-17,
|         4.00000000e-02,   8.00000000e-02,   1.20000000e-01,
|         1.60000000e-01])


Using np.linspace(-0.2,0.2,11) gives a much neater set of levels and the floating point calculation of levels was changed 
to adopt this method.

::

    Done


13. levs - cfp.levs() fails to reset colorbar extensions
========================================================

cfp.levs() failed to reset colorbar extensions.


::

    Done



14. Change of name for some colour scales
=========================================

Colour scales with plus and minus in them cause issues in cfview. These colour scales have been renamed with the plus and minus changed to an underscore.


::

    Done



15. con - negative_linestyle and zero_thick issues
==================================================

Recent changes in the 1.5.x version of Matplotlib causes issues with the con routine negative_linestyle and zero_thick options.  con was changed to the new Matplotlib way of doing these.

::

    Done


16. con - xlog / log specification
==================================

Amended the xlog and ylog specification so that it now accpets True as well as 1 to give a log plot.


::

    Done


17. con, vect  added axis labelling commands
============================================

Added xticks, xticklabels, yticks, yticklabels, xlabel, ylabel to con and vect to control axis labelling.  Also added axis, axis, yaxis to control whether axes are plotted.


::

    Done


18. con - bug in color scheme
=============================

When turning off a colorbar with colorbar=None in the con routine the extension colors were then out of alignment.


::

    Fixed


19. vect - added vertical log scale
===================================

Added optional vertical log scale to the vect routine.


::

    Done



20. con  - added time vs height plots
=====================================

Added time vs height plots.

::

    Done

21. colour scales - adjust name
===============================

One of the colour scales had an incorrect extension and this caused an issue in cf-view.

::

    Done


22. Plot blocking resolved
==========================

If the display command from ImageMagick is available this is now used in conjunction with subprocess 
in preference to build-in Matplotlib viewer. This gets around the problem of a plot blocking the command prompt 
preventing further plots from being made.  Using cfp.setvars(viewer='matplotlib') will revert to using the 
built-in matplotlib picture viewer.


::

    Done


23. timeaxis routine introduced
===============================

The timeaxis routine takes a time axis and returns a sensible set of tick positions and labels.  This is an internal
routine that is used in Hovmuller and graph plots.


::

    Done



24. Multiple hovmuller plot calls produce incorrect pictures
============================================================

Subsequent plots after the first hovmuller plot call produce incorrect pictures.

::

    Fixed




25. Added time axis options to setvars
======================================

Added time axis tick marks and labelling options to setvars. Once set these plot options are used
for all subsequent time axes.

| tspace_year=None - time axis spacing in years
| tspace_month=None - time axis spacing in months
| tspace_day=None - time axis spacing in days
| tspace_hour=None - time axis spacing in hours

::

    Done



26. Time axes bugfix
====================

Bugfix for an issue in time axes.

::

    Done



27. Add axis label and alignment options to setvars
===================================================

Add axis label and alignment options to setvars:

| xtick_label_rotation=0 - rotation of xtick labels
| xtick_label_align='center' - alignment of xtick labels
| ytick_label_rotation=0 - rotation of ytick labels
| ytick_label_align='right' - alignment of ytick labels


::

    Done



28. Bugfix in gset
==================

Bugfix in gset for recent time axis changes.

::

    Fixed


29. Bug in lineplot
===================

Lineplot is now more logical and takes a CF-field (f) as the base use. The other use is
not to pass f but to have x=x and y=y.  This allows x vs y plots and y vs x plots.

::

    Fixed



30. con - filled contours and irregular contour levels
======================================================

Selecting irregular contour levels with cfp.levs(manual=manual) and filled contours gives a slight 
colour scale mismatch.  This was resolved by calculating a normalization array: 
plotvars.norm=matplotlib.colors.BoundaryNorm(boundaries=plotvars.levels, ncolors=ncolors)

::

    Fixed


31. con - blockfill plots
=========================

Slight bug in blockfill colours at the top end of the drawn colours.


::

    Fixed



32. setvars / lineplot - legend text size and weight
====================================================

Two new options were added to cfp.setvars to change the font size and weight for the legend in lineplot:

legend_text_size=None - legend text size
legend_text_weight=None - legend text weight


::

    Added



33. levs - changed level generation scheme
==========================================

The level generation scheme in levs when the user passes min, max, step has been changed.  It is now using Neil
Massey's scheme:

If min, max, step are integers:
levs = ((((np.arange(min, max+step*1e-10, step, dtype=np.float64)*1e10)).astype(np.int64)).astype(np.float64)/1e10).astype(np.int)

else:
levs = (((np.arange(min, max+step*1e-10, step, dtype=np.float64)*1e10)).astype(np.int64)).astype(np.float64)/1e10



::

    Changed



34. gvals - changed scheme for step >= 1
========================================

gvals changed to use more sensible steps when step >= 1.

steps are now 1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000, 20000, 25000, 50000, 100000, 
200000, 250000, 500000, 1000000.
              
If the number of steps from the above in (data max - data min) is greater than 12 then this step is used.


::

    Changed




