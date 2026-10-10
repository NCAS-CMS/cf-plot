.. _example14:

Example 14: Vector plot overlaid on a contour map
-------------------------------------------------


.. code-block:: python
   :caption: Overlaying a vector plot on a contoured temperature field

   f = cf.read(f"cfplot_data/ggap.nc")

   u = f.select_by_identity("eastward_wind")[0]
   v = f.select_by_identity("northward_wind")[0]
   t = f.select_by_identity("air_temperature")[0]

   # Subspace to get values for a specified pressure, here 500 mbar
   u = u.subspace(pressure=500)
   v = v.subspace(pressure=500)
   t = t.subspace(pressure=500)

   cfp.gopen()
   cfp.mapset(lonmin=10, lonmax=120, latmin=-30, latmax=30)
   cfp.levs(min=254, max=270, step=1)
   cfp.con(t)
   cfp.vect(u=u, v=v, key_length=10, scale=50, stride=2)
   cfp.gclose()


.. figure:: /../../tests/reference-example-images/ref_fig_14.png
