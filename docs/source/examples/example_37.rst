.. _example37:

Example 37: Orthographic projection
-----------------------------------


.. code-block:: python
   :caption: Plotting using the Orthographic projection

   f = cf.read("cfplot_data/tas_A1.nc")[0]

   cfp.mapset(proj="ortho")
   cfp.con(
       f.subspace(time=15),
       linestyles="dashed",
       linewidths=0.75,
       title="Orthographic projection",
   )


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_37.png
