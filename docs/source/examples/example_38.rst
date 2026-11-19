.. _example38:

Example 38: Robinson projection
-------------------------------


.. code-block:: python
   :caption: Plotting using the Robinson projection

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]

   cfp.mapset(proj="robin")
   cfp.con(
       f.subspace(time=15),
       linestyles="dashed",
       linewidths=0.75,
       title="Robinson projection",
   )


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_38.png
