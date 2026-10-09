.. _example16b:

Example 16b: Basic stream plot
------------------------------


.. code-block:: python
   :caption: Making a basic stream plot

   f = cf.read(f"cfplot_data/ggap.nc")

   u = f.select_by_identity("eastward_wind")[0]
   v = f.select_by_identity("northward_wind")[0]

   u = u.subspace(pressure=500)
   v = v.subspace(pressure=500)

   u = u.anchor("X", -180)
   v = v.anchor("X", -180)

   cfp.stream(u=u, v=v, density=2)


.. figure:: /../../tests/reference-example-images/ref_fig_16b.png
