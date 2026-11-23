.. _example28:

Example 28: Line plot with a legend
-----------------------------------


.. code-block:: python
   :caption: Adding a legend to annotate a line plot with multiple
             plotted lines

   fl = cf.read("cfplot_data/ggap.nc")
   f = fl.select_by_identity("eastward_wind")[0]

   g = f.collapse("X: mean")

   xticks = [-90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90]
   xticklabels = [
       "90S",
       "75S",
       "60S",
       "45S",
       "30S",
       "15S",
       "0",
       "15N",
       "30N",
       "45N",
       "60N",
       "75N",
       "90N",
   ]
   xpts = [-30, 30, 30, -30, -30]
   ypts = [-8, -8, 5, 5, -8]

   cfp.gset(xmin=-90, xmax=90, ymin=-10, ymax=50)
   cfp.gopen()

   cfp.lineplot(
       g.subspace(pressure=100),
       marker="o",
       color="slateblue",
       title="Zonal mean zonal wind",
       label="100 mb",
   )
   cfp.lineplot(
       g.subspace(pressure=200),
       marker="D",
       color="indianred",
       label="200 mb",
       xticks=xticks,
       xticklabels=xticklabels,
       legend_location="upper right",
   )

   cfp.plotvars.plot.plot(xpts, ypts, linewidth=3.0, color="mediumseagreen")
   cfp.plotvars.plot.text(
       2, -7, "Region of interest", horizontalalignment="left"
   )

   cfp.gclose()


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_28.png
