.. _example41:

Example 41: Feature propagation over Europe
-------------------------------------------


.. code-block:: python
   :caption: Plotting the propagation of features over Europe

   f = cf.read("cfplot_data/ff_trs_pos.nc")[0]

   cfp.mapset(lonmin=-20, lonmax=20, latmin=35, latmax=60, resolution="50m")
   cfp.traj(
        f,
        vector=True,
        markersize=0,
        ec="darkslateblue",  # helps to distinguish track from land lines
        fc="darkslateblue",
    )


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_41.png
