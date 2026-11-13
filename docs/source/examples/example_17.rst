.. _example17:

Example 17: Basic stipple plot
------------------------------


.. code-block:: python
   :caption: A stipple plot, whereby stippling is applied to a contour
             plot to indicate areas of statistical significance.

   f = cf.read(f"cfplot_data/tas_A1.nc")[0]
   g = f[-1]  # last time value subspace

   # Calculate spatial mean and standard deviation
   mean = g.mean().datum()
   std = g.sd().datum()
   upper = mean + std
   lower = mean - std
   minim = g.min().datum()
   maxim = g.max().datum()

   cfp.gopen()
   cfp.cscale("magma")
   cfp.con(g, lines=False)

   # Stipple regions over one standard deviation below or above spatial mean
   cfp.stipple(
       f=g,
       min=minim,
       max=lower,
       size=12,
       marker="v",
       color="#ffffff",
       edgecolors="#ffffff",
   )
   cfp.stipple(
       f=g,
       min=upper,
       max=maxim,
       size=12,
       marker="^",
       color="#1f4e79",
       edgecolors="#1f4e79",
   )
   cfp.gclose()


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_17.png
