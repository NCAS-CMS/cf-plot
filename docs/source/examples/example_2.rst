.. _example2:

Example 2: Basic blockfill plot in default projection
-----------------------------------------------------


.. code-block:: python
   :caption: Making a basic blockfill plot which uses the default,
             Cylindrical, projection

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]

   cfp.con(f.subspace(time=15), blockfill=True, lines=False)


.. figure:: /../../tests/reference-example-images/ref_fig_2.png
