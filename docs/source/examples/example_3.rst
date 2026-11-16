.. _example3:

Example 3: Contour plot with altered map limits and levels
----------------------------------------------------------


.. code-block:: python
   :caption: Altering a contour plot to show different limits
             of latitude and longitude and to change the contour
             levels displayed

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]

   cfp.mapset(lonmin=-90, lonmax=-30, latmin=-60, latmax=20, resolution="10m")
   cfp.levs(min=280, max=300, step=2)

   cfp.con(f.subspace(time=15), linestyles="dotted")


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_3.png
