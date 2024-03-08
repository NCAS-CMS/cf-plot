.. _colour_scales:
Colour scales
*************

There are two default colour scales in cf-plot:

1) A continuous scale ('viridis') that goes from blue to green and then yellow and suits data that has no zero in it.  For example air temperature in Kelvin or geopotential height - see example 1 in the plot gallery.  

2) A diverging scale ('scale1') that goes from blue to red and suits data with a zero in it.  For example temperature in Celsius or zonal wind - see example 4 in the plot gallery.  The colour scale is automatically adjusted so that blue hues are below zero and red hues above zero.

When no calls have been made to **cfp.cscale** cf-plot selects one of theses scales based on whether there is a zero in the data passed for contouring.  If a call is made to **cfp.cscale** with just a colour scale name  **cfp.cscale('radar')**, for example, then this colour scale is used for all subsequent plots.  The colour scale is adjusted automatically to fit the number of contour levels in the plot. 

If a call to **cfp.cscale** specifies additional parameters to the colour scale, then the automatic colour adjustment is turned off giving the user fine tuning of colours as below.


.. image::  images/cs1.png 
  :scale: 65% 

::

   cfp.levs(min=-80, max=80, step=10)
   cfp.scale('scale1')

|
|




To change the number of colours in a scale use the ncols parameters. 


.. image::  images/cs2.png 
  :scale: 65% 

::

   cfp.cscale('scale1', ncols=12)
   cfp.levs(min=-5, max=5, step=1)

|
|

To change the number of colours above and below the mid-point of the scale use the above and below parameters.  This is useful for fields where you have differing extents of data above and below the zero line. 


.. image::  images/cs3.png 
  :scale: 65% 


::

   cfp.cscale('scale1', below=4, above=7)
   cfp.levs(min=-30, max=60, step=10)

|
|

For data where you need white to indicate that this data region is insignificant use the white=white parameter.  This can take single or multiple values of the index of the colour scale where white is required in the colour scale.

.. image::  images/cs4.png 
  :scale: 65% 

::

   cfp.cscale('scale1', ncols=11, white=5)
   cfp.levs(manual=[-10,-8, -6, -4, -2, 2, 4, 6, 8, 10])

.. image::  images/cs4.png
   :scale: 52% 


To reverse a colour scale use the **reverse=1** option to **cscale** and specify the number of colours required.

::

    cfp.cscale('scale1', reverse=1, ncols=10)



As a short example to show the flexibilty of the colour scale routines we will make a orography plot using the wiki_2_0.rgb orography/bathymetry colour scale. This has as many colours for bathymetry as for the oroggraphy but in this case we just need a blue ocean as we are really only interested in the orography.  So in this case we will define a set of levels using *levs* and then match the colour scale to them.  The wiki_2_0.rgb colour scale has as many colours for the ocean as for the land so we can use the above and below options 


.. image::  images/orog.png
   :scale: 52% 

::

   import cf
   import cfplot as cfp
   import numpy as np
   f=cf.read('cfplot_data/12km_orog.nc')[0]
   cfp.cscale('wiki_2_0', ncols=16, below=2, above=14)
   cfp.levs(manual=np.arange(15)*150)
   cfp.con(f, lines=False) 



User defined colour scales
--------------------------
Store these as rgb values in a file with one rgb value per line.  i.e. 

::

   255 0   0
   255 255 255
   0   0   255

will give a red white blue colour scale.  If the file is saved as /home/swsheaps/rwb.txt it is read in using

::

   cfp.cscale('/home/swsheaps/rwb.txt')



Selecting colours for graph lines
---------------------------------

This can be done in several ways:

1) Select the colours from the Matplotlib colour names - Google 'Images for matplotlib color names'.

cfp.lineplot(g.subspace(pressure=925), color='plum')

2) Use the hexadecimal code for the colour.

cfp.lineplot(g.subspace(pressure=925), color = '#eeefff')
 
  
3) Shades of grey can be selected with cmap(shade), where shade go from 0 to 1.

cfp.lineplot(g.subspace(pressure=925), color=cmap(0.8))




Predefined colour scales
------------------------
A lot of the following colour maps were downloaded from the NCAR Command Language web site.  Users of the IDL guide colour maps can see these maps at the end of the colour scales.


Perceptually uniform colour scales
----------------------------------
A selection of perceptually uniform colour scales for contouring data without a zero in. See `The end of the rainbow <http://www.climate-lab-book.ac.uk/2014/end-of-the-rainbow>`_ and `Matplotlib colour maps <http://bids.github.io/colormap>`_ for a good discussion on colour scales, colour blindness and uniform colour scales.

