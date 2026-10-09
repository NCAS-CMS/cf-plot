.. _example7:

Example 7: Latitude-pressure plot over zonal mean
-------------------------------------------------


.. code-block:: python
   :caption: Making a plot with latitude and pressure as the axes
             for a zonal mean (mean over longitude)

   fl = cf.read(f"{self.data_dir}/ggap.nc")
   f = fl.select_by_identity("eastward_wind")[0]

   cfp.con(f.collapse("mean", "longitude"))


.. figure:: /../../tests/reference-example-images/ref_fig_7.png
