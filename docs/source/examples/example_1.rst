.. _example1:

Example 1: Basic contour plot in default projection
---------------------------------------------------


.. code-block:: python
   :caption: Making a basic default contour plot which uses the default
             projection, Cylindrical, and has contour lines explicitly
             filled and shown with value labels

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]

   cfp.con(f.subspace(time=15))


.. figure:: /../../tests/reference-example-images/ref_fig_1.png
