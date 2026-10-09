.. _example8:

Example 8: Latitude against log of pressure over longitude zonal mean
---------------------------------------------------------------------


.. code-block:: python
   :caption: Making a semilog plot with latitude and the log of the
             pressure as the axes for a zonal mean over longitude

   fl = cf.read(f"{self.data_dir}/ggap.nc")
   f = fl.select_by_identity("eastward_wind")[0]

   cfp.con(f.collapse("mean", "longitude"), ylog=1)


.. figure:: /../../tests/reference-example-images/ref_fig_8.png
