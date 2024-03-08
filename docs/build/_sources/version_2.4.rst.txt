.. _version_2.4:
version 2.4 changes
*******************

Trajectory plotting

0. Added support for trajectories
=================================

Support added for plotting trajectories in contiguous ragged array format.




::

    Done



1. zorder option added to plotting commands
===========================================

The plotting order parameter, zorder, has been added to con, vect, stipple and lineplot.  Using 
zorder with a larger number puts the plotted item on top of an item with a lower zorder number.


::

    Done


2. Fix blockfill on pressure plots
==================================

A bug in pressure blockplots was fixed.


::

    Done



3. Add a gallery item for WRF plots
===================================

A gallery item was added for Weather Research and Forecasting (WRF) Model plots.


::

    Done




4. Test release
===============

A test release to fix a bug in the markup in the README.txt file for cf-plot



::

    Fixed


5. traj - fix missing trajectories
==================================

An incorrect loop index was used leading to not all teh trajectories being plotted.



::

    Fixed




6. vect - magmin keyword added
==============================

The magmin keyword was added to vect.  Any vectors with a magnitude less than this aren't plotted.


::

    Done



7. con - model level data not properly labelled
===============================================

Contour plots of latitude or longitude vs model level number weren't proper labelled on the y-axis.


::

    Done


8. con - polar plot labels
==========================

If a polar plot is made and the axis_label_fontsize is set to zero then the longitide labels are no longer 
plotted.  Previously they were plotted but still appeared on the plot wven though they had zero size.


::

    Done


9. con - Rotated pole data change
=================================

Contour plots using rotated pole data - if the longitudes and latitudes for each point are supplied as 2D arrays 
in auxiliary coordinates then these are now used for making a contour plot.  Previously the rotated pole coordinate 
system was used to generate the longitudes and latitudes for the contour plot.


::

    Changed











