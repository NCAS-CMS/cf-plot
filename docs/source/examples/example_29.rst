.. _example29:

Example 29: Time series line plot
---------------------------------


.. code-block:: python
   :caption: Making a basic line plot for a time series where the
             data shown is global average annual temperature

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]

   temp = f.subspace(time=cf.wi(cf.dt("1900-01-01"), cf.dt("1980-01-01")))
   temp_annual = temp.collapse("T: mean", group=cf.Y())
   temp_annual_global = temp_annual.collapse("area: mean", weights="area")
   temp_annual_global.Units -= 273.15

   cfp.lineplot(
       temp_annual_global,
       title="Global average annual temperature",
       color="blue",
   )


.. figure:: /../../tests/reference-example-images/ref_fig_29.png
