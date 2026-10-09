.. _example23a:

Example 23a: Rotated pole plot from data which is not CF Compliant
------------------------------------------------------------------


.. code-block:: python
   :caption: Constructing a rotated pole plot from data which is not
             very CF Compliant, noting that this takes more set up
             than for CF Compliant data (see Example 21b)

   f = cf.read(f"cfplot_data/rgp.nc")[0]

   data = f.array
   xvec = f.construct("ncvar%x").array
   yvec = f.construct("ncvar%y").array
   xpole = 160
   ypole = 30

   cfp.gopen()
   cfp.cscale("plasma")
   xpts = np.arange(np.size(xvec))
   ypts = np.arange(np.size(yvec))
   cfp.gset(
       xmin=0, xmax=np.size(xvec) - 1, ymin=0, ymax=np.size(yvec) - 1
   )
   cfp.levs(min=980, max=1035, step=2.5)
   cfp.con(data, xpts, ypts[::-1])
   cfp.rgaxes(xpole=xpole, ypole=ypole, xvec=xvec, yvec=yvec)
   cfp.gclose()


.. figure:: /../../tests/reference-example-images/ref_fig_23a.png
