.. _example19a:

Example 19d: Multiple plots using `gfigure` context manager
-----------------------------------------------------------


.. code-block:: python
   :caption: Making a single figure with multiple plots on it
             using the context manager `gfigure` instead of
             via wrapping with `gopen` and `gclose`

   fl = cf.read(f"{self.data_dir}/ggap.nc")
   f = fl.select_by_identity("eastward_wind")[0]

   with cfp.gfigure(rows=2, columns=2, bottom=0.2):
       cfp.gpos(1)
       cfp.con(f.subspace(pressure=500), colorbar=None)
       cfp.gpos(2)
       cfp.mapset(proj="moll")
       cfp.con(f.subspace(pressure=500), colorbar=None)
       cfp.gpos(3)
       cfp.mapset(proj="npstere", boundinglat=30, lon_0=180)
       cfp.con(f.subspace(pressure=500), colorbar=None)
       cfp.gpos(4)
       cfp.mapset(proj="spstere", boundinglat=-30, lon_0=180)
       cfp.con(
           f.subspace(pressure=500),
           colorbar_position=[0.1, 0.1, 0.8, 0.02],
           colorbar_orientation="horizontal",
       )


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_19d.png