================== =====
Name               Scale
================== =====
viridis            .. image:: images/colour_scales/viridis.png
magma              .. image:: images/colour_scales/magma.png
inferno            .. image:: images/colour_scales/inferno.png
plasma             .. image:: images/colour_scales/plasma.png
parula             .. image:: images/colour_scales/parula.png
gray               .. image:: images/colour_scales/gray.png
================== =====

NCAR Command Language - MeteoSwiss colour maps
----------------------------------------------

================== =====
Name               Scale
================== =====
hotcold_18lev      .. image:: images/colour_scales/hotcold_18lev.png
hotcolr_19lev      .. image:: images/colour_scales/hotcolr_19lev.png
mch_default        .. image:: images/colour_scales/mch_default.png
perc2_9lev         .. image:: images/colour_scales/perc2_9lev.png
percent_11lev      .. image:: images/colour_scales/percent_11lev.png
precip2_15lev      .. image:: images/colour_scales/precip2_15lev.png
precip2_17lev      .. image:: images/colour_scales/precip2_17lev.png
precip3_16lev      .. image:: images/colour_scales/precip3_16lev.png
precip4_11lev      .. image:: images/colour_scales/precip4_11lev.png
precip4_diff_19lev .. image:: images/colour_scales/precip4_diff_19lev.png
precip_11lev       .. image:: images/colour_scales/precip_11lev.png
precip_diff_12lev  .. image:: images/colour_scales/precip_diff_12lev.png
precip_diff_1lev   .. image:: images/colour_scales/precip_diff_1lev.png
rh_19lev           .. image:: images/colour_scales/rh_19lev.png
spread_15lev       .. image:: images/colour_scales/spread_15lev.png
================== =====


NCAR Command Language - small color maps (<50 colours)
------------------------------------------------------

=================== =====
Name                Scale
=================== =====
amwg                .. image:: images/colour_scales/amwg.png
amwg_blueyellowred  .. image:: images/colour_scales/amwg_blueyellowred.png
BlueDarkRed18       .. image:: images/colour_scales/BlueDarkRed18.png
BlueDarkOrange18    .. image:: images/colour_scales/BlueDarkOrange18.png
BlueGreen14         .. image:: images/colour_scales/BlueGreen14.png
BrownBlue12         .. image:: images/colour_scales/BrownBlue12.png
Cat12               .. image:: images/colour_scales/Cat12.png
cmp_flux            .. image:: images/colour_scales/cmp_flux.png
cosam12             .. image:: images/colour_scales/cosam12.png
cosam               .. image:: images/colour_scales/cosam.png
GHRSST_anomaly      .. image:: images/colour_scales/GHRSST_anomaly.png
GreenMagenta16      .. image:: images/colour_scales/GreenMagenta16.png
hotcold_18lev       .. image:: images/colour_scales/hotcold_18lev.png
hotcolr_19lev       .. image:: images/colour_scales/hotcolr_19lev.png
mch_default         .. image:: images/colour_scales/mch_default.png
nrl_sirkes          .. image:: images/colour_scales/nrl_sirkes.png
nrl_sirkes_nowhite  .. image:: images/colour_scales/nrl_sirkes_nowhite.png
perc2_9lev          .. image:: images/colour_scales/perc2_9lev.png
percent_11lev       .. image:: images/colour_scales/percent_11lev.png
posneg_2            .. image:: images/colour_scales/posneg_2.png
prcp_1              .. image:: images/colour_scales/prcp_1.png
prcp_2              .. image:: images/colour_scales/prcp_2.png
prcp_3              .. image:: images/colour_scales/prcp_3.png
precip_11lev        .. image:: images/colour_scales/precip_11lev.png
precip_diff_12lev   .. image:: images/colour_scales/precip_diff_12lev.png
precip_diff_1lev    .. image:: images/colour_scales/precip_diff_1lev.png
precip2_15lev       .. image:: images/colour_scales/precip2_15lev.png
precip2_17lev       .. image:: images/colour_scales/precip2_17lev.png
precip3_16lev       .. image:: images/colour_scales/precip3_16lev.png
precip4_11lev       .. image:: images/colour_scales/precip4_11lev.png
precip4_diff_19lev  .. image:: images/colour_scales/precip4_diff_19lev.png
radar               .. image:: images/colour_scales/radar.png
radar_1             .. image:: images/colour_scales/radar_1.png
rh_19lev            .. image:: images/colour_scales/rh_19lev.png
seaice_1            .. image:: images/colour_scales/seaice_1.png
seaice_2            .. image:: images/colour_scales/seaice_2.png
so4_21              .. image:: images/colour_scales/so4_21.png
spread_15lev        .. image:: images/colour_scales/spread_15lev.png
StepSeq25           .. image:: images/colour_scales/StepSeq25.png
sunshine_9lev       .. image:: images/colour_scales/sunshine_9lev.png
sunshine_diff_12lev .. image:: images/colour_scales/sunshine_diff_12lev.png
temp_19lev          .. image:: images/colour_scales/temp_19lev.png
temp_diff_18lev     .. image:: images/colour_scales/temp_diff_18lev.png
temp_diff_1lev      .. image:: images/colour_scales/temp_diff_1lev.png
topo_15lev          .. image:: images/colour_scales/topo_15lev.png
wgne15              .. image:: images/colour_scales/wgne15.png
wind_17lev          .. image:: images/colour_scales/wind_17lev.png
=================== =====


