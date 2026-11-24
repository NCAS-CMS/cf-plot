.. _example39b:

Example 39b: plotting a single (1D) DSG trajectory
--------------------------------------------------


.. code-block:: python
   :caption: Plotting data for a single trajectory encoded as a
             discrete sampling geometry in the form of a
             one-dimensional array, as
             `standard <https://cfconventions.org/cf-conventions/cf-conventions.html#_single_trajectory>`_)

   f = cf.read("cfplot_data/dsg_trajectory.nc")[0]

   cfp.setvars(
       land_color="darkseagreen",
       ocean_color="lightsteelblue",
       feature_zorder=0,
   )

   # Ends over a small part of the Netherlands so focus in on that area
   cfp.mapset(lonmin=4.5, lonmax=5.0, latmin=52.6, latmax=53.3, resolution="10m")

   cfp.traj(
       f,
       marker="D",
       markeredgecolor="maroon",
       linecolor="maroon",
       # np.round avoids floating point rounding values, e.g. .99999... -> 1.0
       xticks=np.round(np.arange(4.5, 5.05, 0.05), 2),
       yticks=np.round(np.arange(52.6, 53.35, 0.05), 2),
   )


.. figure:: /../../tests/v350-controlled-env-ref-images/ref_fig_39b.png
