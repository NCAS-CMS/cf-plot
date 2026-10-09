.. _example32:

Example 32: UKCP projection with blockfill
------------------------------------------


.. code-block:: python
   :caption: Plotting a blockfill plot using the UKCP projection

   f = cf.read(f"cfplot_data/ukcp_rcm_test.nc")[0]

   cfp.mapset(proj="UKCP", resolution="50m")
   cfp.levs(-3, 7, 0.5)
   cfp.setvars(grid_colour="grey")

   cfp.con(
       f,
       lines=False,
       blockfill=True,
       # Centered over UK region with spacing of 1 each
       xticks=np.arange(14) - 11,
       yticks=np.arange(13) + 49,
   )


.. figure:: /../../tests/reference-example-images/ref_fig_32.png
