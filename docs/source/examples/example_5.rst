.. _example5:

Example 5: South Pole polar projection contour plot with bounding latitude
--------------------------------------------------------------------------


.. code-block:: python
   :caption: Changing the view area of a contour plot in the South Pole
             polar stereographic projection by setting the latitude limit to
             30 degrees south

   fl = cf.read("cfplot_data/ggap.nc")
   f = fl.select_by_identity("northward_wind")[0]
   
   cfp.mapset(proj="spstere", boundinglat=-30, lon_0=180)

   cfp.con(
       f.subspace(pressure=1000),
       linewidths=0.75,
       colors="slategrey",
       line_labels=False,  # else it gets a bit busy with these contours
   )


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_5.png