NCAR Command Language - large colour maps (>50 colours)
-------------------------------------------------------

======================= =====
Name                    Scale
======================= =====
amwg256                 .. image:: images/colour_scales/amwg256.png
BkBlAqGrYeOrReViWh200   .. image:: images/colour_scales/BkBlAqGrYeOrReViWh200.png
BlAqGrYeOrRe            .. image:: images/colour_scales/BlAqGrYeOrRe.png
BlAqGrYeOrReVi200       .. image:: images/colour_scales/BlAqGrYeOrReVi200.png
BlGrYeOrReVi200         .. image:: images/colour_scales/BlGrYeOrReVi200.png
BlRe                    .. image:: images/colour_scales/BlRe.png
BlueRed                 .. image:: images/colour_scales/BlueRed.png
BlueRedGray             .. image:: images/colour_scales/BlueRedGray.png
BlueWhiteOrangeRed      .. image:: images/colour_scales/BlueWhiteOrangeRed.png
BlueYellowRed           .. image:: images/colour_scales/BlueYellowRed.png
BlWhRe                  .. image:: images/colour_scales/BlWhRe.png
cmp_b2r                 .. image:: images/colour_scales/cmp_b2r.png
cmp_haxby               .. image:: images/colour_scales/cmp_haxby.png
detail                  .. image:: images/colour_scales/detail.png
extrema                 .. image:: images/colour_scales/extrema.png
GrayWhiteGray           .. image:: images/colour_scales/GrayWhiteGray.png
GreenYellow             .. image:: images/colour_scales/GreenYellow.png
helix                   .. image:: images/colour_scales/helix.png
helix1                  .. image:: images/colour_scales/helix1.png
hotres                  .. image:: images/colour_scales/hotres.png
matlab_hot              .. image:: images/colour_scales/matlab_hot.png
matlab_hsv              .. image:: images/colour_scales/matlab_hsv.png
matlab_jet              .. image:: images/colour_scales/matlab_jet.png
matlab_lines            .. image:: images/colour_scales/matlab_lines.png
ncl_default             .. image:: images/colour_scales/ncl_default.png
ncview_default          .. image:: images/colour_scales/ncview_default.png
OceanLakeLandSnow       .. image:: images/colour_scales/OceanLakeLandSnow.png
rainbow                 .. image:: images/colour_scales/rainbow.png
rainbow_white_gray      .. image:: images/colour_scales/rainbow_white_gray.png
rainbow_white           .. image:: images/colour_scales/rainbow_white.png
rainbow_gray            .. image:: images/colour_scales/rainbow_gray.png
tbr_240_300             .. image:: images/colour_scales/tbr_240_300.png
tbr_stdev_0_30          .. image:: images/colour_scales/tbr_stdev_0_30.png
tbr_var_0_500           .. image:: images/colour_scales/tbr_var_0_500.png
tbrAvg1                 .. image:: images/colour_scales/tbrAvg1.png
tbrStd1                 .. image:: images/colour_scales/tbrStd1.png
tbrVar1                 .. image:: images/colour_scales/tbrVar1.png
thelix                  .. image:: images/colour_scales/thelix.png
ViBlGrWhYeOrRe          .. image:: images/colour_scales/ViBlGrWhYeOrRe.png
wh_bl_gr_ye_re          .. image:: images/colour_scales/wh_bl_gr_ye_re.png
WhBlGrYeRe              .. image:: images/colour_scales/WhBlGrYeRe.png
WhBlReWh                .. image:: images/colour_scales/WhBlReWh.png
WhiteBlue               .. image:: images/colour_scales/WhiteBlue.png
WhiteBlueGreenYellowRed .. image:: images/colour_scales/WhiteBlueGreenYellowRed.png
WhiteGreen              .. image:: images/colour_scales/WhiteGreen.png
WhiteYellowOrangeRed    .. image:: images/colour_scales/WhiteYellowOrangeRed.png
WhViBlGrYeOrRe          .. image:: images/colour_scales/WhViBlGrYeOrRe.png
WhViBlGrYeOrReWh        .. image:: images/colour_scales/WhViBlGrYeOrReWh.png
wxpEnIR                 .. image:: images/colour_scales/wxpEnIR.png
3gauss                  .. image:: images/colour_scales/3gauss.png
3saw                    .. image:: images/colour_scales/3saw.png
BrBG                    .. image:: images/colour_scales/BrBG.png
======================= =====


