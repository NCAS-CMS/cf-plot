.. _example35:

Example 35: Mollweide projection
--------------------------------


.. code-block:: python
   :caption: Plotting using the Mollweide projection

   f = cf.read("cfplot_data/tas_A1.nc")[0]

   cfp.mapset(proj="moll")
   cfp.con(
       f.subspace(time=15),
       linestyles="dashed",
       linewidths=0.75,
       title="Mollweide projection",
   )


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_35.png
