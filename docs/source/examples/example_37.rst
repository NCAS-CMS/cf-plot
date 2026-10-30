.. _example37:

Example 37: Orthographic projection
-----------------------------------


.. code-block:: python
   :caption: Plotting using the Orthographic projection

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]

   cfp.mapset(proj="ortho")

   cfp.con(f.subspace(time=15))


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_37.png
