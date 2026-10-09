.. _example36:

Example 36: Mercator projection
-------------------------------


.. code-block:: python
   :caption: Plotting using the Mercator projection

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]

   cfp.mapset(proj="merc")

   cfp.con(f.subspace(time=15))


.. figure:: /../../tests/reference-example-images/ref_fig_36.png
