.. _example39b:

Example 39b: plotting a single (1D) DSG trajectory
--------------------------------------------------


.. code-block:: python
   :caption: Plotting data for a single trajectory encoded as a
             discrete sampling geometry in the form of a
             one-dimensional array, as
             `standard <https://cfconventions.org/cf-conventions/cf-conventions.html#_single_trajectory>`_)

   f = cf.read(f"cfplot_data/dsg_trajectory.nc")[0]

   cfp.traj(f)


.. figure:: /../../tests/reference-example-images/ref_fig_39b.png
