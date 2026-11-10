.. _example27b:

Example 27b: Basic scatter plot
-------------------------------


.. code-block:: python
   :caption: Making a basic scatter plot

   fl = cf.read(f"{self.data_dir}/ggap.nc")
   f = fl.select_by_identity("eastward_wind")[0]

   g = f.collapse("Y: minimum")

   _configure_example_output("27b")
   cfp.scatter(
       g.subspace(pressure=700),
       title="Meridional minimum of zonal wind at 700mb",
   )


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_27b.png
