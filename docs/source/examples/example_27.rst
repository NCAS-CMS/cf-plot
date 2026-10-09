.. _example27:

Example 27: Basic line plot
---------------------------


.. code-block:: python
   :caption: Making a basic line plot

   fl = cf.read(f"{self.data_dir}/ggap.nc")
   f = fl.select_by_identity("eastward_wind")[0]

   g = f.collapse("X: mean")

   cfp.gopen()
   cfp.lineplot(
       g.subspace(pressure=100),
       marker="o",
       color="blue",
       title="Zonal mean zonal wind at 100mb",
   )
   cfp.gclose()


.. figure:: /../../tests/reference-example-images/ref_fig_27.png
