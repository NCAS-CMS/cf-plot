.. _example22:

Example 22: Plot of rotated pole data on its native grid
--------------------------------------------------------


.. code-block:: python
   :caption: Making a plot of data defined on a rotated pole coordinate
             system shown on its native grid

   f = cf.read(f"cfplot_data/rgp.nc")[0]

   cfp.cscale("plasma")
   cfp.mapset(proj="rotated")

   cfp.con(f)


.. figure:: /../../tests/reference-example-images/ref_fig_22.png
