.. _example19a:

Example 19d: Multiple plots using `gfigure` context manager
-----------------------------------------------------------


.. code-block:: python
   :caption: Making a single figure with multiple plots on it
             using the context manager `gfigure` instead of
             via wrapping with `gopen` and `gclose`

   fl = cf.read("cfplot_data/ggap.nc")
   f = fl.select_by_identity("eastward_wind")[0]
   f_500 = f.subspace(pressure=500)

   with cfp.gfigure(rows=2, columns=2, bottom=0.2):
       proj_list = ["cyl", "moll", "npstere", "spstere"]
       for index, proj_name in enumerate(proj_list):
           cfp.gpos(index + 1)  # gpos(1), gpos(2), etc. to position each
           cfp.mapset(proj=proj_name)

           if index < len(proj_list) - 1:  # all but last plot
               cfp.con(f_500, lines=False, colorbar=None)
           else:
               cfp.con(
                   f_500,
                   lines=False,
                   colorbar_position=[0.1, 0.1, 0.8, 0.02],
                   colorbar_orientation="horizontal",
               )


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_19d.png
