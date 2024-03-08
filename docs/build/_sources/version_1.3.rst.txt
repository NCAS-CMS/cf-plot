.. _version_1.3:

version 1.3 changes
*******************


1. Document code changes in a more detailed manner
==================================================
More information is needed on the changes made between versions.  This is useful for both users to see what has changed since the previous version and to track cf-plot development in a more meaningful way.

::

   Changes made for new releases in the versions page from 1.3 forward have their own web page
   referenced from the versions page. 




2. Remove redundant __init__.py file from source code
=====================================================
Work out which of the source __init__.py are used for version information and delete the other copy.

::

   The __init__.py in /home/swsheaps/cfplot.src/cfplot is the one to use, the other copy has been deleted.




3. Blockfill example now fails
==============================

::
 
   In cf-python the isbounded method was renamed to hasbounds.  Changed code to use the new method.

 

4. gvals bug
============

cfp.gvals(dmin=32400, dmax=43200, tight=1, mod=0)

gives

(array([32160, 32830, 33500, 34170, 34840, 35510, 36180, 36850, 37520,
38190, 38860, 39530, 40200, 40870, 41540, 42210, 42880]), 0)

The result shouldn't have a value below 32400 and should start at 32400.

:: 

   Modified gvals routine to not change the step if mod is set to 0.



5. Example 7 x-axis is labelled as degrees_north
================================================

The various CF latitude names should be caught and the returned as 'latitude' 

:: 

   Fixed.



6. Plot limits bug
==================

When plots is made with no user call to gset a zonal mean plot followed by a map plot 
gives previous plot limits.  A call of gset() is needed before the call to gclose 
in con and vect routines.

::

   Fixed.


7. Colour scales prevent cf-plot being used as a stand-alone program
====================================================================

The code uses a call to cscale to set the colour scales and this requires
that the colour scales are installed in the correct place by the installer.
This prevents the cfplot.py program from being used as a stand-alone program.

::

   scale1 and cosam colour scales integrated into the program so that cf-plot
   can be used in stand-alone mode.


8. Revamp colour scales page to use consistent set of images
============================================================

The colour scales page had a set of scale images from a variety of sources.  

::

   A new routine called  process_color_scales was written to produce consistent
   images and the rst code needed for the colour_scales.rst file.



9. Move up the vector plot in the gallery so that it is level with the other plots
==================================================================================

::

   Moved



10. Add in code to get verbose messages
=======================================

It is useful for debugging to see what cf-plot is doing as it progresses with making a 
plot.  Calling the con routine with verbose=1 gives some basic messages about the progress.
Of greater interest might be the output of the call from con to cf_data_assign.
The cf_data_assign function verbose option lets the user know which parts of CF are being used to
assign the axes names, units and data.

The verbose nature of cf-plot may be expanded beyond this if it is found to be useful.


::

   Verbose code added to con and cf_data_assign


11. Tidy up contour routine
===========================

Con, the contour routine, needs tidying up, commenting and reordering to make it clearer.

::

   Done


12. Batch mode processing
=========================

Check cf-plot works in batch mode and modify if not.

::

   A display check is now made in the cf-plot code and if none is present then the Agg backing 
   store is used.

   The following configuration works on the Reading Met department Linux system.  Need to check why
   submitting just the Python script doesn't work.


   /home/swsheaps/ajh.sh:
   #!/bin/sh
   /home/opt-user/Enthought/Canopy_64bit/User/bin/python /home/swsheaps/ajh.py

   /home/swsheaps/ajh.py:
   import cf, cfplot as cfp
   f=cf.read('cfplot_data/tas_A1.nc')[0]
   cfp.plotvars.file='/home/swsheaps/ll.png'
   cfp.con(f.subspace(time=15))

   run the batch job at 16:33:
   at -f /home/swsheaps/ajh.sh 16:33


13. process_color_scales page doesn't appear as an autofunction
===============================================================

::
  
   Fixed - need to have the cf-plot reference in the line
   .. autofunction:: cf-plot.process_color_scales


14. Tidy up and comment cf_data_assign data input code
======================================================

::

   Done


15. Data input documentation section needs revising 
===================================================

The cf_data_assign code rewrite has made the data input documentation out of date.

::

   Data input documentation rewritten.


16. Vect routine keyword documentation incomplete
=================================================

::

   Fixed


17. Rearrange order of gallery plots
====================================

Rearrange the order of the gallery plots to make the major plot types more prominent.

::

   Fixed






