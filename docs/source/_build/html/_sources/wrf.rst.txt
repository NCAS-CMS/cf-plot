.. _wrf:
WRF data
********


Output data from the Weather Research and Forecasting (WRF) Model is some distance from being CF compliant.  A Python script is available, from the University of Cantabria, that converts WRF data into CF netCDF. The Python script can be downloaded from http://www.meteo.unican.es/wiki/cordexwrf/SoftwareTools/WrfncXnj

Our input file here is called wrf.nc.  As the file is large at 5GB this file isn't distributed and this is a worked example of what is needed. 

**python wrfncxnj.py -v T2 -o wrf2.nc wrf.nc**


We now have a CF netCDF file with the temperature at 2m which can be readily manipulated and plotted using cf-python and cf-plot.

|

Example 43 - plotting WRF data
------------------------------

.. image::  images/fig43.png
   :scale: 52% 

::

   import cf
   import cfplot as cfp
   f=cf.read('wrf2.nc')[0]
   t2=f.subspace(time=cf.dt('2016-12-25'))
   t2.units='degC'
   cfp.con(t2, lines=False)


| 
| 



