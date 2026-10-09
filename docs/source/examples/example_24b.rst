.. _example24b:

Example 24b: UGRID plot in the polar stereographic projection view
------------------------------------------------------------------


.. code-block:: python
   :caption: *TODO describe Example 24b*

   f = cf.read("cfplot_data/lfric_initial.nc")

   # Select the relevant fields for the objects required for the plot,
   # taking the air potential temperature as a variable to choose to view.
   pot = f.select_by_identity("air_potential_temperature")[0]
   lats = f.select_by_identity("latitude")[0]
   lons = f.select_by_identity("longitude")[0]
   faces = f.select_by_identity("cf_role=face_edge_connectivity")[0]

   # Reduce the variable to match the shapes
   pot = pot[4,:]

   cfp.levs(240, 310, 5)

   # This time set the projection to a polar one for a different view
   cfp.mapset(proj="npstere")
   cfp.con(
       f=pot, face_lons=lons,
       face_lats=lats, face_connectivity=faces, lines=False,
       blockfill=True,
   )


.. figure:: /../../tests/reference-example-images/ref_fig_24b.png
