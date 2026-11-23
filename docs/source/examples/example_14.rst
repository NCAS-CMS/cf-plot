.. _example14:

Example 14: Vector plot overlaid on a contour map
-------------------------------------------------


.. code-block:: python
   :caption: Overlaying a vector plot on a contoured temperature field

   f = cf.read("cfplot_data/ggap.nc")

   u = ggap_file["eastward_wind"]
   v = ggap_file["northward_wind"]
   t = ggap_file["air_temperature"]

   # Subspace to get values for a specified pressure, here 700 mbar
   u = u.subspace(pressure=700)
   v = v.subspace(pressure=700)
   t = t.subspace(pressure=700)

   cfp.setvars(
       land_color="darkgreen",
       feature_zorder=2,
   )

   cfp.gopen()
   cfp.mapset(lonmin=10, lonmax=120, latmin=-30, latmax=30)
   cfp.levs(min=270, max=290, step=1)
   cfp.con(t, lines=False)
   cfp.vect(u=u, v=v, key_length=10, scale=40, stride=2, color="cyan")
   cfp.gclose()


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_14.png
