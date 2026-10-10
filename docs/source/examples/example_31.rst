.. _example31:

Example 31: UKCP projection
---------------------------


.. code-block:: python
   :caption: Plotting using the UKCP projection

   f = cf.read(f"cfplot_data/ukcp_rcm_test.nc")[0]

   cfp.mapset(proj="UKCP", resolution="50m")
   cfp.levs(-3, 7, 0.5)
   cfp.setvars(grid_x_spacing=1, grid_y_spacing=1)

   cfp.con(f, lines=False)

.. figure:: /../../tests/reference-example-images/ref_fig_31.png
