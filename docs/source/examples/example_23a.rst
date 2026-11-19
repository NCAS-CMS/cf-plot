.. _example23a:

Example 23a: Rotated pole plot from data which is not CF Compliant
------------------------------------------------------------------


.. code-block:: python
   :caption: Constructing a rotated pole plot from data which is not
             very CF Compliant, noting that this takes more set up
             than for CF Compliant data (see Example 21b)

   f = cf.read(f"cfplot_data/rgp.nc")[0]

   data = f.array
   xvec = f.construct("ncvar%x")
   yvec = f.construct("ncvar%y")

   _configure_example_output("23")

   cfp.gopen()

   # Set up the data
   xpts = np.arange(np.size(xvec))
   ypts = np.arange(np.size(yvec))
   cfp.gset(xmin=0, xmax=np.size(xvec) - 1, ymin=0, ymax=np.size(yvec) - 1)

   # Configure the plot
   cfp.cscale("plasma")
   cfp.levs(min=680, max=1020, step=20)
   cfp.con(
       data, xpts, ypts[::-1],
       linewidths=0.5,
       linestyle="dashed",
   )

   # Add the rotated pole axes grid and labels separately
   xpole = 160
   ypole = 30
   cfp.rgaxes(xpole=xpole, ypole=ypole, xvec=xvec, yvec=yvec)

   cfp.gclose()


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_23.png
