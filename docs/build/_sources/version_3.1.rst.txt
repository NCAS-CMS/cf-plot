.. _version_3.1:
version 3.1 changes
*******************


0. Add initial support for UGRID data
=====================================

Initial support for UGRID data was added.


::

    Done



1. Add titles option to cfp.con
===============================

A titles option was added to cfp.con.  Setting this to True prints off a set of dimension 
titles at the top of the plot.


::

    Done



2. Time axis - calendar is now set to standard if none is present
=================================================================

If a time axis has no calendar then this is now set to standard if none is present.


::

    Done



6. Various changes to update to cf-python 3.9.0
===============================================

Various changes to setup.py and cf-plot were made to be compatible with cf-python 3.9.0. 


::

    Done



7. cfp.lines, cfp.vect - added titles option 
============================================

The titles option to display the field dimension and cell methods selections were added to cfp.lines and cfp.vect.

::

    Done



8. cfp.mapset - LambertCylindrical added
========================================


The LambertCylindrical projection was added to cfp.mapset.

::

    Done



9. Mapping change internally
============================

A mapping change was made internally to change from f.ref('rotated_latitude_longitude') to 
f.ref('grid_mapping_name:rotated_latitude_longitude'). This was due to a feature introduced in 
cf-python 3.8.0.  The longer form always works and so this has been adopted.

::

    Done



10. cfp.gpos(1) causes stray box lines
=====================================


When making multiple plots on a page calling cfp.gpos(1) causes stray box lines to be added to the first plot.

::

    Fixed



11. cfp.con - blockfill bugfix
==============================

If a blockfill contour plot is requested and the X coordinate has bounds and the Y coordinate does not have bounds then 
an error occurs.

::

    Fixed



12. cfp.bfill - default plotting order changed
==============================================

The default plotting order for cfp.bill has been changed from None to 4.  If any issues arise because of this please report 
them to me - andy.heaps@ncas.ac.uk.

::

    Changed



13. cfp.vect - added transparency setting
=========================================

An alpha transparency setting was added to cfp.vect.

::

    Done



14. cfp.mapset - overlay map plots stopped working
==================================================

More recent versions of Cartopy stopped overlay map plots from working. 


::

    Fixed


15. cfp.cf_data_assign - internal routine updated
=================================================

The internal data assignment routine cfp.cf_data_assign was updated to use the cf-python 
filter_by_axis method in f.coordinate.



::

    Updated


16. cfp.vect - high latitude vector code modified
=================================================

Cartopy has an issue with higher latitude vectors as described at https://github.com/SciTools/cartopy/issues/1179.


The following code sets all the u and v components to be 10m/s so it would be expected that the vectors will be at 
45 degrees to the longitude lines.  Prior to the modification this wasn't the case. 

::

    import cf
    import cfplot as cfp

    f=cf.read('cfplot_data/ggap.nc')
    u=f[1].subspace(pressure=500)
    v=f[2].subspace(pressure=500)

    u.data[:] = 10
    v.data[:] = 10
    cfp.mapset(proj='npstere')

    cfp.vect(u=u, v=v, key_length=10, scale=100, pts=30)


This was fixed internally in cf-plot version 3.1.16 but may need a reversion to the original code if Cartopy gets a patch for this feature.


::

    Fixed


17. cfp.mapset - contour issue when using cartopy 0.20.0 and possibly later
===========================================================================

Cartopy version 0.20.0 and possibly later cause a contour over maps issue in cf-plot.  A version check in cf-plot is now in place to circumvent this.


::

    Cartopy version check in place
 
 
18. cfp.con - changes to ptype=0 code
=====================================
 
Additional code was added to cfp.con to cope with data which has one axis of longitude, latitude, pressure, time 
and another that isn't recogised as one of these.
 
::

   Changed
 
 
19. cfp.con - improved Z axis detection
======================================
 
