.. _example23b:

Example 23b: Overlaying vectors over a rotated pole data plot
-------------------------------------------------------------


.. code-block:: python
   :caption: *TODO describe Example 23 Other*

   f = cf.read(
       f"cfplot_data/20160601-05T0000Z_INCOMPASS_km4p4_uv_RH_500.nc"
   )
   r = fl.select_by_identity("long_name=Relative humidity")[0]
   u = fl.select_by_identity("eastward_wind")[0]
   v = fl.select_by_identity("northward_wind")[0]

   cfp.mapset(50, 100, 5, 35)
   cfp.levs(0, 90, 15, extend="neither")

   cfp.gopen()
   cfp.con(r, lines=False)
   cfp.vect(u=u, v=v, stride=40, key_length=10)
   cfp.gclose()


.. figure:: /../../tests/reference-example-images/ref_fig_23b.png
