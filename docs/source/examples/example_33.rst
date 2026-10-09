.. _example33:

Example 33: OSGB and EuroPP projections
---------------------------------------


.. code-block:: python
   :caption: Plotting using the projections OSGB and EuroPP

   f = cf.read(f"cfplot_data/ukcp_rcm_test.nc")[0]

   cfp.levs(-3, 7, 0.5)

   cfp.gopen(columns=2)
   cfp.mapset(proj="OSGB", resolution="50m")
   cfp.con(f, lines=False, colorbar_label_skip=2)
   cfp.gpos(2)
   cfp.mapset(proj="EuroPP", resolution="50m")
   cfp.con(f, lines=False, colorbar_label_skip=2)
   cfp.gclose()


.. figure:: /../../tests/reference-example-images/ref_fig_33.png