The cf-plot find_dim_names routine was modified to use the cf-python get_data_axes method leading to more reliable Z axis detection when multiple Z axes
are defined in the field.


::

   Changed
 
 
20. cfp.con - transform_first - higher resolution map data contour plots
========================================================================

When making map contour plots > 400 points in longitude cartopy slows down markedly due to having to transform lots of patches.  The transform_first
keyword to cfp.con transforms the points rather than patches and leads to a considerable speed improvement.  For example a 1440 longitudes map plot took
30 minutes with the normal method and this decreased to 0.7 seconds when transform_first=True was set. If this keyword is set for lower resolution data
then the plot limits in longitude sometimes have missing data.

When there are more that 400 longitude points the option is set automatically but it can always be turned off with transform_first=False.


::

    Done
    

21. cfp.con - blockfill_fast - faster blockfill plotting
========================================================

Higher resolution data causes blockfill plotting to slow down markedly due to the number of cells plotted.  The blockfill_fast option was added to cfp.con which 
uses the Matplotlib pcolormesh routine to produce a much faster plot.  The original blockfill plotting is more accurate though and careful comparison of plots made both methods show 
small differences particularly at higher latitudes.  One blockfill plot went from 174 seconds to 4.3 seconds using the new option.


::

    Done
 
 
22. cfp.find_dim_names bug
==========================
 
If numpy arrays are passed for plotting some recently added code in cfp.find_dim_names tried to find the dimension names in the field.  The code was modified to not do this for this class of data.

 
::

    Fixed
    
    
23. Central data local added for cartopy
========================================

If the user has a central location for cartopy data it can be specified with the pre_existing_data_dir environment variable.  This location is checked for the relevant map data before ~/.local/share/cartopy.  If it is in neither then an attempt will be made to download the data.


::

    Added
    

24. cfp.gvals - final catch missing for no values
=================================================

A final catch for no defined values was missing


::

    Added


25. cfp.con - cartopy.add_cyclic_point - check for regular longitudes
=====================================================================

An error occurs in cartopy.add_cyclic_point if the longitudes aren't regular.  Added code to only call cartopy.add_cyclic_point if the longitudes are regular.


::

    Fixed
    
    
26. plot titles - change cell methods to cell_methods
=====================================================

In the plot titles section cell methds was corrected to cell_methods.


::

    Fixed


27. map_title - fixed bug in title for the southern polar stereographic projection
==================================================================================

A bug in the title code for the southern polar stereographic projection has been fixed.


::

    Fixed


28. cfp.con - added nlevs option
================================

The nlevs option to cfp.con was added which specifies the number of levels for to use for contour and fast 
blockfill methods.  For example cfp.con(f, nlevs=200, lines=False) will draw 200 filled contours and turn the line 
contours off.  This is useful when looking at data which is very close together where the traditional contour 
levels don't show the detail in the field.  The colour map for a divergent field such as zonal wind, 'scale1', 
is not necessarily centred on zero with this option so more care with interpretation is needed.


::

    Added


29. cfp.con - type 0 plots bugfix
=================================

cfp.con was changed to fix some bugs with the identification and plotting of axes.
 

::

    Fixed

 
30. cfp.generate_titles - update code to include cell_method qualifiers
=======================================================================
 
cfp.generate_titles was updated to include the text for any cell_method qualifiers.
 
 
::

    Fixed
 
 
31. cfp.con - axis labelling issues with rotated pole coordinates
=================================================================
 
cfp.con produced extraneous axis labels for rotated pole coordinates.
 
 
::

 
   Fixed
 
 
32. cfp.plot_map_axes - mods for cartopy > 0.20.0
=================================================

The use of outline_patch.set_visible(False) to remove a surrounding box for polar stereographic and lcc plots has been change to 
set_frame_on(False) as the previous method has been depreciated from cartopy 0.20.0.


::

   Changed
   
   
   

 
 
 
 
 
 
 
 
