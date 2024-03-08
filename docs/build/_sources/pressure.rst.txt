.. _pressure:
Latitude / longitude - pressure
*******************************


Example 6 - latitude - pressure
-------------------------------

.. image::  images/fig6.png
   :scale: 44% 

::

   import cf
   import cfplot as cfp
   f=cf.read('cfplot_data/ggap.nc')[2]
   cfp.con(f.subspace(longitude=0))

| 
| 
|
| 


Example 7 - latitude - pressure - zonal mean
--------------------------------------------

.. image::  images/fig7.png
   :scale: 44% 

::

   import cf
   import cfplot as cfp
   f=cf.read('cfplot_data/ggap.nc')[1]
   cfp.con(f.collapse('mean','longitude'))

| 
| 
|
| 




Example 8 - latitude - log pressure
-----------------------------------



.. image::  images/fig8.png
   :scale: 44% 


::

   import cf
   import cfplot as cfp
   f=cf.read('cfplot_data/ggap.nc')[1]
   cfp.con(f.collapse('mean','longitude'), ylog=True)



Example 9 - longitude - pressure
--------------------------------



.. image::  images/fig9.png
   :scale: 44% 


::

   import cf
   import cfplot as cfp
   f=cf.read('cfplot_data/ggap.nc')[0]
   cfp.con(f.collapse('mean', 'latitude'))





