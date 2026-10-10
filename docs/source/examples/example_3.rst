.. _example3:

Example 3: Contour plot with altered map limits and levels
----------------------------------------------------------


.. code-block:: python
   :caption: Altering a contour plot to show different limits
             of latitude and longitude and to change the contour
             levels displayed

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]

   cfp.mapset(lonmin=-15, lonmax=3, latmin=48, latmax=60)
   cfp.levs(min=265, max=285, step=1)

   cfp.con(f.subspace(time=15))


.. figure:: /../../tests/reference-example-images/ref_fig_3.png