NCAR Command Language - Enhanced to help with colour blindness
--------------------------------------------------------------

================ =====
Name             Scale
================ =====
StepSeq25        .. image:: images/colour_scales/StepSeq25.png
posneg_2         .. image:: images/colour_scales/posneg_2.png
posneg_1         .. image:: images/colour_scales/posneg_1.png
BlueDarkOrange18 .. image:: images/colour_scales/BlueDarkOrange18.png
BlueDarkRed18    .. image:: images/colour_scales/BlueDarkRed18.png
GreenMagenta16   .. image:: images/colour_scales/GreenMagenta16.png
BlueGreen14      .. image:: images/colour_scales/BlueGreen14.png
BrownBlue12      .. image:: images/colour_scales/BrownBlue12.png
Cat12            .. image:: images/colour_scales/Cat12.png
================ =====


Orography/bathymetry colour scales
----------------------------------

================ =====
Name             Scale
================ =====
os250kmetres        .. image:: images/colour_scales/os250kmetres.png
wiki_1_0_2          .. image:: images/colour_scales/wiki_1_0_2.png
wiki_1_0_3          .. image:: images/colour_scales/wiki_1_0_3.png
wiki_2_0            .. image:: images/colour_scales/wiki_2_0.png
wiki_2_0_reduced    .. image:: images/colour_scales/wiki_2_0_reduced.png
arctic              .. image:: images/colour_scales/arctic.png
================ =====



IDL guide scales
----------------

======= =====
Name    Scale
======= =====
scale1  .. image:: images/colour_scales/scale1.png
scale2  .. image:: images/colour_scales/scale2.png
scale3  .. image:: images/colour_scales/scale3.png
scale4  .. image:: images/colour_scales/scale4.png
scale5  .. image:: images/colour_scales/scale5.png
scale6  .. image:: images/colour_scales/scale6.png
scale7  .. image:: images/colour_scales/scale7.png
scale8  .. image:: images/colour_scales/scale8.png
scale9  .. image:: images/colour_scales/scale9.png
scale10 .. image:: images/colour_scales/scale10.png
scale11 .. image:: images/colour_scales/scale11.png
scale12 .. image:: images/colour_scales/scale12.png
scale13 .. image:: images/colour_scales/scale13.png
scale14 .. image:: images/colour_scales/scale14.png
scale15 .. image:: images/colour_scales/scale15.png
scale16 .. image:: images/colour_scales/scale16.png
scale17 .. image:: images/colour_scales/scale17.png
scale18 .. image:: images/colour_scales/scale18.png
scale19 .. image:: images/colour_scales/scale19.png
scale20 .. image:: images/colour_scales/scale20.png
scale21 .. image:: images/colour_scales/scale21.png
scale22 .. image:: images/colour_scales/scale22.png
scale23 .. image:: images/colour_scales/scale23.png
scale24 .. image:: images/colour_scales/scale24.png
scale25 .. image:: images/colour_scales/scale25.png
scale26 .. image:: images/colour_scales/scale26.png
scale27 .. image:: images/colour_scales/scale27.png
scale28 .. image:: images/colour_scales/scale28.png
scale29 .. image:: images/colour_scales/scale29.png
scale30 .. image:: images/colour_scales/scale30.png
scale31 .. image:: images/colour_scales/scale31.png
scale32 .. image:: images/colour_scales/scale32.png
scale33 .. image:: images/colour_scales/scale33.png
scale34 .. image:: images/colour_scales/scale34.png
scale35 .. image:: images/colour_scales/scale35.png
scale36 .. image:: images/colour_scales/scale36.png
scale37 .. image:: images/colour_scales/scale37.png
scale38 .. image:: images/colour_scales/scale38.png
scale39 .. image:: images/colour_scales/scale39.png
scale40 .. image:: images/colour_scales/scale40.png
scale41 .. image:: images/colour_scales/scale41.png
scale42 .. image:: images/colour_scales/scale42.png
scale43 .. image:: images/colour_scales/scale43.png
scale44 .. image:: images/colour_scales/scale44.png
======= =====






