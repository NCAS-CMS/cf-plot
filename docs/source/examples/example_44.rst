.. _example_44:

Example 44: NEMO data on a curvilinear T grid
---------------------------------------------


.. code-block:: python
   :caption: Making a global and close-up contour plot of NEMO data
             defined on a curvilinear T grid, shown on a single figure

   fl = cf.read(f"cfplot_data/nemo_eg260916.nc")
   f = fl[0].squeeze()

   cfp.gopen(rows=2, columns=1, bottom=0.2)
   cfp.cscale("precip2_17lev")
   cfp.gpos(1)
   cfp.con(
       f, colorbar=None, lines=False,
       title=(
           "Total precipitation flux at midnight 1979-02-15 highlighted "
           "over the Tropical Indo-Pacific"
       ))
   cfp.gpos(2)
   cfp.con(
       f.subspace(
           X=cf.wi(120, 180), Y=cf.wi(-25, 5)),
       lines=False,
   )
   cfp.gclose()


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_nemo1.png
