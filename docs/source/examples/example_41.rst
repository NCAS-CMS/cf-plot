.. _example41:

Example 41: Feature propagation over Europe
-------------------------------------------


.. code-block:: python
   :caption: Plotting the propagation of features over Europe

   f = cf.read(f"cfplot_data/ff_trs_pos.nc")[0]

   cfp.mapset(lonmin=-20, lonmax=20, latmin=30, latmax=70)

   cfp.traj(f, vector=True, markersize=0.0, fc="b", ec="b")


.. figure:: /../../tests/reference-example-images/ref_fig_41.png
