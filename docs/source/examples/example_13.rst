.. _example13:

Example 13: Basic vector plot
-----------------------------


.. code-block:: python
   :caption: Making a basic vector plot

   f = cf.read(f"cfplot_data/ggap.nc")

   u = f.select_by_identity("eastward_wind")[0]
   v = f.select_by_identity("northward_wind")[0]

   # Subspace to get values for a specified pressure, here 500 mbar
   u = u.subspace(pressure=500)
   v = v.subspace(pressure=500)

   cfp.vect(u=u, v=v, key_length=10, scale=100, stride=5)

.. figure:: /../../tests/reference-example-images/ref_fig_13.png
