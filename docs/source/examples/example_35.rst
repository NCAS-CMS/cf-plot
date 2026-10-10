.. _example35:

Example 35: Mollweide projection
--------------------------------


.. code-block:: python
   :caption: Plotting using the Mollweide projection

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]

   cfp.mapset(proj="moll")

   cfp.con(f.subspace(time=15))


.. figure:: /../../tests/reference-example-images/ref_fig_35.png
