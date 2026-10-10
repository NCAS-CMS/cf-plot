.. _example42b:

Example 42b: Tracks displayed in a colour scale
-----------------------------------------------


.. code-block:: python
   :caption: Plotting tracks where the trajectory is shown in
             colours mapped to a colour scale corresponding to
             the value of the underlying data by setting the
             `legend_lines` keyword to `True`

   f = cf.read(f"cfplot_data/ff_trs_pos.nc")[0]

   cfp.mapset(lonmin=-50, lonmax=50, latmin=20, latmax=80)
   g = f.subspace(time=cf.wi(cf.dt("1979-12-01"), cf.dt("1979-12-10")))
   g = g * 1e5
   cfp.levs(0, 12, 1, extend="max")
   cfp.cscale("scale1", below=0, above=13)
   cfp.traj(
       g,
       legend_lines=True,
       linewidth=2,
       colorbar_title="Relative Vorticity (Hz) * 1e5",
   )


.. figure:: /../../tests/reference-example-images/ref_fig_42b.png
